"""Schema-boundary projection: loose runtime payloads → validated contracts.

This is the validate-then-normalize layer that sits between every agent and the
orchestrator (the "strict schema profile" the architecture calls for). The loose
dicts produced by the task generator, the ``EvaluationResult`` from the
evaluator, and the ``FeedbackResult`` from the feedback generator are projected
here into the strict contract models from this package *before* they are emitted
to the frontend.

A projection failure raises :class:`ContractValidationError`; callers decide
whether to repair, fall back to deterministic content, or emit a typed error
event — bad agent output never reaches a widget.

M2 implements the ``fill_blanks`` task family (``READ_CLOZE`` / ``LISTEN_CLOZE``)
plus the archetype-agnostic evaluation and feedback projections. WS3 extends the
task side to the remaining families; the eval/feedback projections are already
generic.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from pydantic import BaseModel, ValidationError

from app.modules.sessions.contracts.base import (
    BlankItem,
    DictationItem,
    ErrorCorrectionItem,
    ErrorSpottingError,
    ErrorSpottingSentence,
    ErrorSpottingToken,
    McqItem,
    OpenTextItem,
    StructureLabelItem,
    TfngItem,
    TransformItem,
)
from app.modules.sessions.contracts.evaluation import (
    ActivityEvaluationOutput,
    PronunciationAssessment,
)
from app.modules.sessions.contracts.feedback import (
    ActivityFeedbackOutput,
    FeedbackMistake,
)
from app.modules.sessions.contracts.registry import ArchetypeContract, get_contract
from app.modules.sessions.contracts.task_payloads import (
    DictationPayload,
    ErrorCorrectionPayload,
    ErrorSpottingPayload,
    FillBlanksPayload,
    McqPayload,
    OpenTextPayload,
    ReadStructurePayload,
    SpeakingPayload,
    TfngPayload,
    TransformPayload,
)
from app.modules.sessions.evaluator import EvaluationResult
from app.modules.sessions.feedback_generator import FeedbackResult
from app.scoring.constants import MAX_RAW_SCORE, MIN_RAW_SCORE
from app.scoring.engine import tier_for_score


_SECTION_LABELS = {
    "read": "Reading",
    "listen": "Listening",
    "write": "Writing",
    "speak": "Speaking",
}


def contract_widgets(archetype_id: str) -> dict[str, str]:
    """Return the rich widget keys an archetype's events should route to.

    The orchestrator stamps this on the task payload (under ``activity_contract``)
    so the task/evaluation/feedback events all render through the contracted rich
    widgets rather than the generic fallback.
    """
    contract = get_contract(archetype_id)
    return {
        "archetype_id": contract.archetype_id,
        "task_widget": contract.task_widget,
        "evaluation_widget": contract.evaluation_widget,
        "feedback_widget": contract.feedback_widget,
    }


class ContractValidationError(Exception):
    """Raised when loose agent output cannot be projected onto its contract.

    Carries the ``archetype_id`` and the underlying validation detail so the
    orchestrator can log, fall back, or emit a typed error event.
    """

    def __init__(self, archetype_id: str, detail: str) -> None:
        self.archetype_id = archetype_id
        self.detail = detail
        super().__init__(f"{archetype_id}: {detail}")


# ── Task projection ─────────────────────────────────────────────────


def project_task_payload(
    archetype_id: str,
    content: dict[str, Any],
    *,
    activity_id: str,
    sequence: int,
) -> dict[str, Any]:
    """Project a loose ``task_content`` dict onto its strict task contract.

    Returns the JSON-serializable payload (``model_dump(mode="json")``) the rich
    frontend widget consumes. Raises :class:`ContractValidationError` if the
    content does not satisfy the contract.
    """
    contract = get_contract(archetype_id)
    base = _base_task_fields(contract, content, activity_id, sequence)

    builder = _BODY_BUILDERS.get(contract.task_payload)
    if builder is None:  # pragma: no cover - guarded by registry coverage test
        raise ContractValidationError(
            archetype_id,
            f"no task projection implemented for {contract.task_payload.__name__}",
        )
    body = builder(archetype_id, content)

    try:
        model = contract.task_payload.model_validate({**base, **body})
    except ValidationError as exc:
        raise ContractValidationError(archetype_id, _fmt(exc)) from exc
    return model.model_dump(mode="json")


def _base_task_fields(
    contract: ArchetypeContract,
    content: dict[str, Any],
    activity_id: str,
    sequence: int,
) -> dict[str, Any]:
    return {
        "activity_id": activity_id,
        "sequence": sequence,
        "archetype_id": contract.archetype_id,
        "task_widget": contract.task_widget,
        "core_activity": contract.core_activity,
        "section_label": _str(content.get("section_label"))
        or _SECTION_LABELS.get(contract.core_activity, contract.core_activity.title()),
        "topic": _str(content.get("topic")),
        "task_intro": _str(content.get("task_intro")),
        "instructions": _str(content.get("instructions"))
        or _str(content.get("instruction")),
        "sub_skill": _str(content.get("sub_skill")) or _default_sub_skill(contract),
        "estimated_minutes": _int(
            content.get("estimated_minutes")
            or content.get("estimated_time_minutes"),
            default=3,
        ),
        "grammar_rule": _str(content.get("grammar_rule"))
        or _str(content.get("grammar_rule_explained"))
        or _str(content.get("grammar_rule_to_practice")),
        "target_words": tuple(content.get("target_words") or ()),
    }


# Each builder maps a loose ``task_content`` dict onto the body fields of one
# task-payload family. The base fields are added by ``_base_task_fields``; the
# family model's ``min_length`` / type rules do the final enforcement.


def _fill_blanks_body(archetype_id: str, content: dict[str, Any]) -> dict[str, Any]:
    items = _build_items(
        archetype_id,
        content.get("items") or content.get("blanks"),
        lambda raw: BlankItem(
            item_id=_str(raw.get("item_id") or raw.get("blank_id")),
            sentence_with_blank=_str(raw.get("sentence_with_blank")),
            correct_answer=_str(raw.get("correct_answer")),
            explanation=_str(raw.get("explanation")),
            base_verb=_str(raw.get("base_verb")),
        ),
    )
    return {
        "passage_title": _str(content.get("passage_title")),
        "passage": _passage(content),
        "items": items,
        **_audio_fields(content),
    }


def _mcq_body(archetype_id: str, content: dict[str, Any]) -> dict[str, Any]:
    items = _build_items(
        archetype_id,
        content.get("items"),
        lambda raw: McqItem(
            item_id=_str(raw.get("item_id")),
            prompt=_str(raw.get("prompt")),
            options=tuple(str(o) for o in (raw.get("options") or ())),
            correct_index=_int(raw.get("correct_index"), default=0),
            explanation=_str(raw.get("explanation")),
        ),
    )
    return {
        "items": items,
        "passage_title": _str(content.get("passage_title")),
        "passage": _passage(content),
        **_audio_fields(content),
    }


def _tfng_body(archetype_id: str, content: dict[str, Any]) -> dict[str, Any]:
    items = _build_items(
        archetype_id,
        content.get("items"),
        lambda raw: TfngItem(
            item_id=_str(raw.get("item_id")),
            prompt=_str(raw.get("prompt")),
            correct_answer=cast(Any, _tfng_answer(raw.get("correct_answer"))),
            explanation=_str(raw.get("explanation")),
        ),
    )
    return {
        "passage_title": _str(content.get("passage_title")),
        "passage": _passage(content),
        "items": items,
    }


def _error_spotting_body(
    archetype_id: str, content: dict[str, Any]
) -> dict[str, Any]:
    raw_sentences = content.get("passage_sentences") or content.get("sentences")
    sentences = _build_items(
        archetype_id, raw_sentences, _error_spotting_sentence
    )
    return {
        "passage_title": _str(content.get("passage_title")),
        "sentences": sentences,
    }


def _error_spotting_sentence(raw: dict[str, Any]) -> ErrorSpottingSentence:
    tokens = tuple(
        ErrorSpottingToken(
            token_id=_str(t.get("token_id")),
            text=_str(t.get("text")),
            is_error=bool(t.get("is_error")),
        )
        for t in (raw.get("tokens") or ())
        if isinstance(t, dict)
    )
    err = dict(raw.get("error") or {})
    # The generator carries an extra ``error_type`` the strict contract drops.
    error = ErrorSpottingError(
        token_id=_str(err.get("token_id")),
        incorrect_phrase=_str(err.get("incorrect_phrase")),
        correction=_str(err.get("correction")),
        rule=_str(err.get("rule")),
        explanation=_str(err.get("explanation")),
    )
    return ErrorSpottingSentence(
        sentence_id=_str(raw.get("sentence_id")),
        tokens=tokens,
        error=error,
    )


def _dictation_body(archetype_id: str, content: dict[str, Any]) -> dict[str, Any]:
    items = _build_items(
        archetype_id,
        content.get("items"),
        lambda raw: DictationItem(
            item_id=_str(raw.get("item_id")),
            prompt=_str(raw.get("prompt")),
            correct_answer=_str(raw.get("correct_answer")),
            explanation=_str(raw.get("explanation")),
        ),
    )
    # AudioMixin requires the audio fields — surface them as required, not optional.
    return {
        "items": items,
        "audio_genre": _str(content.get("audio_genre")),
        "audio_script": _str(content.get("audio_script")),
        "audio_url": _optional_str(content.get("audio_url")),
        "audio_duration_seconds": _int(
            content.get("audio_duration_seconds"), default=0
        ),
    }


def _open_text_body(archetype_id: str, content: dict[str, Any]) -> dict[str, Any]:
    items = _build_items(
        archetype_id,
        content.get("items"),
        lambda raw: OpenTextItem(
            item_id=_str(raw.get("item_id") or raw.get("id")),
            prompt=_str(raw.get("prompt")),
            sample_answer=_str(raw.get("sample_answer")),
            answer_hints=_str_tuple(raw.get("answer_hints")),
        ),
    )
    return {
        "items": items,
        "prompt": _str(content.get("prompt")),
        "sample_answer": _str(content.get("sample_answer")),
        "minimum_words": _int(content.get("minimum_words"), default=0),
        "bullets": _str_tuple(content.get("bullets")),
        "common_mistakes": _str_tuple(content.get("common_mistakes")),
    }


def _transform_body(archetype_id: str, content: dict[str, Any]) -> dict[str, Any]:
    items = _build_items(
        archetype_id,
        content.get("items"),
        lambda raw: TransformItem(
            item_id=_str(raw.get("item_id") or raw.get("id")),
            source_sentence=_str(raw.get("source_sentence") or raw.get("source")),
            sample_answer=_str(raw.get("sample_answer")),
            watch_hints=_str_tuple(raw.get("watch_hints")),
        ),
    )
    return {"items": items}


def _error_correction_body(
    archetype_id: str, content: dict[str, Any]
) -> dict[str, Any]:
    items = _build_items(
        archetype_id,
        content.get("items"),
        lambda raw: ErrorCorrectionItem(
            item_id=_str(raw.get("item_id") or raw.get("id")),
            incorrect_sentence=_str(
                raw.get("incorrect_sentence") or raw.get("incorrect")
            ),
            sample_answer=_str(raw.get("sample_answer") or raw.get("correction")),
            watch_hints=_str_tuple(raw.get("watch_hints")),
        ),
    )
    return {"items": items}


def _read_structure_body(
    archetype_id: str, content: dict[str, Any]
) -> dict[str, Any]:
    items = _build_items(
        archetype_id,
        content.get("items"),
        lambda raw: StructureLabelItem(
            item_id=_str(raw.get("item_id")),
            paragraph=_str(raw.get("paragraph")),
            correct_answer=_str(raw.get("correct_answer")),
            explanation=_str(raw.get("explanation")),
            label=_str(raw.get("label")),
        ),
    )
    return {
        "passage_title": _str(content.get("passage_title")),
        "structure_labels": _str_tuple(content.get("structure_labels")),
        "items": items,
    }


def _speaking_body(archetype_id: str, content: dict[str, Any]) -> dict[str, Any]:
    prompts = _str_tuple(
        content.get("speaking_prompts")
        or content.get("prompts")
        or ([content.get("speaking_prompt")] if content.get("speaking_prompt") else [])
    )
    return {
        "prompts": prompts,
        "sample_responses": _str_tuple(
            content.get("sample_responses") or content.get("sample_answers")
        ),
        "speaking_duration_seconds": _int(
            content.get("speaking_duration_seconds"), default=45
        ),
        "text_to_read_aloud": _str(
            content.get("text_to_read_aloud") or content.get("passage")
        ),
        "image_url": _str(content.get("image_url")),
        "image_alt": _str(content.get("image_alt")),
        "passage_to_retell": _str(content.get("passage_to_retell")),
        **_audio_fields(content),
    }


_BODY_BUILDERS = {
    FillBlanksPayload: _fill_blanks_body,
    McqPayload: _mcq_body,
    TfngPayload: _tfng_body,
    ErrorSpottingPayload: _error_spotting_body,
    DictationPayload: _dictation_body,
    OpenTextPayload: _open_text_body,
    TransformPayload: _transform_body,
    ErrorCorrectionPayload: _error_correction_body,
    ReadStructurePayload: _read_structure_body,
    SpeakingPayload: _speaking_body,
}


# ── Evaluation projection ───────────────────────────────────────────


def project_evaluation(
    archetype_id: str,
    *,
    activity_id: str,
    evaluation: EvaluationResult,
    sub_skill_breakdown: dict[str, float] | None = None,
    pronunciation_assessment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project an :class:`EvaluationResult` onto the strict evaluation contract."""
    raw = _clamp(evaluation.raw_score, MIN_RAW_SCORE, MAX_RAW_SCORE)
    try:
        pronunciation = (
            PronunciationAssessment.model_validate(pronunciation_assessment)
            if pronunciation_assessment is not None
            else None
        )
        model = ActivityEvaluationOutput(
            activity_id=activity_id,
            archetype_id=archetype_id,
            raw_score=raw,
            percentage=raw * 10.0,
            tier=tier_for_score(raw),
            rubric_scores=dict(evaluation.rubric_scores),
            sub_skill_breakdown=dict(sub_skill_breakdown or {}),
            pronunciation_assessment=pronunciation,
            evaluator_notes=evaluation.evaluator_notes or "",
        )
    except ValidationError as exc:
        raise ContractValidationError(archetype_id, _fmt(exc)) from exc
    return model.model_dump(mode="json")


# ── Feedback projection ─────────────────────────────────────────────


def project_feedback(
    archetype_id: str,
    *,
    activity_id: str,
    feedback: FeedbackResult,
) -> dict[str, Any]:
    """Project a :class:`FeedbackResult` onto the strict feedback contract."""
    mistakes = tuple(
        FeedbackMistake(
            issue=m.issue,
            user_wrote=m.user_wrote or "",
            correction=m.correction or "",
            rule=m.rule or "",
            sub_skills_affected=tuple(m.sub_skills_affected),
        )
        for m in feedback.mistakes
    )
    try:
        model = ActivityFeedbackOutput(
            activity_id=activity_id,
            archetype_id=archetype_id,
            score=feedback.score,
            summary=feedback.summary,
            did_well=tuple(feedback.did_well),
            mistakes=mistakes,
            next_tip=feedback.next_tip or "",
            sub_skill_breakdown=dict(feedback.sub_skill_breakdown),
        )
    except ValidationError as exc:
        raise ContractValidationError(archetype_id, _fmt(exc)) from exc
    return model.model_dump(mode="json")


# ── helpers ─────────────────────────────────────────────────────────


def _default_sub_skill(contract: ArchetypeContract) -> str:
    if contract.rubric:
        return contract.rubric[0]
    if contract.weight_map:
        return next(iter(contract.weight_map))
    return ""


def _build_items(
    archetype_id: str,
    raw_items: Any,
    builder: "Callable[[dict[str, Any]], BaseModel]",
) -> tuple[BaseModel, ...]:
    """Build a tuple of strict item models, mapping loose dicts via ``builder``.

    Non-dict entries are skipped; a malformed item raises
    :class:`ContractValidationError`. Emptiness is enforced by the payload
    model's ``min_length`` rather than here.
    """
    items: list[BaseModel] = []
    for raw in raw_items or ():
        if not isinstance(raw, dict):
            continue
        try:
            items.append(builder(raw))
        except ValidationError as exc:
            raise ContractValidationError(archetype_id, _fmt(exc)) from exc
    return tuple(items)


def _passage(content: dict[str, Any]) -> str:
    return _str(content.get("passage")) or _str(content.get("primary_text"))


def _audio_fields(content: dict[str, Any]) -> dict[str, Any]:
    """Optional audio source fields, present only when the content carries them."""
    if not content.get("audio_script"):
        return {}
    return {
        "audio_genre": _str(content.get("audio_genre")),
        "audio_script": _str(content.get("audio_script")),
        "audio_url": _optional_str(content.get("audio_url")),
        "audio_duration_seconds": _int(
            content.get("audio_duration_seconds"), default=0
        ),
    }


def _str_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(v).strip() for v in value if str(v).strip())


def _optional_str(value: Any) -> str | None:
    cleaned = str(value or "").strip()
    return cleaned or None


def _tfng_answer(value: Any) -> str:
    """Coerce a True/False/Not Given answer to its canonical casing.

    Passes unknown values through so the strict ``Literal`` raises and the
    caller falls back, rather than guessing.
    """
    text = _str(value).lower()
    return {
        "true": "True",
        "false": "False",
        "not given": "Not Given",
        "notgiven": "Not Given",
    }.get(text, _str(value))


def _str(value: Any) -> str:
    return str(value).strip() if value not in (None, "") else ""


def _int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _fmt(exc: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors()
    )


__all__ = [
    "ContractValidationError",
    "contract_widgets",
    "project_task_payload",
    "project_evaluation",
    "project_feedback",
]
