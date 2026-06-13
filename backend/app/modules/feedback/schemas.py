"""Request/response schemas for the feedback-prompt system."""

from datetime import date, datetime

from pydantic import BaseModel, Field


# ── User-facing ────────────────────────────────────────────────────


class ShouldShowResponse(BaseModel):
    show: bool
    trigger_type: str | None = None


class FeedbackSubmit(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    positive_feedback: str | None = Field(default=None, max_length=4000)
    improvement_feedback: str | None = Field(default=None, max_length=4000)
    bug_report: str | None = Field(default=None, max_length=4000)
    app_version: str | None = Field(default=None, max_length=40)


class FeedbackSubmitResponse(BaseModel):
    review_id: int
    created_at: datetime


class DismissResponse(BaseModel):
    dismissed: bool


# ── Admin analytics ────────────────────────────────────────────────


class ThemeCount(BaseModel):
    text: str
    count: int


class ReviewTrendPoint(BaseModel):
    date: date
    count: int
    average_rating: float


class ReviewStats(BaseModel):
    total_reviews: int
    average_rating: float | None
    rating_distribution: dict[int, int]
    # submitted prompts / total prompts shown
    submission_rate: float | None
    prompts_shown: int
    prompts_submitted: int
    top_improvements: list[ThemeCount]
    top_bugs: list[ThemeCount]
    trend: list[ReviewTrendPoint]
