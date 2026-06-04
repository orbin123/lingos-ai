"""Backward-compat shim: composed 48-week calendar view."""

from __future__ import annotations

from app.modules.curriculum.data.composer import compose_weeks
from app.modules.curriculum.data.types import WeekSource
from app.scoring import CourseLength

WEEKS_48: tuple[WeekSource, ...] = compose_weeks(CourseLength.WEEKS_48)

__all__ = ["WEEKS_48", "WeekSource"]
