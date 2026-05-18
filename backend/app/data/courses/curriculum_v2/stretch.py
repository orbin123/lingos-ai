"""Derive the 48-week plan from the 24-week source.

Each 24w week is replayed twice — first as an 'Intro' week (recognition +
light production), then as an 'Extend' week (integration + confidence). The
day topics are preserved; titles and explanation_briefs gain a phase marker
so the Task Generator can shift difficulty and depth across the pair.
"""

from __future__ import annotations

from app.data.courses.curriculum_v2.source_24w import WeekSource


def stretch_to_48w(weeks_24: tuple[WeekSource, ...]) -> tuple[WeekSource, ...]:
    """Return 48 `WeekSource` rows derived from the 24-week source."""
    out: list[WeekSource] = []
    for src in weeks_24:
        out.append(_phase_variant(src, week_number=2 * src.week_number - 1, phase="Intro"))
        out.append(_phase_variant(src, week_number=2 * src.week_number, phase="Extend"))
    return tuple(out)


def _phase_variant(
    src: WeekSource,
    *,
    week_number: int,
    phase: str,
) -> WeekSource:
    prefix = "Introduce" if phase == "Intro" else "Extend"
    return WeekSource(
        week_number=week_number,
        theme_type=src.theme_type,
        title=f"{src.title} — {phase}",
        cefr_level=src.cefr_level,
        sub_level_min=src.sub_level_min,
        sub_level_max=src.sub_level_max,
        learning_goal=f"{phase}: {src.learning_goal}",
        days=tuple(
            (topic, f"{prefix} — {brief}")
            for (topic, brief) in src.days
        ),
    )
