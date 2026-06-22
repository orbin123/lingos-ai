"""Pydantic shapes for the preferences REST API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CourseLengthLiteral = Literal["24w", "48w"]


class UserCoursePreferenceRead(BaseModel):
    """Response for `GET /preferences`."""

    model_config = ConfigDict(from_attributes=True)

    course_length: CourseLengthLiteral
    tasks_per_day: int = Field(..., ge=2, le=4)
    allow_read: bool
    allow_write: bool
    allow_listen: bool
    allow_speak: bool
    current_week: int
    current_day_in_week: int
    current_day_started_at: datetime
    last_completed_on: date | None
    # Stamped once when the learner finishes the final day of the course; null
    # while still in progress. Drives the dashboard "course complete" state and
    # the completion certificate date.
    course_completed_at: datetime | None = None
    require_pass_to_advance: bool
    pass_threshold_pct: int = Field(..., ge=0, le=100)


class UserCoursePreferenceUpdate(BaseModel):
    """Body for `PATCH /preferences` — every field optional, partial update."""

    course_length: CourseLengthLiteral | None = None
    tasks_per_day: int | None = Field(default=None, ge=2, le=4)
    allow_read: bool | None = None
    allow_write: bool | None = None
    allow_listen: bool | None = None
    allow_speak: bool | None = None
    require_pass_to_advance: bool | None = None
    pass_threshold_pct: int | None = Field(default=None, ge=0, le=100)
