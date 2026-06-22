"""Concrete widget payload schemas used by generated session tasks."""

from __future__ import annotations

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.tasks.schemas.base import GeneratedTaskBase


class BlankItem(GeneratedTaskBase):
    """One cloze item for the FillInBlanks widget."""

    model_config = ConfigDict(extra="allow")

    item_id: str
    sentence_with_blank: str
    base_verb: str | None = None
    correct_answer: str
    distractors: list[str] = Field(default_factory=list)
    options: list[str] = Field(default_factory=list)
    grammar_rule: str | None = None
    explanation: str

    @field_validator("item_id", "sentence_with_blank", "correct_answer", "explanation")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be empty")
        return cleaned

    @field_validator("sentence_with_blank")
    @classmethod
    def _has_blank_marker(cls, value: str) -> str:
        if "___" not in value:
            raise ValueError("sentence_with_blank must contain ___")
        return value


class FillInBlanksTask(GeneratedTaskBase):
    """Payload contract for frontend FillBlanksWidget."""

    model_config = ConfigDict(extra="allow")

    topic: str
    instructions: str
    task_intro: str | None = None
    estimated_time_minutes: int | None = Field(default=None, ge=1, le=30)
    grammar_rule_explained: str | None = None
    passage_title: str | None = None
    passage: str | None = None
    primary_text: str = ""
    target_words: list[str] = Field(default_factory=list)
    items: list[BlankItem] = Field(default_factory=list, min_length=1)
    total_blanks: int | None = Field(default=None, ge=1)

    @field_validator("topic", "instructions")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be empty")
        return cleaned

    @model_validator(mode="after")
    def _sync_total_blanks(self) -> "FillInBlanksTask":
        # `total_blanks` is a derived count, not an independent input — coerce it
        # to the real item count rather than rejecting a payload the widget can
        # render fine. (A stochastic LLM that miscounts must not fail the session.)
        self.total_blanks = len(self.items)
        return self
