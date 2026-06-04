"""Curriculum v2 — week / day / archetype data for the restructured flow.

Three level-band source modules (`source_L_A1A2`, `source_L_B1B2`,
`source_L_C1C2`) hold 8 canonical weeks each. ``composer.compose_weeks()``
assembles 24w and 48w calendar views at runtime.

Consumers should call ``loader.load_weeks(course_length)`` rather than
importing the source modules directly — the loader returns the fully
hydrated structure (week_id, day_id, mandatory_activities,
suggested_archetypes) that the seeder writes to the database.
"""

from app.modules.curriculum.data.loader import load_weeks

__all__ = ["load_weeks"]
