"""Pydantic schemas for v2 curriculum entities.

These are the read/write shapes for the API layer (Phase 3) plus internal
service-layer plumbing. They mirror the ORM models in `v2_models.py` and the
JSON shape described in the restructure spec §16.1–16.3.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.modules.curriculum.v2_models import CoreActivity, ThemeType


class CurriculumDayRead(BaseModel):
    """API/read shape for a single day record."""

    model_config = ConfigDict(from_attributes=True)

    day_id: str
    day_number: int
    topic: str
    explanation_brief: str
    default_activities: list[str]
    mandatory_activities: list[str]
    suggested_archetypes: dict[str, list[str]]


class CurriculumWeekRead(BaseModel):
    """API/read shape for a week record + its 7 days."""

    model_config = ConfigDict(from_attributes=True)

    week_id: str
    course_length: str
    week_number: int
    theme_type: ThemeType
    title: str
    cefr_level: str
    sub_level_min: int
    sub_level_max: int
    learning_goal: str
    days: list[CurriculumDayRead] = Field(default_factory=list)


class TaskArchetypeRead(BaseModel):
    """API/read shape for an archetype row."""

    model_config = ConfigDict(from_attributes=True)

    archetype_id: str
    name: str
    core_activity: CoreActivity
    description: str
    ui_widget: str
    themes_supported: list[str]
    cefr_min: str
    cefr_max: str
    weight_map: dict[str, float]
    rubric: list[str]
    mvp: bool


# ── Internal seed payloads ─────────────────────────────────────────


class CurriculumWeekSeed(BaseModel):
    """Pre-write payload used by the seeder. Differs from Read by omitting `days`."""

    model_config = ConfigDict(frozen=True)

    week_id: str
    course_length: str
    week_number: int
    theme_type: ThemeType
    title: str
    cefr_level: str
    sub_level_min: int
    sub_level_max: int
    learning_goal: str


class CurriculumDaySeed(BaseModel):
    """Pre-write payload for one day row."""

    model_config = ConfigDict(frozen=True)

    day_id: str
    day_number: int
    topic: str
    explanation_brief: str
    default_activities: list[str]
    mandatory_activities: list[str]
    suggested_archetypes: dict[str, list[str]]


class TaskArchetypeSeed(BaseModel):
    """Pre-write payload for one archetype row, mirrored from the Python registry."""

    model_config = ConfigDict(frozen=True)

    archetype_id: str
    name: str
    core_activity: CoreActivity
    description: str
    ui_widget: str
    themes_supported: list[str]
    cefr_min: str
    cefr_max: str
    weight_map: dict[str, float]
    rubric: list[str]
    mvp: bool
