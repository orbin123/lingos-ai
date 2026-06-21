"""Deterministic scoring engine — pure code, no LLM, no DB.

Public API:
  - `tier_for_score(score)`           bucket a 0–10 raw_score into a Tier.
  - `base_reward(score, course)`      points for one activity (24w or 48w).
  - `distribute(reward, weight_map)`  split reward across sub-skills.
  - `aggregate_session(activities)`   sum per-activity distributions, round once.
  - `apply_to_totals(earned, current)` cap totals at MAX_POINTS_PER_SUBSKILL.
  - `points_to_dashboard(total)`      convert capped points to 0.0–10.0 display.
  - `build_session_aggregation(...)`  one-call wrapper returning a SessionAggregation.
  - `ARCHETYPE_REGISTRY`              archetype lookup by id.

Read `app/scoring/constants.py` for the locked numerical constants.
Read `RESTRUCTURE_DECISIONS.md` for the rationale behind those numbers.
"""

from app.scoring.archetypes import (
    ARCHETYPE_REGISTRY,
    get_archetype,
    list_mvp_archetypes,
    speaking_archetype_ids,
)
from app.scoring.constants import (
    ARCHETYPE_WEIGHT_TOLERANCE,
    MAX_POINTS_PER_SUBSKILL,
    MAX_RAW_SCORE,
    MIN_RAW_SCORE,
    POINTS_PER_DASHBOARD_UNIT,
    REWARDS_24W,
    REWARDS_48W,
    SUB_SKILLS,
    SUB_SKILL_ALIASES,
    TIER_BOUNDARIES,
    CourseLength,
    Tier,
)
from app.scoring.engine import (
    aggregate_session,
    apply_to_totals,
    base_reward,
    build_session_aggregation,
    distribute,
    points_to_dashboard,
    tier_for_score,
)
from app.scoring.types import (
    ActivityScore,
    ArchetypeSpec,
    CoreActivity,
    SessionAggregation,
)

__all__ = [
    "ARCHETYPE_REGISTRY",
    "ARCHETYPE_WEIGHT_TOLERANCE",
    "ActivityScore",
    "ArchetypeSpec",
    "CoreActivity",
    "CourseLength",
    "MAX_POINTS_PER_SUBSKILL",
    "MAX_RAW_SCORE",
    "MIN_RAW_SCORE",
    "POINTS_PER_DASHBOARD_UNIT",
    "REWARDS_24W",
    "REWARDS_48W",
    "SUB_SKILLS",
    "SUB_SKILL_ALIASES",
    "SessionAggregation",
    "TIER_BOUNDARIES",
    "Tier",
    "aggregate_session",
    "apply_to_totals",
    "base_reward",
    "build_session_aggregation",
    "distribute",
    "get_archetype",
    "list_mvp_archetypes",
    "points_to_dashboard",
    "speaking_archetype_ids",
    "tier_for_score",
]
