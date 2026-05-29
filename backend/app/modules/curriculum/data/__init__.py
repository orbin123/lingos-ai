"""Curriculum v2 — week / day / archetype data for the restructured flow.

The 24-week plan is the source of truth (`source_24w.WEEKS_24`). The 48-week
plan is derived from it by `stretch.stretch_to_48w` so a content change in
the 24w plan automatically flows into the 48w plan with the same topics.

Consumers should call `loader.load_weeks(course_length)` rather than
importing the source modules directly — the loader returns the fully
hydrated structure (week_id, day_id, mandatory_activities,
suggested_archetypes) that the seeder writes to the database.
"""

from app.modules.curriculum.data.loader import load_weeks

__all__ = ["load_weeks"]
