"""Pydantic models for the scoring engine — pure data shapes, no behavior."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.scoring.constants import (
    ARCHETYPE_WEIGHT_TOLERANCE,
    MAX_RAW_SCORE,
    MIN_RAW_SCORE,
    SUB_SKILLS,
)


CoreActivity = Literal["read", "write", "listen", "speak"]


class ArchetypeSpec(BaseModel):
    """Static definition of one task archetype.

    Lives in `app.scoring.archetypes.ARCHETYPE_REGISTRY` and is read by the
    scoring engine to distribute an activity's earned points across sub-skills.
    """

    model_config = ConfigDict(frozen=True)

    archetype_id: str
    name: str
    core_activity: CoreActivity
    description: str
    ui_widget: str
    themes_supported: tuple[str, ...]
    cefr_min: str
    cefr_max: str
    weight_map: dict[str, float]
    rubric: tuple[str, ...]
    mvp: bool = True

    @field_validator("weight_map")
    @classmethod
    def _weights_sum_to_one(cls, v: dict[str, float]) -> dict[str, float]:
        total = sum(v.values())
        if abs(total - 1.0) > ARCHETYPE_WEIGHT_TOLERANCE:
            raise ValueError(
                f"weight_map sums to {total} (must be 1.0 ±{ARCHETYPE_WEIGHT_TOLERANCE})"
            )
        unknown = set(v) - set(SUB_SKILLS)
        if unknown:
            raise ValueError(f"unknown sub-skills in weight_map: {sorted(unknown)}")
        for skill, weight in v.items():
            if weight <= 0:
                raise ValueError(f"weight for {skill!r} must be > 0, got {weight}")
        return v


class ActivityScore(BaseModel):
    """One activity's outcome, the input to per-session aggregation.

    Built by `sessions/service.py` from an `ActivityEvaluation` row plus the
    matching `ArchetypeSpec` weight_map.
    """

    model_config = ConfigDict(frozen=True)

    archetype_id: str
    raw_score: float = Field(ge=MIN_RAW_SCORE, le=MAX_RAW_SCORE)
    weight_map: dict[str, float]

    @field_validator("weight_map")
    @classmethod
    def _validate(cls, v: dict[str, float]) -> dict[str, float]:
        total = sum(v.values())
        if abs(total - 1.0) > ARCHETYPE_WEIGHT_TOLERANCE:
            raise ValueError(f"weight_map sums to {total} (must be 1.0)")
        return v


class SessionAggregation(BaseModel):
    """Result of aggregating one session's activities into per-sub-skill points.

    `points_earned` is the uncapped delta the user actually earned — used for
    the "+N pts" notification. `subskill_totals_after` applies the cap at
    MAX_POINTS_PER_SUBSKILL. `dashboard_after` is the 0.0–10.0 display value.
    """

    model_config = ConfigDict(frozen=True)

    points_earned: dict[str, int]
    subskill_totals_after: dict[str, int] | None = None
    dashboard_after: dict[str, float] | None = None
