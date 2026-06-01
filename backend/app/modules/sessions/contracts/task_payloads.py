"""Task-payload contracts — one model per render family (≈10).

Every archetype maps to exactly one of these in ``registry.py``. The model is
the strict schema the task agent's output is normalized into before the
orchestrator emits a ``task`` event. Optional fields let a family cover several
closely-related widgets without exploding into one class per archetype; WS3 may
split a family further if a widget needs a tighter contract.
"""

from __future__ import annotations

from pydantic import Field

from app.modules.sessions.contracts.base import (
    AudioMixin,
    BlankItem,
    DialogueTurn,
    DictationItem,
    ErrorCorrectionItem,
    ErrorSpottingSentence,
    InterviewQuestion,
    McqItem,
    OpenTextItem,
    StructureLabelItem,
    TaskPayloadBase,
    TfngItem,
    TransformItem,
)


class FillBlanksPayload(TaskPayloadBase):
    """READ_CLOZE, LISTEN_CLOZE — cloze passage with typed blanks.

    Listening variants additionally carry the ``audio_*`` fields.
    """

    passage_title: str = ""
    passage: str
    items: tuple[BlankItem, ...] = Field(min_length=1)
    # Present only for LISTEN_CLOZE.
    audio_genre: str = ""
    audio_script: str = ""
    audio_url: str | None = None
    audio_duration_seconds: int = 0


class McqPayload(TaskPayloadBase):
    """MCQ-style read/listen tasks.

    READ_COMP_MCQ, READ_CONTEXT_MCQ, READ_WORD_MATCH, READ_TONE_ID,
    LISTEN_MCQ, LISTEN_INFER, LISTEN_TONE.
    """

    items: tuple[McqItem, ...] = Field(min_length=1)
    passage_title: str = ""
    passage: str = ""
    # Present only for listening variants.
    audio_genre: str = ""
    audio_script: str = ""
    audio_url: str | None = None
    audio_duration_seconds: int = 0


class TfngPayload(TaskPayloadBase):
    """READ_TFNG — True / False / Not Given over a passage."""

    passage_title: str = ""
    passage: str
    items: tuple[TfngItem, ...] = Field(min_length=1)


class ErrorSpottingPayload(TaskPayloadBase):
    """READ_ERROR_SPOT — tap the incorrect token in each sentence."""

    passage_title: str = ""
    sentences: tuple[ErrorSpottingSentence, ...] = Field(min_length=1)


class DictationPayload(AudioMixin, TaskPayloadBase):
    """LISTEN_DICTATION — type each sentence exactly as heard."""

    items: tuple[DictationItem, ...] = Field(min_length=1)


class OpenTextPayload(TaskPayloadBase):
    """Free-writing tasks driven by prompts.

    WRITE_OPEN_SENT, WRITE_PARA, WRITE_EMAIL, WRITE_PARAPHRASE,
    WRITE_WORD_UPGRADE, WRITE_BULLETS_TO_PARA, WRITE_IDEA_PARA, WRITE_TIMED.
    """

    items: tuple[OpenTextItem, ...] = Field(min_length=1)
    prompt: str = ""
    sample_answer: str = ""
    minimum_words: int = 0
    bullets: tuple[str, ...] = ()
    common_mistakes: tuple[str, ...] = ()


class TransformPayload(TaskPayloadBase):
    """WRITE_SENT_TRANS — rewrite a source sentence."""

    items: tuple[TransformItem, ...] = Field(min_length=1)


class ErrorCorrectionPayload(TaskPayloadBase):
    """WRITE_ERROR_CORR — fix the sentence."""

    items: tuple[ErrorCorrectionItem, ...] = Field(min_length=1)


class ReadStructurePayload(TaskPayloadBase):
    """READ_STRUCTURE_ID — label each paragraph's structural role."""

    passage_title: str = ""
    structure_labels: tuple[str, ...] = Field(min_length=2)
    items: tuple[StructureLabelItem, ...] = Field(min_length=1)


class SpeakingPayload(TaskPayloadBase):
    """All SPEAK_* plus LISTEN_RETELL / LISTEN_SHADOW.

    A speaking response is one or more spoken turns. Optional fields adapt the
    same family to read-aloud, picture description, roleplay, interview, and
    listen-then-speak variants.
    """

    prompts: tuple[str, ...] = ()
    sample_responses: tuple[str, ...] = ()
    speaking_duration_seconds: int = Field(default=45, ge=5, le=600)

    # Variant-specific optional fields.
    text_to_read_aloud: str = ""          # read_aloud / shadow
    image_url: str = ""                    # pic_desc / present
    image_alt: str = ""
    dialogue_context: tuple[DialogueTurn, ...] = ()   # roleplay / smalltalk / debate
    questions: tuple[InterviewQuestion, ...] = ()      # interview
    # Present for LISTEN_RETELL / LISTEN_SHADOW (listen-then-speak).
    audio_genre: str = ""
    audio_script: str = ""
    audio_url: str | None = None
    audio_duration_seconds: int = 0
    passage_to_retell: str = ""


__all__ = [
    "FillBlanksPayload",
    "McqPayload",
    "TfngPayload",
    "ErrorSpottingPayload",
    "DictationPayload",
    "OpenTextPayload",
    "TransformPayload",
    "ErrorCorrectionPayload",
    "ReadStructurePayload",
    "SpeakingPayload",
]
