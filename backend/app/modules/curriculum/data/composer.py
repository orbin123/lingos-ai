"""Compose calendar-facing curriculum weeks from level-band source files.

Three band modules each hold 8 canonical source weeks. This module maps
24w (one day per topic) and 48w (two consecutive days per topic with level
pairing) onto those bands at runtime.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace

from app.modules.curriculum.data.source_L_A1A2 import WEEKS_A1A2
from app.modules.curriculum.data.source_L_B1B2 import WEEKS_B1B2
from app.modules.curriculum.data.source_L_C1C2 import WEEKS_C1C2
from app.modules.curriculum.data.types import DaySource, LevelBand, Theme, WeekSource
from app.scoring import CourseLength

logger = logging.getLogger(__name__)

BAND_WEEKS: dict[LevelBand, tuple[WeekSource, ...]] = {
    "A1A2": WEEKS_A1A2,
    "B1B2": WEEKS_B1B2,
    "C1C2": WEEKS_C1C2,
}

BAND_START_48: dict[LevelBand, int] = {
    "A1A2": 1,
    "B1B2": 17,
    "C1C2": 33,
}

SUB_LEVELS: dict[str, tuple[int, int]] = {
    "A1": (1, 2),
    "A2": (3, 3),
    "B1": (4, 5),
    "B2": (6, 7),
    "C1": (8, 8),
    "C2": (8, 8),
}

MAX_CALENDAR_WEEKS: dict[CourseLength, int] = {
    CourseLength.WEEKS_24: 24,
    CourseLength.WEEKS_48: 48,
}


@dataclass(frozen=True)
class ResolvedDay:
    calendar_week: int
    day_index: int
    band: LevelBand
    source_week: int
    source_day: int
    pass_index: int
    cefr_level: str
    sub_level_min: int
    sub_level_max: int
    day: DaySource
    theme_type: Theme
    week_title: str
    learning_goal: str


def _band_for_calendar_week_24(calendar_week: int) -> tuple[LevelBand, int]:
    if not 1 <= calendar_week <= 24:
        raise ValueError(f"calendar_week={calendar_week} out of range for 24w")
    if calendar_week <= 8:
        return "A1A2", calendar_week
    if calendar_week <= 16:
        return "B1B2", calendar_week - 8
    return "C1C2", calendar_week - 16


def _band_for_calendar_week_48(calendar_week: int) -> LevelBand:
    if not 1 <= calendar_week <= 48:
        raise ValueError(f"calendar_week={calendar_week} out of range for 48w")
    if calendar_week <= 16:
        return "A1A2"
    if calendar_week <= 32:
        return "B1B2"
    return "C1C2"


def _cefr_for_24w(band: LevelBand, source_week: int) -> str:
    lower = {"A1A2": "A1", "B1B2": "B1", "C1C2": "C1"}[band]
    upper = {"A1A2": "A2", "B1B2": "B2", "C1C2": "C2"}[band]
    return lower if source_week <= 4 else upper


def _cefr_for_48w(band: LevelBand, source_week: int, pass_index: int) -> str:
    if source_week <= 4:
        if pass_index == 0:
            return {"A1A2": "A1", "B1B2": "B1", "C1C2": "C1"}[band]
        return {"A1A2": "A2", "B1B2": "B2", "C1C2": "C2"}[band]
    return {"A1A2": "A2", "B1B2": "B2", "C1C2": "C2"}[band]


def _48w_coordinates(
    calendar_week: int,
    day_index: int,
    band: LevelBand,
) -> tuple[int, int, int]:
    band_start = BAND_START_48[band]
    linear = (calendar_week - band_start) * 7 + day_index
    source_week = linear // 14 + 1
    within = linear % 14
    source_day = within // 2
    pass_index = within % 2
    return source_week, source_day, pass_index


def _get_band_week(band: LevelBand, source_week: int) -> WeekSource:
    weeks = BAND_WEEKS[band]
    for week in weeks:
        if week.week_number == source_week:
            return week
    raise ValueError(
        f"source_week={source_week} not found in band {band} (has {len(weeks)} weeks)"
    )


def _resolve_day_content(base_day: DaySource, pass_index: int) -> DaySource:
    if pass_index == 0:
        return base_day
    if base_day.depth_day is not None:
        return base_day.depth_day
    logger.debug(
        "depth_day missing for %r; falling back to base day content",
        base_day.title,
    )
    return base_day


def resolve_day(
    course_length: CourseLength,
    calendar_week: int,
    day_index: int,
) -> ResolvedDay:
    """Resolve one calendar day to band-local content and CEFR metadata."""
    if not 0 <= day_index <= 6:
        raise ValueError(f"day_index={day_index} out of range (expected 0..6)")

    if course_length is CourseLength.WEEKS_24:
        band, source_week = _band_for_calendar_week_24(calendar_week)
        source_day = day_index
        pass_index = 0
        cefr_level = _cefr_for_24w(band, source_week)
    else:
        band = _band_for_calendar_week_48(calendar_week)
        source_week, source_day, pass_index = _48w_coordinates(
            calendar_week, day_index, band
        )
        cefr_level = _cefr_for_48w(band, source_week, pass_index)

    week = _get_band_week(band, source_week)
    if not 0 <= source_day < len(week.days):
        raise ValueError(
            f"source_day={source_day} out of range for band {band} week {source_week}"
        )

    base_day = week.days[source_day]
    day = _resolve_day_content(base_day, pass_index)
    sub_min, sub_max = SUB_LEVELS[cefr_level]

    return ResolvedDay(
        calendar_week=calendar_week,
        day_index=day_index,
        band=band,
        source_week=source_week,
        source_day=source_day,
        pass_index=pass_index,
        cefr_level=cefr_level,
        sub_level_min=sub_min,
        sub_level_max=sub_max,
        day=day,
        theme_type=week.theme_type,
        week_title=week.title,
        learning_goal=week.learning_goal,
    )


def compose_weeks(course_length: CourseLength) -> tuple[WeekSource, ...]:
    """Build calendar-facing WeekSource rows for seeding and hydration."""
    max_week = MAX_CALENDAR_WEEKS[course_length]
    composed: list[WeekSource] = []

    for calendar_week in range(1, max_week + 1):
        resolved_days = tuple(
            resolve_day(course_length, calendar_week, day_index)
            for day_index in range(7)
        )
        first = resolved_days[0]
        composed.append(
            WeekSource(
                week_number=calendar_week,
                theme_type=first.theme_type,
                cefr_level=first.cefr_level,
                sub_level_min=first.sub_level_min,
                sub_level_max=first.sub_level_max,
                days=tuple(r.day for r in resolved_days),
                title=first.week_title,
                learning_goal=first.learning_goal,
            )
        )

    return tuple(composed)


def week_source_from_resolved(resolved: ResolvedDay) -> WeekSource:
    """Build a WeekSource shell for blueprint adaptation."""
    week = _get_band_week(resolved.band, resolved.source_week)
    return replace(
        week,
        week_number=resolved.calendar_week,
        cefr_level=resolved.cefr_level,
        sub_level_min=resolved.sub_level_min,
        sub_level_max=resolved.sub_level_max,
    )
