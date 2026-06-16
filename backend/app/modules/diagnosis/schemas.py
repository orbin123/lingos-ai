"""Pydantic schemas for the diagnosis API."""

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


class PronunciationWordIn(BaseModel):
    """One word from the Azure pronunciation assessment.

    Only the fields the result page needs (per-phoneme detail is dropped).
    """

    word: str
    accuracy_score: float = Field(ge=0, le=100)
    error_type: str | None = None


class ReadAloudIn(BaseModel):
    """Read-aloud result from Azure Speech Pronunciation Assessment.

    The frontend records the passage, converts the audio to WAV, POSTs it to
    ``/diagnosis/pronunciation-score`` (Azure), and includes the returned
    scores here in the main submit payload — keeping submit a clean JSON
    endpoint.

    All five scores are on Azure's 0–100 scale.
    """

    passage_id: str  # e.g. "diag_passage_v1"
    overall_score: float = Field(ge=0, le=100)
    accuracy_score: float = Field(ge=0, le=100)
    fluency_score: float = Field(ge=0, le=100)
    completeness_score: float = Field(ge=0, le=100)
    prosody_score: float = Field(ge=0, le=100)
    words: list[PronunciationWordIn] = Field(default_factory=list)


class DiagnosisSubmitRequest(BaseModel):
    """Full payload for POST /diagnosis/submit."""

    self_assessment: SelfAssessmentIn
    fill_blank: FillBlankIn
    writing: WritingIn
    read_aloud: ReadAloudIn


# ── Read-aloud analysis (returned to frontend) ─────────────────────────────


class ReadAloudAnalysisOut(BaseModel):
    """Azure read-aloud analysis shown in the result page scorecard.

    All five scores are on Azure's 0–100 scale.
    """

    overall: float = Field(ge=0, le=100)
    accuracy: float = Field(ge=0, le=100)
    fluency: float = Field(ge=0, le=100)
    completeness: float = Field(ge=0, le=100)
    prosody: float = Field(ge=0, le=100)
    words_to_improve: list[str] = Field(default_factory=list)


# ── Feedback sub-schemas ───────────────────────────────────────────────────


class SkillCalloutOut(BaseModel):
    """A skill stat card: which skill + a one-sentence description."""

    skill_name: str
    description: str


class FocusCalloutOut(BaseModel):
    """The 'first focus' stat card: a short title + a description."""

    title: str
    description: str


class DiagnosisFeedbackOut(BaseModel):
    """AI-generated feedback included in the diagnosis response."""

    estimated_level_label: str
    level_description: str
    summary: str
    biggest_weakness: SkillCalloutOut
    strongest_skill: SkillCalloutOut
    first_focus: FocusCalloutOut


# ── Final response ─────────────────────────────────────────────────────────


class DiagnosisSubmitResponse(BaseModel):
    """Response after diagnosis is computed."""

    skill_scores: dict[str, float]  # {"grammar": 3.0, "vocabulary": 2.7, ...}
    goal: UserGoal  # used for the "Personalized for …" meta
    feedback: DiagnosisFeedbackOut  # AI-generated interpretation
    read_aloud_analysis: ReadAloudAnalysisOut | None = None
    next_step: str = "Your first personalized task is ready."
