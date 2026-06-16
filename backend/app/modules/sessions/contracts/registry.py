"""Archetype Contract Registry — the single source of truth that ties each
archetype to its task widget, agents, render widgets, and strict I/O schemas.

The curriculum blueprint (``source_24w.py``) only references an
``archetype_id``. Everything else the runtime needs — which task agent to run,
which rich frontend widget renders it, which schema the agent output must
satisfy, which evaluation/feedback widgets close the loop — is resolved here.

Add a new *day*  → write blueprint data (no code here changes).
Add a new *kind* of activity → add one archetype to the scoring registry and
one row to ``_TASK_SPEC`` below; the contract is then reusable forever.

This module composes ``app.scoring.ARCHETYPE_REGISTRY`` rather than duplicating
it, and fails at import time if any registered archetype lacks a contract.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel

from app.modules.sessions.contracts.evaluation import ActivityEvaluationOutput
from app.modules.sessions.contracts.feedback import ActivityFeedbackOutput
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
from app.scoring import ARCHETYPE_REGISTRY
from app.scoring.types import ArchetypeSpec


# ── Canonical widget vocabularies (cross-checked against the frontend) ──

# Rich task widgets — must match TaskWidgetKind in tasks/source.ts.
KNOWN_TASK_WIDGETS: frozenset[str] = frozenset(
    {
        "read_comp_mcq",
        "read_tfng",
        "error_spotting",
        "fill_blanks",
        "read_word_match",
        "read_context_mcq",
        "read_tone_id",
        "read_structure",
        "open_text",
        "sentence_transform",
        "error_correction",
        "write_paragraph",
        "write_email",
        "write_word_upgrade",
        "write_paraphrase",
        "write_timed",
        "write_bullets_to_para",
        "listen_mcq",
        "listen_cloze",
        "listen_dictation",
        "listen_infer",
        "listen_retell",
        "listen_shadow",
        "listen_tone",
        "read_aloud",
        "speak_pic_desc",
        "speak_timed",
        "speak_interview",
        "speak_roleplay",
        "speak_smalltalk",
        "speak_debate",
        "speak_present",
        "speak_record",
    }
)

EVALUATION_WIDGETS: frozenset[str] = frozenset(
    {"read_listen_evaluation", "write_speak_evaluation", "read_aloud_assessment"}
)
FEEDBACK_WIDGETS: frozenset[str] = frozenset(
    {"read_listen_feedback", "write_speak_feedback", "read_aloud_assessment"}
)


# ── Per-archetype task spec: (rich task widget, task payload model) ──────

_TASK_SPEC: dict[str, tuple[str, type[BaseModel]]] = {
    # Reading
    "READ_COMP_MCQ": ("read_comp_mcq", McqPayload),
    "READ_TFNG": ("read_tfng", TfngPayload),
    "READ_ERROR_SPOT": ("error_spotting", ErrorSpottingPayload),
    "READ_CLOZE": ("fill_blanks", FillBlanksPayload),
    "READ_WORD_MATCH": ("read_word_match", McqPayload),
    "READ_CONTEXT_MCQ": ("read_context_mcq", McqPayload),
    "READ_TONE_ID": ("read_tone_id", McqPayload),
    "READ_STRUCTURE_ID": ("read_structure", ReadStructurePayload),
    # Writing
    "WRITE_OPEN_SENT": ("open_text", OpenTextPayload),
    "WRITE_SENT_TRANS": ("sentence_transform", TransformPayload),
    "WRITE_ERROR_CORR": ("error_correction", ErrorCorrectionPayload),
    "WRITE_PARA": ("write_paragraph", OpenTextPayload),
    "WRITE_EMAIL": ("write_email", OpenTextPayload),
    "WRITE_WORD_UPGRADE": ("write_word_upgrade", OpenTextPayload),
    "WRITE_PARAPHRASE": ("write_paraphrase", ErrorCorrectionPayload),
    "WRITE_IDEA_PARA": ("write_paragraph", OpenTextPayload),
    "WRITE_TIMED": ("write_timed", OpenTextPayload),
    "WRITE_BULLETS_TO_PARA": ("write_bullets_to_para", OpenTextPayload),
    # Listening
    "LISTEN_MCQ": ("listen_mcq", McqPayload),
    "LISTEN_CLOZE": ("listen_cloze", FillBlanksPayload),
    "LISTEN_DICTATION": ("listen_dictation", DictationPayload),
    "LISTEN_INFER": ("listen_infer", McqPayload),
    "LISTEN_RETELL": ("listen_retell", SpeakingPayload),
    "LISTEN_SHADOW": ("listen_shadow", SpeakingPayload),
    "LISTEN_TONE": ("listen_tone", McqPayload),
    # Speaking
    "SPEAK_READ_ALOUD": ("read_aloud", SpeakingPayload),
    "SPEAK_PIC_DESC": ("speak_pic_desc", SpeakingPayload),
    "SPEAK_TIMED": ("speak_timed", SpeakingPayload),
    "SPEAK_INTERVIEW": ("speak_interview", SpeakingPayload),
    "SPEAK_ROLEPLAY": ("speak_roleplay", SpeakingPayload),
    "SPEAK_OPINION": ("speak_present", SpeakingPayload),
    "SPEAK_SMALLTALK": ("speak_smalltalk", SpeakingPayload),
    "SPEAK_DEBATE": ("speak_debate", SpeakingPayload),
    "SPEAK_PRESENT": ("speak_present", SpeakingPayload),
}

# Archetypes scored deterministically (no LLM judgement needed).
_OBJECTIVE: frozenset[str] = frozenset(
    {
        "READ_COMP_MCQ",
        "READ_TFNG",
        "READ_ERROR_SPOT",
        "READ_CLOZE",
        "READ_WORD_MATCH",
        "READ_CONTEXT_MCQ",
        "READ_TONE_ID",
        "LISTEN_MCQ",
        "LISTEN_CLOZE",
        "LISTEN_DICTATION",
        "LISTEN_INFER",
        "LISTEN_TONE",
    }
)

# Archetypes that produce a pronunciation assessment (Azure Speech).
_PRONUNCIATION: frozenset[str] = frozenset({"SPEAK_READ_ALOUD", "LISTEN_SHADOW"})


@dataclass(frozen=True)
class ArchetypeContract:
    """Everything the runtime needs to drive one activity slot, end to end."""

    archetype_id: str
    name: str
    core_activity: str
    rubric: tuple[str, ...]
    weight_map: dict[str, float]

    # Task slot
    task_widget: str
    task_agent: str
    task_payload: type[BaseModel]

    # Evaluation slot
    evaluator: str
    evaluation_widget: str
    evaluation_payload: type[BaseModel]

    # Feedback slot
    feedback_generator: str
    feedback_widget: str
    feedback_payload: type[BaseModel]

    has_pronunciation: bool


def _evaluator_for(archetype_id: str) -> str:
    if archetype_id in _PRONUNCIATION:
        return "pronunciation"
    if archetype_id in _OBJECTIVE:
        return "objective"
    return "llm"


def _eval_widget_for(archetype_id: str, core_activity: str) -> str:
    if archetype_id in _PRONUNCIATION:
        return "read_aloud_assessment"
    return (
        "read_listen_evaluation"
        if core_activity in {"read", "listen"}
        else "write_speak_evaluation"
    )


def _feedback_widget_for(archetype_id: str, core_activity: str) -> str:
    if archetype_id in _PRONUNCIATION:
        return "read_aloud_assessment"
    return (
        "read_listen_feedback"
        if core_activity in {"read", "listen"}
        else "write_speak_feedback"
    )


def _build_contract(spec: ArchetypeSpec) -> ArchetypeContract:
    aid = spec.archetype_id
    task_widget, task_payload = _TASK_SPEC[aid]
    if task_widget not in KNOWN_TASK_WIDGETS:
        raise ValueError(
            f"{aid}: task_widget {task_widget!r} not in KNOWN_TASK_WIDGETS"
        )
    return ArchetypeContract(
        archetype_id=aid,
        name=spec.name,
        core_activity=spec.core_activity,
        rubric=spec.rubric,
        weight_map=dict(spec.weight_map),
        task_widget=task_widget,
        task_agent="default",
        task_payload=task_payload,
        evaluator=_evaluator_for(aid),
        evaluation_widget=_eval_widget_for(aid, spec.core_activity),
        evaluation_payload=ActivityEvaluationOutput,
        feedback_generator="pronunciation" if aid in _PRONUNCIATION else "default",
        feedback_widget=_feedback_widget_for(aid, spec.core_activity),
        feedback_payload=ActivityFeedbackOutput,
        has_pronunciation=aid in _PRONUNCIATION,
    )


def _assemble() -> dict[str, ArchetypeContract]:
    missing = sorted(set(ARCHETYPE_REGISTRY) - set(_TASK_SPEC))
    if missing:
        raise ValueError(
            "archetypes registered in scoring but missing a contract in "
            f"_TASK_SPEC: {missing}"
        )
    extra = sorted(set(_TASK_SPEC) - set(ARCHETYPE_REGISTRY))
    if extra:
        raise ValueError(f"_TASK_SPEC references unknown archetypes: {extra}")
    return {aid: _build_contract(spec) for aid, spec in ARCHETYPE_REGISTRY.items()}


ARCHETYPE_CONTRACTS: dict[str, ArchetypeContract] = _assemble()


def get_contract(archetype_id: str) -> ArchetypeContract:
    """Return the full contract for ``archetype_id``. Raises KeyError if unknown."""
    try:
        return ARCHETYPE_CONTRACTS[archetype_id]
    except KeyError:
        raise KeyError(f"no contract for archetype_id: {archetype_id!r}") from None


__all__ = [
    "ArchetypeContract",
    "ARCHETYPE_CONTRACTS",
    "get_contract",
    "KNOWN_TASK_WIDGETS",
    "EVALUATION_WIDGETS",
    "FEEDBACK_WIDGETS",
]
