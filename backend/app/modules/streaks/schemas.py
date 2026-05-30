"""Pydantic schemas for the streak API."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

StreakState = Literal[
    "NO_STREAK_YET",
    "FIRST_STREAK_EARNED",
    "STREAK_ALREADY_COMPLETED_TODAY",
    "STREAK_CONTINUED",
    "STREAK_FROZEN",
    "STREAK_RESET",
    "INACTIVE_TODAY",
]

StreakStatus = Literal["new", "active", "frozen", "broken"]

AnimationType = Literal["rekindle", "on_fire", "frozen_to_fire", "frozen"]


class ActivityGridCell(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD in user's local timezone")
    activity_count: int
    completed: bool
    intensity: int = Field(..., ge=0, le=4)
    frozen_protected: bool


class StreakDataResponse(BaseModel):
    current_streak: int
    longest_streak: int
    freezes_remaining: int
    today_complete: bool
    today_streak_awarded: bool
    last_activity_date: date | None
    last_streak_date: date | None
    streak_status: StreakStatus
    streak_state_for_ui: StreakState
    should_show_animation: bool
    animation_type: AnimationType | None
    activity_grid: list[ActivityGridCell]
    timezone: str
