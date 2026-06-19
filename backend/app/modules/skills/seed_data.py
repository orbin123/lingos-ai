"""Canonical seed data for the `skills` master table.

This is the single source of truth for the 7 sub-skill rows that MUST exist in
every environment. The Alembic seed migration, the operational
`scripts/seed_curriculum.py` seeder, and the regression test all consume this
list so the three can never drift.

`name` matches `app.scoring.SUB_SKILLS` (the legacy identifiers used everywhere
in code and DB). `display_label` matches the user-facing labels backfilled by
migration `f1a2b3c4d567_skill_display_labels`. `description` mirrors the name,
matching how tests/factories have always seeded these rows.
"""

from __future__ import annotations

from app.scoring import SUB_SKILLS

# name → user-facing display label (see f1a2b3c4d567._LABELS / RESTRUCTURE_DECISIONS.md §2).
_DISPLAY_LABELS: dict[str, str] = {
    "grammar": "Grammar",
    "vocabulary": "Vocabulary",
    "pronunciation": "Pronunciation",
    "fluency": "Fluency",
    "expression": "Thought Organization",
    "comprehension": "Listening",
    "tone": "Tone & Social",
}


# (name, description, display_label) tuples, ordered by SUB_SKILLS. Building from
# SUB_SKILLS guarantees a KeyError here at import time if a new sub-skill is added
# without a label — surfacing the gap loudly instead of shipping a half-seeded table.
SKILL_SEED: tuple[tuple[str, str, str], ...] = tuple(
    (name, name, _DISPLAY_LABELS[name]) for name in SUB_SKILLS
)
