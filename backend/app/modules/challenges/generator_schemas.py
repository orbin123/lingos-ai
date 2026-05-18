"""Schemas for AI-generated challenge task payloads."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class GeneratedMCQItem(BaseModel):
    """Multiple-choice item generated for IELTS-style challenge sections."""

    model_config = ConfigDict(extra="forbid")

    item_id: NonEmptyString
    prompt: NonEmptyString
    options: list[NonEmptyString] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    explanation: NonEmptyString


class GeneratedWritingPrompt(BaseModel):
    """Writing prompt generated for the timed writing widget."""

    model_config = ConfigDict(extra="forbid")

    item_id: NonEmptyString
    prompt: NonEmptyString
    target_word_count: int = Field(gt=0)


class GeneratedTaskMeta(BaseModel):
    """Metadata that keeps the frontend and persisted JSON self-describing."""

    model_config = ConfigDict(extra="forbid")

    challenge_slug: NonEmptyString
    challenge_name: NonEmptyString
    level_number: int = Field(gt=0)
    level_name: NonEmptyString
    phase: Literal[3]


class GeneratedListeningSection(BaseModel):
    """Transcript-only listening payload for Phase 3."""

    model_config = ConfigDict(extra="forbid")

    widget: Literal["listen_and_respond"]
    task_intro: NonEmptyString
    instructions: NonEmptyString
    audio_url: None
    audio_script: NonEmptyString
    audio_duration_seconds: int = Field(gt=0)
    inner_widget: Literal["mcq"]
    items: list[GeneratedMCQItem] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_item_ids(self) -> "GeneratedListeningSection":
        _ensure_unique_item_ids(self.items, section_name="listening")
        return self


class GeneratedReadingSection(BaseModel):
    """Reading passage and MCQs consumed by the Phase 2 frontend."""

    model_config = ConfigDict(extra="forbid")

    widget: Literal["mcq"]
    task_intro: NonEmptyString
    instructions: NonEmptyString
    passage_title: NonEmptyString
    passage: NonEmptyString
    items: list[GeneratedMCQItem] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_item_ids(self) -> "GeneratedReadingSection":
        _ensure_unique_item_ids(self.items, section_name="reading")
        return self


class GeneratedWritingSection(BaseModel):
    """Writing payload consumed by the timed text widget."""

    model_config = ConfigDict(extra="forbid")

    widget: Literal["timed_text"]
    task_intro: NonEmptyString
    instructions: NonEmptyString
    items: list[GeneratedWritingPrompt] = Field(min_length=1)
    target_word_count: int = Field(gt=0)
    time_limit_seconds: int = Field(gt=0)
    minimum_word_count: int = Field(ge=0)
    no_editing_allowed: bool
    sample_response: str

    @model_validator(mode="after")
    def validate_item_ids(self) -> "GeneratedWritingSection":
        _ensure_unique_item_ids(self.items, section_name="writing")
        if self.minimum_word_count > self.target_word_count:
            raise ValueError("minimum_word_count cannot exceed target_word_count")
        return self


class GeneratedSpeakingSection(BaseModel):
    """Prompt-only speaking payload for Phase 3."""

    model_config = ConfigDict(extra="forbid")

    widget: Literal["speak_and_record"]
    task_intro: NonEmptyString
    instructions: NonEmptyString
    speaking_duration_seconds: int = Field(gt=0)
    speaking_prompts: list[NonEmptyString] = Field(min_length=1)
    sample_responses: list[str]


class GeneratedTaskSections(BaseModel):
    """All IELTS sections expected by the active challenge UI."""

    model_config = ConfigDict(extra="forbid")

    listening: GeneratedListeningSection
    reading: GeneratedReadingSection
    writing: GeneratedWritingSection
    speaking: GeneratedSpeakingSection


class GeneratedIELTSTaskPayload(BaseModel):
    """Top-level generated IELTS task payload persisted on an attempt."""

    model_config = ConfigDict(extra="forbid")

    meta: GeneratedTaskMeta
    sections: GeneratedTaskSections


def _ensure_unique_item_ids(items: list, *, section_name: str) -> None:
    item_ids = [item.item_id for item in items]
    if len(item_ids) != len(set(item_ids)):
        raise ValueError(f"{section_name} item_id values must be unique")
