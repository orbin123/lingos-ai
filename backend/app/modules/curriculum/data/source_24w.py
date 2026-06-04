"""Backward-compat shim: composed 24-week calendar view."""

from __future__ import annotations

from app.modules.curriculum.data.composer import compose_weeks
from app.modules.curriculum.data.types import (
    ActivityBlueprint,
    ActivityKind,
    DaySource,
    EvaluationBlueprint,
    FeedbackBlueprint,
    FinalReviewBlueprint,
    LevelBand,
    TaskBlueprint,
    TeacherBlueprint,
    TeacherStep,
    Theme,
    WeekSource,
)
from app.scoring import CourseLength

WEEKS_24: tuple[WeekSource, ...] = compose_weeks(CourseLength.WEEKS_24)

__all__ = [
    "ActivityBlueprint",
    "ActivityKind",
    "DaySource",
    "EvaluationBlueprint",
    "FeedbackBlueprint",
    "FinalReviewBlueprint",
    "LevelBand",
    "TaskBlueprint",
    "TeacherBlueprint",
    "TeacherStep",
    "Theme",
    "WEEKS_24",
    "WeekSource",
]
