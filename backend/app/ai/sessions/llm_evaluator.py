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
from app.ai.sessions.prompts import (
    build_eval_user_prompt,
    build_speak_eval_user_prompt,
    eval_system_prompt,
)
from app.ai.sessions.speaking_eval import (
    build_speaking_eval_items,
    has_any_transcript,
)
from app.modules.sessions.evaluator import EvaluationResult
from app.scoring import ArchetypeSpec


logger = logging.getLogger(__name__)


class EvaluationOutput(BaseModel):
    """LLM-side schema enforced via structured output."""

    raw_score: float = Field(ge=0.0, le=10.0)
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
        evaluator_overrides: dict | None = None,
    ) -> EvaluationResult:
        if user_response is None:
            return EvaluationResult(
                raw_score=0.0,
                rubric_scores={r: 0.0 for r in archetype.rubric},
                evaluator_notes="No response submitted.",
            )

        if archetype.archetype_id == "LISTEN_MCQ":
            return self._evaluate_listen_mcq(
                archetype=archetype,
                task_content=task_content,
                user_response=user_response,
            )

        if archetype.ui_widget == "SpeakAndRecord":
            return await self._evaluate_speak_and_record(
                archetype=archetype,
                task_content=task_content,
                user_response=user_response,
                evaluator_overrides=evaluator_overrides,
            )

        try:
            output = await self.llm.generate_structured(
                system_prompt=eval_system_prompt(),
                user_prompt=build_eval_user_prompt(
                    archetype=archetype,
                    task_content=task_content,
                    user_response=user_response,
                    evaluator_overrides=evaluator_overrides,
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

        rubric_scores = {r: float(output.raw_score) for r in archetype.rubric}
        return EvaluationResult(
            raw_score=float(output.raw_score),
            rubric_scores=rubric_scores,
            evaluator_notes=output.evaluator_notes or None,
        )

    @staticmethod
    def _evaluate_listen_mcq(
        *,
        archetype: ArchetypeSpec,
        task_content: dict,
        user_response: dict,
    ) -> EvaluationResult:
        items = task_content.get("items") or []
        if not isinstance(items, list) or not items:
            return EvaluationResult(
                raw_score=0.0,
                rubric_scores={r: 0.0 for r in archetype.rubric},
                evaluator_notes="Listening task had no MCQ items to score.",
            )

        answer_rows = _listen_mcq_answer_rows(user_response)
        selected_by_id: dict[str, int] = {}
        for row in answer_rows:
            if not isinstance(row, dict):
                continue
            item_id = str(row.get("item_id") or "")
            try:
                selected_by_id[item_id] = int(row.get("selected_index"))
            except (TypeError, ValueError):
                continue

        total = 0
        correct = 0
        missing = 0
        for idx, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("item_id") or f"q{idx}")
            options = item.get("options") or []
            try:
                correct_index = int(item.get("correct_index"))
            except (TypeError, ValueError):
                continue
            if not isinstance(options, list) or not (0 <= correct_index < len(options)):
                continue
            total += 1
            selected_index = selected_by_id.get(item_id)
            if selected_index is None:
                missing += 1
                continue
            if selected_index == correct_index:
                correct += 1

        if total == 0:
            raw_score = 0.0
        else:
            raw_score = round((correct / total) * 10, 1)
        notes = (
            f"Deterministic listening MCQ score: {correct}/{total} correct"
            + (f", {missing} missing." if missing else ".")
        )
        return EvaluationResult(
            raw_score=raw_score,
            rubric_scores={r: raw_score for r in archetype.rubric},
            evaluator_notes=notes,
        )

    async def _evaluate_speak_and_record(
        self,
        *,
        archetype: ArchetypeSpec,
        task_content: dict,
        user_response: dict,
        evaluator_overrides: dict | None = None,
    ) -> EvaluationResult:
        if not has_any_transcript(user_response):
            return EvaluationResult(
                raw_score=0.0,
                rubric_scores={r: 0.0 for r in archetype.rubric},
                evaluator_notes="No speech transcript was submitted.",
            )

        speaking_items = build_speaking_eval_items(
            task_content=task_content,
            user_response=user_response,
        )
        try:
            output = await self.llm.generate_structured(
                system_prompt=eval_system_prompt(),
                user_prompt=build_speak_eval_user_prompt(
                    archetype=archetype,
                    task_content=task_content,
                    speaking_items=speaking_items,
                    evaluator_overrides=evaluator_overrides,
                ),
                output_model=EvaluationOutput,
                temperature=self.temperature,
            )
        except LLMError as exc:
            logger.warning(
                "LLM speaking evaluator failed for archetype=%s: %s",
                archetype.archetype_id, exc,
            )
            return EvaluationResult(
                raw_score=5.0,
                rubric_scores={r: 5.0 for r in archetype.rubric},
                evaluator_notes=f"Evaluator unavailable: {exc}",
            )

        rubric_scores = {r: float(output.raw_score) for r in archetype.rubric}
        return EvaluationResult(
            raw_score=float(output.raw_score),
            rubric_scores=rubric_scores,
            evaluator_notes=output.evaluator_notes or None,
        )


def _listen_mcq_answer_rows(user_response: dict) -> list:
    inner_response = user_response.get("inner_response")
    if isinstance(inner_response, dict) and isinstance(inner_response.get("answers"), list):
        return inner_response["answers"]
    answers = user_response.get("answers")
    return answers if isinstance(answers, list) else []
