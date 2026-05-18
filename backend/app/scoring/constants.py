"""Locked numerical constants for the scoring engine.

These values are the contract. Never inline them, never duplicate them, and
never let an LLM compute them. Changes require:
  1. A documented update in RESTRUCTURE_DECISIONS.md
  2. A new Alembic migration if any DB-backed defaults need to follow
  3. Updated unit tests covering the new values

Sub-skill identifiers are the LEGACY names (matching the live `skills` table).
The restructuring doc uses friendlier names — see SUB_SKILL_ALIASES.
"""

from enum import Enum
from typing import Final


# ── Sub-skills ──────────────────────────────────────────────────────

SUB_SKILLS: Final[tuple[str, ...]] = (
    "grammar",
    "vocabulary",
    "pronunciation",
    "fluency",
    "expression",        # doc calls this "thought_org"
    "comprehension",     # doc calls this "listening"
    "tone",              # doc calls this "tone_social"
)

# Doc → legacy code mapping. Use only at the doc/code boundary; never store
# a doc name in DB rows or downstream code logic.
SUB_SKILL_ALIASES: Final[dict[str, str]] = {
    "thought_org": "expression",
    "listening": "comprehension",
    "tone_social": "tone",
}


# ── Course length ──────────────────────────────────────────────────


class CourseLength(str, Enum):
    """24-week or 48-week curriculum. Determines per-activity reward size."""

    WEEKS_24 = "24w"
    WEEKS_48 = "48w"


# ── Performance tiers ──────────────────────────────────────────────


class Tier(str, Enum):
    """Performance bucket for a single activity's raw_score."""

    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    VERY_POOR = "very_poor"


# Inclusive low bound for each tier. `tier_for_score` walks highest-first and
# returns the first tier whose bound is <= score. Exactly 8.0 → Excellent,
# 6.0 → Good, 4.0 → Average, 2.0 → Poor (boundary inclusive on low side).
TIER_BOUNDARIES: Final[dict[Tier, float]] = {
    Tier.EXCELLENT: 8.0,
    Tier.GOOD: 6.0,
    Tier.AVERAGE: 4.0,
    Tier.POOR: 2.0,
    Tier.VERY_POOR: 0.0,
}


# ── Reward tables ──────────────────────────────────────────────────

REWARDS_24W: Final[dict[Tier, int]] = {
    Tier.EXCELLENT: 55,
    Tier.GOOD: 40,
    Tier.AVERAGE: 24,
    Tier.POOR: 10,
    Tier.VERY_POOR: 0,
}

REWARDS_48W: Final[dict[Tier, int]] = {
    Tier.EXCELLENT: 28,
    Tier.GOOD: 20,
    Tier.AVERAGE: 12,
    Tier.POOR: 5,
    Tier.VERY_POOR: 0,
}


# ── Dashboard / caps ───────────────────────────────────────────────

POINTS_PER_DASHBOARD_UNIT: Final[int] = 1000   # 1000 internal pts = 1.0 visible
MAX_POINTS_PER_SUBSKILL: Final[int] = 10000    # display caps at 10.0/10


# ── Validation tolerance ───────────────────────────────────────────

# Floating-point weights in archetype maps must sum to 1.0 within this slack.
ARCHETYPE_WEIGHT_TOLERANCE: Final[float] = 1e-6


# ── Raw score range ────────────────────────────────────────────────

MIN_RAW_SCORE: Final[float] = 0.0
MAX_RAW_SCORE: Final[float] = 10.0
