"""Pydantic schemas for the diagnosis API."""

from typing import Literal

from pydantic import BaseModel, Field

from app.modules.auth.models import (
    ContentExposure,
    SelfAssessedLevel,
    UserGoal,
)

# ── Input schemas ──────────────────────────────────────────────────────────

class SelfAssessmentIn(BaseModel):
    """User's own answers to the 5 self-assessment questions."""
    self_assessed_level: SelfAssessedLevel
    goal: UserGoal
    daily_time_minutes: int = Field(ge=5, le=240)
    content_exposure: ContentExposure
    interests: list[str] = Field(default_factory=list, max_length=3)


class FillBlankIn(BaseModel):
    """User's answers to the 5 fill-in-the-blank questions."""
    question_set_id: str  # e.g. "diag_fillblank_v1"
    answers: list[str] = Field(min_length=5, max_length=5)


class WritingIn(BaseModel):
    """User's writing response."""
    prompt_id: str  # e.g. "diag_writing_v1"
    response_text: str = Field(min_length=10, max_length=2000)


class ReadAloudWordTiming(BaseModel):
    """One Whisper word timestamp used for pacing and mismatch analysis."""
    word: str = Field(min_length=1)
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(ge=0)
    confidence: float | None = Field(default=None, ge=0, le=1)


class ReadAloudIn(BaseModel):
    """User's read-aloud result after Whisper transcription.

    The frontend uploads audio to POST /diagnosis/transcribe first,
    receives back the transcript and duration, then includes them here
    in the main submit payload — keeping submit as a clean JSON endpoint.
    """
    passage_id: str           # e.g. "diag_passage_v1"
    transcript: str           # Whisper output — what the user actually said
    duration_seconds: float = Field(gt=0)  # total recording length in seconds
    words: list[ReadAloudWordTiming] = Field(default_factory=list)


class DiagnosisSubmitRequest(BaseModel):
    """Full payload for POST /diagnosis/submit."""
    self_assessment: SelfAssessmentIn
    fill_blank: FillBlankIn
    writing: WritingIn
    read_aloud: ReadAloudIn


# ── Transcription response (POST /diagnosis/transcribe) ───────────────────

class TranscribeResponse(BaseModel):
    """Returned by POST /diagnosis/transcribe.

    The frontend receives this and includes transcript + duration_seconds
    + word timestamps in its final DiagnosisSubmitRequest.
    """
    transcript: str
    duration_seconds: float
    words: list[ReadAloudWordTiming] = Field(default_factory=list)


class ReadAloudMismatchOut(BaseModel):
    """One detected transcript/reference mismatch."""
    issue: Literal["substitution", "omission", "insertion"]
    reference_word: str | None = None
    transcript_word: str | None = None
    reference_index: int | None = Field(default=None, ge=0)
    transcript_index: int | None = Field(default=None, ge=0)


class ReadAloudAnalysisOut(BaseModel):
    """Whisper-only read-aloud analysis for the MVP pronunciation flow."""
    fluency_score: float = Field(ge=0, le=1)
    clarity_score: float = Field(ge=0, le=1)
    transcript_similarity: float = Field(ge=0, le=1)
    word_accuracy: float = Field(ge=0, le=1)
    words_per_minute: float = Field(ge=0)
    pause_count: int = Field(ge=0)
    long_pause_count: int = Field(ge=0)
    longest_pause_seconds: float = Field(ge=0)
    average_pause_seconds: float = Field(ge=0)
    mismatch_count: int = Field(ge=0)
    mismatches: list[ReadAloudMismatchOut] = Field(default_factory=list)


# ── Feedback sub-schemas ───────────────────────────────────────────────────

class WeakSkillExplanationOut(BaseModel):
    """Plain-English explanation for one weak skill — returned to frontend."""
    skill_name: str
    what_it_means: str
    why_it_matters: str
    what_to_expect: str


class DiagnosisFeedbackOut(BaseModel):
    """AI-generated feedback included in the diagnosis response."""
    estimated_level_label: str
    summary: str
    weak_skill_explanations: list[WeakSkillExplanationOut]
    motivation: str
    first_week_focus: str


# ── Final response ─────────────────────────────────────────────────────────

class DiagnosisSubmitResponse(BaseModel):
    """Response after diagnosis is computed."""
    skill_scores: dict[str, float]      # {"grammar": 3.0, "vocabulary": 2.7, ...}
    weakest_skills: list[str]           # 2 lowest, by score
    feedback: DiagnosisFeedbackOut      # AI-generated interpretation
    read_aloud_analysis: ReadAloudAnalysisOut | None = None
    next_step: str = "Your first personalized task is ready."
