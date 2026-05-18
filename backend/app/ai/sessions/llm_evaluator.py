"""LLM-driven `Evaluator` implementation for the sessions flow.

Uses `ILLMClient.generate_structured` to coerce the model output into a
Pydantic schema. On any LLM failure, falls back to a conservative
mid-range score (5.0) so the session lifecycle keeps moving rather than
crashing — the evaluator notes record the failure cause for debugging.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field

from app.ai.llm.exceptions import LLMError
from app.ai.llm.interface import ILLMClient
from app.ai.sessions.prompts import build_eval_user_prompt, eval_system_prompt
from app.modules.sessions.evaluator import EvaluationResult
from app.scoring import ArchetypeSpec


logger = logging.getLogger(__name__)


class EvaluationOutput(BaseModel):
    """LLM-side schema enforced via structured output."""

    raw_score: float = Field(ge=0.0, le=10.0)
    rubric_scores: dict[str, float] = Field(default_factory=dict)
    evaluator_notes: str = ""


class LLMEvaluator:
    """Production `Evaluator` — invokes the LLM, validates output, returns
    `EvaluationResult`."""

    def __init__(self, llm: ILLMClient, *, temperature: float | None = 0.2) -> None:
        self.llm = llm
        self.temperature = temperature

    async def evaluate(
        self,
        *,
        archetype: ArchetypeSpec,
        task_content: dict,
        user_response: dict | None,
    ) -> EvaluationResult:
        if user_response is None:
            return EvaluationResult(
                raw_score=0.0,
                rubric_scores={r: 0.0 for r in archetype.rubric},
                evaluator_notes="No response submitted.",
            )

        try:
            output = await self.llm.generate_structured(
                system_prompt=eval_system_prompt(),
                user_prompt=build_eval_user_prompt(
                    archetype=archetype,
                    task_content=task_content,
                    user_response=user_response,
                ),
                output_model=EvaluationOutput,
                temperature=self.temperature,
            )
        except LLMError as exc:
            logger.warning(
                "LLM evaluator failed for archetype=%s: %s",
                archetype.archetype_id, exc,
            )
            return EvaluationResult(
                raw_score=5.0,
                rubric_scores={r: 5.0 for r in archetype.rubric},
                evaluator_notes=f"Evaluator unavailable: {exc}",
            )

        # Defensive: keep only the rubric items the archetype declared.
        rubric_scores = {
            r: float(output.rubric_scores.get(r, output.raw_score))
            for r in archetype.rubric
        }
        return EvaluationResult(
            raw_score=float(output.raw_score),
            rubric_scores=rubric_scores,
            evaluator_notes=output.evaluator_notes or None,
        )
