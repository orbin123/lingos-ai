"""Shared base shapes for the chat-session payload contracts.

These are the *strict schema profiles* every agent output must satisfy before
the orchestrator is allowed to emit it to the frontend. The reusable chat
widgets render directly from these shapes, so a payload that validates here is
guaranteed to be renderable.

Field names are snake_case (the wire format emitted over the WebSocket). The
frontend rich widgets (``components/chat/**``) consume these keys.

Design rules:
  - ``extra="forbid"`` — a strict profile rejects unknown keys. Agent output is
    normalized *into* these models; it never flows around them.
  - One **family** model per render shape (≈10), not one per archetype. The
    archetype → family mapping lives in ``registry.py``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CoreActivity = Literal["read", "write", "listen", "speak"]


class StrictModel(BaseModel):
    """Base for every contract model: frozen-ish, forbids unknown keys."""

    model_config = ConfigDict(extra="forbid")


class TaskPayloadBase(StrictModel):
    """Identity + render header shared by every task widget.

    Mirrors ``BaseTask`` in the frontend reference spec
    (``components/chat/tasks/source.ts``). Family models below extend this with
    their widget-specific body.
    """

    activity_id: str
    sequence: int = Field(ge=1)
    archetype_id: str
    task_widget: str  # rich frontend widget key, e.g. "read_tfng"
    core_activity: CoreActivity
    section_label: str
    topic: str
    task_intro: str
    instructions: str
    sub_skill: str
    estimated_minutes: int = Field(default=3, ge=1, le=60)

    # Common optional teaching aids many widgets surface.
    grammar_rule: str = ""
    target_words: tuple[str, ...] = ()


class AudioMixin(StrictModel):
    """Audio source fields for listening tasks."""

    audio_genre: str
    audio_script: str
    audio_url: str | None = None
    audio_duration_seconds: int = Field(ge=1, le=600)


# ── Reusable item shapes ───────────────────────────────────────────


class BlankItem(StrictModel):
    item_id: str
    sentence_with_blank: str
    correct_answer: str
    explanation: str
    base_verb: str = ""


class McqItem(StrictModel):
    item_id: str
    prompt: str
    options: tuple[str, ...] = Field(min_length=2)
    correct_index: int = Field(ge=0)
    explanation: str


class TfngItem(StrictModel):
    item_id: str
    prompt: str
    correct_answer: Literal["True", "False", "Not Given"]
    explanation: str


class DictationItem(StrictModel):
    item_id: str
    prompt: str
    correct_answer: str
    explanation: str


class OpenTextItem(StrictModel):
    item_id: str
    prompt: str
    sample_answer: str
    answer_hints: tuple[str, ...] = ()


class TransformItem(StrictModel):
    item_id: str
    source_sentence: str
    sample_answer: str
    watch_hints: tuple[str, ...] = ()


class ErrorCorrectionItem(StrictModel):
    item_id: str
    incorrect_sentence: str
    sample_answer: str
    watch_hints: tuple[str, ...] = ()


class StructureLabelItem(StrictModel):
    item_id: str
    paragraph: str
    correct_answer: str
    explanation: str
    label: str = ""


class ErrorSpottingToken(StrictModel):
    token_id: str
    text: str
    is_error: bool = False


class ErrorSpottingError(StrictModel):
    token_id: str
    incorrect_phrase: str
    correction: str
    rule: str
    explanation: str


class ErrorSpottingSentence(StrictModel):
    sentence_id: str
    tokens: tuple[ErrorSpottingToken, ...] = Field(min_length=1)
    error: ErrorSpottingError


class DialogueTurn(StrictModel):
    role: str
    text: str
    speaker: Literal["partner", "learner", "ai"]


class InterviewQuestion(StrictModel):
    item_id: str
    interviewer_prompt: str
    sample_answer: str = ""
    answer_hint: str = ""
