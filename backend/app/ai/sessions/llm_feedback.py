"""LLM-driven `FeedbackGenerator` implementation for the sessions flow.

Produces the spec §14 shape: summary, did_well[], mistakes[], next_tip,
sub_skill_breakdown. On LLM failure, returns a minimal stub-flavour
feedback so the user still sees something — and the activity lifecycle
proceeds.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field

from app.ai.llm.exceptions import LLMError
from app.ai.llm.interface import ILLMClient
from app.ai.sessions.prompts import (
    build_feedback_user_prompt,
    feedback_system_prompt,
)
from app.modules.sessions.evaluator import EvaluationResult
from app.modules.sessions.feedback_generator import (
    FeedbackResult,
    MistakeOut,
)
from app.scoring import ArchetypeSpec


logger = logging.getLogger(__name__)


class MistakeOutSchema(BaseModel):
    issue: str
    user_wrote: str | None = None
    correction: str | None = None
    rule: str | None = None
    sub_skills_affected: list[str] = Field(default_factory=list)


class FeedbackOutput(BaseModel):
    """LLM-side schema enforced via structured output."""

    score: int = Field(ge=0, le=10)
    summary: str
    did_well: list[str] = Field(default_factory=list)
    mistakes: list[MistakeOutSchema] = Field(default_factory=list)
    next_tip: str | None = None
    sub_skill_breakdown: dict[str, int] = Field(default_factory=dict)


class LLMFeedbackGenerator:
    """Production `FeedbackGenerator` — invokes the LLM, validates output,
    returns `FeedbackResult`."""

    def __init__(self, llm: ILLMClient, *, temperature: float | None = 0.4) -> None:
        self.llm = llm
        self.temperature = temperature

    async def generate(
        self,
        *,
        archetype: ArchetypeSpec,
        evaluation: EvaluationResult,
        user_response: dict | None,
    ) -> FeedbackResult:
        rounded = int(round(evaluation.raw_score))
        if user_response is None:
            return FeedbackResult(
                score=0,
                summary=f"No response submitted for {archetype.name}.",
                did_well=(),
                mistakes=(),
                next_tip="Try submitting an answer next time, even a short one.",
                sub_skill_breakdown={skill: 0 for skill in archetype.weight_map},
            )

        try:
            output = await self.llm.generate_structured(
                system_prompt=feedback_system_prompt(),
                user_prompt=build_feedback_user_prompt(
                    archetype=archetype,
                    raw_score=evaluation.raw_score,
                    rubric_scores=evaluation.rubric_scores,
                    evaluator_notes=evaluation.evaluator_notes,
                    task_content={},  # caller passes empty since llm_evaluator already saw it
                    user_response=user_response,
                ),
                output_model=FeedbackOutput,
                temperature=self.temperature,
            )
        except LLMError as exc:
            logger.warning(
                "LLM feedback failed for archetype=%s: %s",
                archetype.archetype_id, exc,
            )
            return FeedbackResult(
                score=rounded,
                summary=(
                    f"Feedback temporarily unavailable. Score: {rounded}/10. "
                    "We'll generate detailed feedback once the service is back."
                ),
                did_well=(),
                mistakes=(),
                next_tip=None,
                sub_skill_breakdown={skill: rounded for skill in archetype.weight_map},
            )

        # Keep only sub-skills the archetype declared — defensive.
        breakdown = {
            skill: int(output.sub_skill_breakdown.get(skill, rounded))
            for skill in archetype.weight_map
        }
        # Cap mistakes per spec rule ("max 3 per activity"). Defensive in
        # case the LLM ignores the instruction.
        mistakes_capped = tuple(
            MistakeOut(
                issue=m.issue,
                user_wrote=m.user_wrote,
                correction=m.correction,
                rule=m.rule,
                sub_skills_affected=tuple(m.sub_skills_affected),
            )
            for m in output.mistakes[:3]
        )
        return FeedbackResult(
            score=int(output.score),
            summary=output.summary,
            did_well=tuple(output.did_well),
            mistakes=mistakes_capped,
            next_tip=output.next_tip,
            sub_skill_breakdown=breakdown,
        )
