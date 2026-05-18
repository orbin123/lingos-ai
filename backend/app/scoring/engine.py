"""Pure functions implementing the scoring math.

No DB calls. No I/O. No randomness. Same inputs → same outputs.
Math derived from RESTRUCTURE_DECISIONS.md (§1–§3) and the restructure spec.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from app.scoring.constants import (
    ARCHETYPE_WEIGHT_TOLERANCE,
    MAX_POINTS_PER_SUBSKILL,
    POINTS_PER_DASHBOARD_UNIT,
    REWARDS_24W,
    REWARDS_48W,
    TIER_BOUNDARIES,
    CourseLength,
    Tier,
)
from app.scoring.types import ActivityScore, SessionAggregation

# Highest-first walk so the inclusive-low boundary rule works in one pass:
# 8.0 → Excellent, 6.0 → Good, 4.0 → Average, 2.0 → Poor.
_TIERS_HIGH_TO_LOW: list[tuple[Tier, float]] = sorted(
    TIER_BOUNDARIES.items(), key=lambda kv: kv[1], reverse=True
)


def tier_for_score(score: float) -> Tier:
    """Return the tier a 0–10 raw_score falls into.

    Boundary rule: each tier's `>= boundary` wins, walking highest first.
    Exactly 4.0 → Average, 6.0 → Good, 8.0 → Excellent.
    """
    for tier, lower_bound in _TIERS_HIGH_TO_LOW:
        if score >= lower_bound:
            return tier
    return Tier.VERY_POOR  # unreachable while VERY_POOR boundary is 0.0


def base_reward(score: float, course_length: CourseLength) -> int:
    """Return the per-activity base reward in points."""
    tier = tier_for_score(score)
    table = REWARDS_24W if course_length is CourseLength.WEEKS_24 else REWARDS_48W
    return table[tier]


def distribute(reward: int, weight_map: dict[str, float]) -> dict[str, float]:
    """Split a single activity's reward across its sub-skills.

    Returns float points per sub-skill. Rounding is deferred to
    `aggregate_session` so cumulative loss doesn't compound across activities.
    """
    total_weight = sum(weight_map.values())
    if abs(total_weight - 1.0) > ARCHETYPE_WEIGHT_TOLERANCE:
        raise ValueError(f"weight_map sums to {total_weight} (must be 1.0)")
    return {skill: reward * weight for skill, weight in weight_map.items()}


def aggregate_session(
    activities: Iterable[ActivityScore],
    course_length: CourseLength,
) -> dict[str, int]:
    """Sum every activity's distributed points, then round per sub-skill.

    Rounding happens once per sub-skill at session end — never per activity —
    so a sub-skill earning three 4.8s gets +14, not +15 (3 × round(4.8) = 15
    would lose precision). See doc §13.3.
    """
    running: dict[str, float] = defaultdict(float)
    for activity in activities:
        reward = base_reward(activity.raw_score, course_length)
        for skill, pts in distribute(reward, activity.weight_map).items():
            running[skill] += pts
    return {skill: round(pts) for skill, pts in running.items()}


def apply_to_totals(
    earned: dict[str, int],
    current_totals: dict[str, int],
) -> dict[str, int]:
    """Add session earnings to existing totals, capped at MAX_POINTS_PER_SUBSKILL.

    The `earned` delta stays uncapped on its way in (so the UI can show
    "+55 pts" even if the user is already at the cap). The returned totals
    are clamped.

    Skills present in `earned` but missing from `current_totals` start at 0.
    Skills in `current_totals` but missing from `earned` are returned
    unchanged.
    """
    new_totals: dict[str, int] = dict(current_totals)
    for skill, delta in earned.items():
        previous = new_totals.get(skill, 0)
        new_totals[skill] = min(previous + delta, MAX_POINTS_PER_SUBSKILL)
    return new_totals


def points_to_dashboard(total_points: int) -> float:
    """Convert capped internal points to a 0.0–10.0 dashboard score.

    1000 points = 1.0 visible. Rounds half-up at one decimal using integer
    arithmetic — avoids Python's banker's rounding plus float-repr quirks
    (e.g. `round(4.155, 1)` can yield 4.1 or 4.2 depending on float repr).
    """
    half_step = POINTS_PER_DASHBOARD_UNIT // 20   # 50 when PPU=1000
    step = POINTS_PER_DASHBOARD_UNIT // 10        # 100 when PPU=1000
    tenths = (total_points + half_step) // step
    return tenths / 10


def build_session_aggregation(
    activities: Iterable[ActivityScore],
    course_length: CourseLength,
    current_totals: dict[str, int] | None = None,
) -> SessionAggregation:
    """Convenience: aggregate + apply caps + compute dashboard in one call.

    If `current_totals` is omitted, only `points_earned` is populated — useful
    for previews and tests that don't care about the absolute totals.
    """
    earned = aggregate_session(activities, course_length)
    if current_totals is None:
        return SessionAggregation(points_earned=earned)
    totals_after = apply_to_totals(earned, current_totals)
    dashboard_after = {
        skill: points_to_dashboard(pts) for skill, pts in totals_after.items()
    }
    return SessionAggregation(
        points_earned=earned,
        subskill_totals_after=totals_after,
        dashboard_after=dashboard_after,
    )
