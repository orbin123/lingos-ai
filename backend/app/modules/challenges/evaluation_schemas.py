"""Structured schemas for IELTS challenge evaluation and feedback."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def validate_half_band(value: float) -> float:
    """Validate an IELTS band score in whole or half-band increments."""
    band = float(value)
    if band < 0.0 or band > 9.0:
        raise ValueError("IELTS band must be between 0.0 and 9.0")
    if abs((band * 2) - round(band * 2)) > 1e-9:
        raise ValueError("IELTS band must be in 0.5 increments")
    return band


class IELTSBandModel(BaseModel):
    """Base model with reusable IELTS band validation."""

    @field_validator("band", "section_band", "overall_score", check_fields=False)
    @classmethod
    def validate_band_fields(cls, value: float) -> float:
        return validate_half_band(value)


class WritingCriterionEvaluation(IELTSBandModel):
    """One IELTS Writing Task 2 criterion score and rationale."""

    model_config = ConfigDict(extra="forbid")

    band: float = Field(ge=0.0, le=9.0)
    rationale: NonEmptyString


class WritingCriteriaEvaluation(BaseModel):
    """The four official IELTS Writing Task 2 scoring criteria."""

    model_config = ConfigDict(extra="forbid")

    task_response: WritingCriterionEvaluation
    coherence_and_cohesion: WritingCriterionEvaluation
    lexical_resource: WritingCriterionEvaluation
    grammatical_range_and_accuracy: WritingCriterionEvaluation


class WritingIssue(BaseModel):
    """A specific issue found in the learner's writing."""

    model_config = ConfigDict(extra="forbid")

    quote: NonEmptyString
    issue: NonEmptyString
    correction: str = ""
    suggestion: NonEmptyString


class WritingPromptEvaluation(IELTSBandModel):
    """LLM evaluation for one writing prompt response."""

    model_config = ConfigDict(extra="forbid")

    item_id: NonEmptyString
    prompt: NonEmptyString
    response_excerpt: str = ""
    response_word_count: int = Field(ge=0)
    criteria: WritingCriteriaEvaluation
    issues: list[WritingIssue] = Field(default_factory=list)
    band: float = Field(ge=0.0, le=9.0)
    summary: NonEmptyString


class WritingEvaluationReport(IELTSBandModel):
    """Structured AI writing evaluation returned by the Phase 4 evaluator."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["ai_writing_phase_4"]
    items: list[WritingPromptEvaluation] = Field(default_factory=list)
    section_band: float = Field(ge=0.0, le=9.0)
    summary: NonEmptyString


class ReadingQuestionEvaluation(BaseModel):
    """Deterministic correctness for one MCQ reading item."""

    model_config = ConfigDict(extra="forbid")

    item_id: NonEmptyString
    prompt: NonEmptyString
    user_answer: str | None
    correct_answer: NonEmptyString
    correct_index: int = Field(ge=0, le=3)
    correct: bool
    explanation: str = ""


class ReadingEvaluationReport(IELTSBandModel):
    """Deterministic reading evaluation derived from the generated answer key."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["deterministic_answer_key"]
    total_correct: int = Field(ge=0)
    total_questions: int = Field(ge=0)
    raw_scaled_40: int = Field(ge=0, le=40)
    section_band: float = Field(ge=0.0, le=9.0)
    questions: list[ReadingQuestionEvaluation] = Field(default_factory=list)


class StubSectionEvaluation(IELTSBandModel):
    """Temporary Phase 4 evaluation for sections completed in later phases."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["hardcoded_phase_4_placeholder"]
    section_band: float = Field(ge=0.0, le=9.0)
    summary: NonEmptyString


class SectionScores(BaseModel):
    """IELTS component scores."""

    model_config = ConfigDict(extra="forbid")

    listening: float = Field(ge=0.0, le=9.0)
    reading: float = Field(ge=0.0, le=9.0)
    writing: float = Field(ge=0.0, le=9.0)
    speaking: float = Field(ge=0.0, le=9.0)

    @field_validator("listening", "reading", "writing", "speaking")
    @classmethod
    def validate_section_band(cls, value: float) -> float:
        return validate_half_band(value)


class UnifiedEvaluationReport(IELTSBandModel):
    """Full Phase 4 evaluation persisted on a challenge attempt."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["phase_4_text_sections"]
    reading: ReadingEvaluationReport
    writing: WritingEvaluationReport
    listening: StubSectionEvaluation
    speaking: StubSectionEvaluation
    section_scores: SectionScores
    overall_score: float = Field(ge=0.0, le=9.0)


class SectionFeedback(BaseModel):
    """Human-facing feedback for one IELTS section."""

    model_config = ConfigDict(extra="forbid")

    went_well: list[NonEmptyString] = Field(default_factory=list)
    needs_work: list[NonEmptyString] = Field(default_factory=list)
    next_tip: NonEmptyString


class FeedbackSections(BaseModel):
    """Feedback grouped by IELTS section."""

    model_config = ConfigDict(extra="forbid")

    listening: SectionFeedback
    reading: SectionFeedback
    writing: SectionFeedback
    speaking: SectionFeedback


class IELTSFeedbackReport(BaseModel):
    """Structured Phase 4 feedback persisted on a challenge attempt."""

    model_config = ConfigDict(extra="forbid")

    mode: Literal["phase_4_feedback"]
    overall_summary: NonEmptyString
    sections: FeedbackSections
