"""Pydantic schemas for the curriculum module — API request/response shapes."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.curriculum.models import (
    CourseLevel,
    CourseStatus,
    EnrollmentStatus,
)


# Course response (read-only, exposed by future GET /courses)

class CourseRead(BaseModel):
    """Public view of a course (catalog item)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: str
    duration_weeks: int
    target_level: CourseLevel
    status: CourseStatus


# Enrollment

class EnrollmentCreate(BaseModel):
    """Request body for POST /courses/enroll."""

    course_slug: str = Field(..., min_length=1, max_length=50)


class EnrollmentRead(BaseModel):
    """Public view of a user's enrollment."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    course_id: int
    current_week: int
    current_day_in_week: int
    tasks_per_day: int
    allow_reading: bool
    allow_writing: bool
    allow_listening: bool
    allow_speaking: bool
    status: EnrollmentStatus
    started_at: datetime | None
    course: CourseRead   # nested — frontend gets course details in one response


class EnrollmentSettingsUpdate(BaseModel):
    """User-configurable practice settings for the active enrollment."""

    tasks_per_day: int | None = Field(default=None, ge=1, le=4)
    allow_reading: bool | None = None
    allow_writing: bool | None = None
    allow_listening: bool | None = None
    allow_speaking: bool | None = None
