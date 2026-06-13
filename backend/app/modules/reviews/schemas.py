"""Schemas for app reviews."""

from datetime import datetime

from pydantic import BaseModel, Field


class AppReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: str | None = Field(default=None, max_length=200)
    body: str | None = Field(default=None, max_length=4000)


class AppReviewRead(BaseModel):
    id: int
    user_id: int
    rating: int
    title: str | None
    body: str | None
    positive_feedback: str | None = None
    improvement_feedback: str | None = None
    bug_report: str | None = None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
