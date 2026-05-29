"""LLM-driven `Evaluator` implementation for the sessions flow.

Uses `ILLMClient.generate_structured` to coerce the model output into a
Pydantic schema. On any LLM failure, falls back to a conservative
mid-range score (5.0) so the session lifecycle keeps moving rather than
crashing — the evaluator notes record the failure cause for debugging.
"""

from __future__ import annotations

import json
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

        if (
            archetype.archetype_id == "LISTEN_CLOZE"
            or (
                task_content.get("widget") == "listen_and_respond"
                and task_content.get("inner_widget") == "fill_in_blanks"
            )
        ):
            return self._evaluate_listen_cloze(
                archetype=archetype,
                task_content=task_content,
                user_response=user_response,
            )

        if archetype.archetype_id == "READ_ERROR_SPOT":
            return self._evaluate_error_spotting(
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
    def _evaluate_error_spotting(
        *,
        archetype: ArchetypeSpec,
        task_content: dict,
        user_response: dict,
    ) -> EvaluationResult:
        sentences = task_content.get("passage_sentences") or []
        selected = user_response.get("selected_token_ids") or []
        if not isinstance(sentences, list) or not isinstance(selected, list):
            return EvaluationResult(
                raw_score=0.0,
                rubric_scores={r: 0.0 for r in archetype.rubric},
                evaluator_notes="Error spotting payload or response was malformed.",
            )

        selected_ids = {str(token_id) for token_id in selected}
        correct_errors: list[dict] = []
        for sentence in sentences:
            if not isinstance(sentence, dict):
                continue
            error = sentence.get("error")
            if isinstance(error, dict) and error.get("token_id"):
                correct_errors.append({
                    **error,
                    "sentence_id": sentence.get("sentence_id"),
                })

        correct_ids = {str(error["token_id"]) for error in correct_errors}
        found_ids = sorted(selected_ids & correct_ids)
        false_positive_ids = sorted(selected_ids - correct_ids)
        missed = [
            error
            for error in correct_errors
            if str(error["token_id"]) not in selected_ids
        ]
        total_errors = int(task_content.get("total_errors") or len(correct_ids) or 0)
        correct_count = len(found_ids)
        raw_score = round((correct_count / total_errors) * 10, 2) if total_errors else 0.0
        notes = {
            "task_type": "error_spotting",
            "selected_token_ids": sorted(selected_ids),
            "found_token_ids": found_ids,
            "missed_errors": missed,
            "false_positive_token_ids": false_positive_ids,
            "correct_count": correct_count,
            "total_errors": total_errors,
            "percentage": round((correct_count / total_errors) * 100, 2)
            if total_errors
            else 0.0,
        }
        return EvaluationResult(
            raw_score=raw_score,
            rubric_scores={r: raw_score for r in archetype.rubric},
            evaluator_notes=json.dumps(notes, ensure_ascii=False),
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

    @staticmethod
    def _evaluate_listen_cloze(
        *,
        archetype: ArchetypeSpec,
        task_content: dict,
        user_response: dict,
    ) -> EvaluationResult:
        items = task_content.get("items") or task_content.get("blanks") or []
        if not isinstance(items, list) or not items:
            return EvaluationResult(
                raw_score=0.0,
                rubric_scores={r: 0.0 for r in archetype.rubric},
                evaluator_notes="Listening cloze task had no blanks to score.",
            )

        submitted = _listen_cloze_answer_map(user_response)
        total = 0
        correct = 0
        missing = 0
        wrong_items: list[dict] = []
        for idx, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("item_id") or item.get("blank_id") or f"b{idx}")
            correct_answer = str(item.get("correct_answer") or "").strip()
            if not item_id or not correct_answer:
                continue
            total += 1
            user_answer = str(submitted.get(item_id) or "").strip()
            if not user_answer:
                missing += 1
                continue
            if user_answer.lower() == correct_answer.lower():
                correct += 1
            else:
                wrong_items.append(
                    {
                        "item_id": item_id,
                        "user_answer": user_answer,
                        "correct_answer": correct_answer,
                    }
                )

        raw_score = round((correct / total) * 10, 1) if total else 0.0
        notes = {
            "task_type": "listen_cloze",
            "correct_count": correct,
            "total_blanks": total,
            "missing": missing,
            "wrong_items": wrong_items,
        }
        return EvaluationResult(
            raw_score=raw_score,
            rubric_scores={r: raw_score for r in archetype.rubric},
            evaluator_notes=json.dumps(notes, ensure_ascii=False),
        )

    async def _evaluate_speak_and_record(
        self,
        *,
        archetype: ArchetypeSpec,
        task_content: dict,
        user_response: dict,
        evaluator_overrides: dict | None = None,
    ) -> EvaluationResult:
        if "pronunciation" in user_response:
            pronun = user_response["pronunciation"]
            if isinstance(pronun, dict):
                raw_score = round(pronun.get("overall_score", 0.0) / 10, 1)
                rubric_scores = {r: raw_score for r in archetype.rubric}
                notes = json.dumps({"task_type": "speak_read_aloud", "pronunciation": pronun}, ensure_ascii=False)
                return EvaluationResult(
                    raw_score=raw_score,
                    rubric_scores=rubric_scores,
                    evaluator_notes=notes,
                )
        elif archetype.archetype_id == "SPEAK_READ_ALOUD":
            # Read-aloud tasks should always include pronunciation data from the
            # Azure Assessment API.  If it is missing (e.g. API timeout on the
            # frontend, or the learner re-submitted without re-recording), log a
            # warning and fall through to the transcript-based LLM path rather
            # than returning 0.0 — a hard zero would corrupt the session
            # scorecard the first time and then be frozen by the idempotency
            # guard.
            logger.warning(
                "SPEAK_READ_ALOUD submission is missing 'pronunciation' key; "
                "falling through to transcript-based evaluator. "
                "archetype=%s",
                archetype.archetype_id,
            )

        if not has_any_transcript(user_response):
            # For read-aloud tasks use a neutral fallback instead of 0.0 so
            # that a transient Azure failure on the frontend does not permanently
            # corrupt the scorecard (which would be frozen by the idempotency
            # guard in complete_session).
            fallback_score = 5.0 if archetype.archetype_id == "SPEAK_READ_ALOUD" else 0.0
            fallback_notes = (
                "Pronunciation API score unavailable; neutral fallback applied."
                if archetype.archetype_id == "SPEAK_READ_ALOUD"
                else "No speech transcript was submitted."
            )
            return EvaluationResult(
                raw_score=fallback_score,
                rubric_scores={r: fallback_score for r in archetype.rubric},
                evaluator_notes=fallback_notes,
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
    if isinstance(answers, list):
        return answers

    # Live chat used to submit MCQ choices as a flat map like {"q1": 1}.
    # Keep accepting that older shape so already-rendered widgets do not score
    # correct answers as missing.
    rows = []
    for key, value in user_response.items():
        if key in {"inner_response", "listen_analytics", "time_spent_seconds", "answers"}:
            continue
        try:
            rows.append({"item_id": str(key), "selected_index": int(value)})
        except (TypeError, ValueError):
            continue
    return rows


def _listen_cloze_answer_map(user_response: dict) -> dict[str, str]:
    inner_response = user_response.get("inner_response")
    rows = []
    if isinstance(inner_response, dict) and isinstance(inner_response.get("answers"), list):
        rows = inner_response["answers"]
    elif isinstance(user_response.get("answers"), list):
        rows = user_response["answers"]

    out: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        item_id = str(row.get("item_id") or row.get("blank_id") or "")
        answer = row.get("user_answer")
        if item_id and answer is not None:
            out[item_id] = str(answer)

    for key, value in user_response.items():
        if key in {"inner_response", "listen_analytics", "time_spent_seconds", "answers"}:
            continue
        if isinstance(value, str):
            out.setdefault(key, value)
    return out
