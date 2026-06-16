"""Contract-unified task content normalization and validation.

Single pipeline: normalize loosely → project strictly. Generation and delivery
both use this so validators never disagree with ``project_task_payload``.
"""

from __future__ import annotations

from typing import Any

from app.modules.sessions.contracts.projection import project_task_payload
from app.modules.sessions.contracts.registry import get_contract
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
from app.modules.sessions.task_generator import (
    normalize_dictation_payload,
    normalize_dialogue_speaking_payload,
    normalize_error_correction_payload,
    normalize_error_spotting_payload,
    normalize_fill_in_blanks_payload,
    normalize_interview_speaking_payload,
    normalize_listen_and_respond_payload,
    normalize_listen_retell_payload,
    normalize_mcq_payload,
    normalize_open_text_payload,
    normalize_read_aloud_payload,
    normalize_read_structure_payload,
    normalize_sentence_transform_payload,
    normalize_speak_and_record_payload,
    normalize_speak_pic_desc_payload,
)
from app.scoring import get_archetype

_LISTEN_INNER_BY_ARCHETYPE: dict[str, str] = {
    "LISTEN_MCQ": "mcq",
    "LISTEN_INFER": "mcq",
    "LISTEN_TONE": "mcq",
    "LISTEN_CLOZE": "fill_in_blanks",
    "LISTEN_DICTATION": "open_text",
    "LISTEN_RETELL": "speak_and_record",
    "LISTEN_SHADOW": "speak_and_record",
}

_SPEAKING_DIALOGUE_ARCHETYPES = frozenset(
    {"SPEAK_ROLEPLAY", "SPEAK_SMALLTALK", "SPEAK_DEBATE"}
)


def infer_listen_inner_widget(archetype_id: str, content: dict[str, Any]) -> str:
    """Return the listening inner widget for an archetype when the LLM omitted it."""
    existing = str(content.get("inner_widget") or "").strip()
    if existing:
        return existing
    return _LISTEN_INNER_BY_ARCHETYPE.get(archetype_id, "mcq")


def normalize_task_content(
    archetype_id: str, content: dict[str, Any]
) -> dict[str, Any]:
    """Normalize loose generated/authored content for the archetype contract."""
    spec = get_archetype(archetype_id)
    payload_cls = get_contract(archetype_id).task_payload
    normalized = dict(content or {})
    normalized.setdefault("archetype_id", archetype_id)
    normalized.setdefault("core_activity", spec.core_activity)

    if archetype_id == "LISTEN_DICTATION":
        return normalize_dictation_payload(normalized)

    if archetype_id in {"LISTEN_RETELL", "LISTEN_SHADOW"}:
        return normalize_listen_retell_payload(normalized)

    if spec.core_activity == "listen":
        if not normalized.get("inner_widget"):
            normalized["inner_widget"] = infer_listen_inner_widget(
                archetype_id, normalized
            )
        return normalize_listen_and_respond_payload(normalized)

    if archetype_id == "READ_ERROR_SPOT":
        return normalize_error_spotting_payload(normalized)

    if archetype_id == "READ_STRUCTURE_ID":
        return normalize_read_structure_payload(normalized)

    if archetype_id == "READ_TONE_ID":
        normalized = normalize_mcq_payload(normalized)
        return normalized

    if archetype_id == "SPEAK_READ_ALOUD":
        return normalize_read_aloud_payload(normalized)

    if archetype_id == "SPEAK_PIC_DESC":
        return normalize_speak_pic_desc_payload(normalized)

    if archetype_id == "SPEAK_INTERVIEW":
        return normalize_interview_speaking_payload(normalized)

    if archetype_id in _SPEAKING_DIALOGUE_ARCHETYPES:
        return normalize_dialogue_speaking_payload(normalized)

    if archetype_id == "WRITE_OPEN_SENT":
        return normalize_open_text_payload(normalized)

    if archetype_id == "WRITE_SENT_TRANS":
        return normalize_sentence_transform_payload(normalized)

    if archetype_id == "WRITE_ERROR_CORR":
        return normalize_error_correction_payload(normalized)

    if payload_cls is McqPayload:
        return normalize_mcq_payload(normalized)

    if payload_cls is TfngPayload:
        return {**normalized, "widget": "true_false_not_given"}

    if payload_cls is FillBlanksPayload:
        return normalize_fill_in_blanks_payload(normalized)

    if payload_cls is OpenTextPayload:
        return normalize_open_text_payload(normalized)

    if payload_cls is TransformPayload:
        return normalize_sentence_transform_payload(normalized)

    if payload_cls is ErrorCorrectionPayload:
        return normalize_error_correction_payload(normalized)

    if payload_cls is ReadStructurePayload:
        return normalize_read_structure_payload(normalized)

    if payload_cls is SpeakingPayload:
        return normalize_speak_and_record_payload(normalized)

    if payload_cls is ErrorSpottingPayload:
        return normalize_error_spotting_payload(normalized)

    if payload_cls is DictationPayload:
        return normalize_dictation_payload(normalized)

    return normalized


def validate_and_project_task_content(
    archetype_id: str,
    content: dict[str, Any],
    *,
    activity_id: str = "gen-check",
    sequence: int = 1,
) -> dict[str, Any]:
    """Normalize, project onto the strict contract, and return merged content.

    Raises :class:`ContractValidationError` when the payload cannot satisfy the
    wire contract.
    """
    normalized = normalize_task_content(archetype_id, content)
    if normalized.get("audio_script") and not normalized.get("audio_duration_seconds"):
        word_count = len(str(normalized.get("audio_script") or "").split())
        normalized["audio_duration_seconds"] = max(1, int(round(word_count / 2.3)))
    projected = project_task_payload(
        archetype_id,
        normalized,
        activity_id=activity_id,
        sequence=sequence,
    )
    runtime_keys = (
        "phase",
        "inner_widget",
        "widget",
        "ui_widget",
        "speaking_prompts",
        "sample_responses",
        "image_error",
        "tts_error",
        "browser_tts_fallback",
        "cefr_level",
        "sub_level",
        "explanation_brief",
        "archetype_name",
    )
    runtime = {key: normalized[key] for key in runtime_keys if key in normalized}
    if projected.get("prompts"):
        runtime.setdefault("speaking_prompts", list(projected["prompts"]))
    if projected.get("sample_responses"):
        runtime.setdefault("sample_responses", list(projected["sample_responses"]))
    if normalized.get("image_error"):
        runtime["image_url"] = normalized.get("image_url")
    return {**normalized, **projected, **runtime}


__all__ = [
    "infer_listen_inner_widget",
    "normalize_task_content",
    "validate_and_project_task_content",
]
