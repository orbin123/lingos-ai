"""Pure-data tests for the v2 curriculum loader.

No DB. Validates the shape and integrity of the in-memory curriculum
records: cycle pattern, theme rotation, ID format, archetype coverage.
"""

from __future__ import annotations

import re

import pytest

from app.modules.curriculum.data import load_weeks
from app.modules.curriculum.data.loader import (
    DayRecord,
    WeekRecord,
    _CANDIDATES_BY_THEME,
    _MANDATORY_BY_THEME,
)
from app.scoring import ARCHETYPE_REGISTRY, CourseLength, get_archetype


_THEME_CYCLE = ("grammar", "communication", "vocabulary", "confidence")

# Expected CEFR per 24w calendar week (6 bands × 4 weeks).
_CYCLE_CEFR = ("A1", "A2", "B1", "B2", "C1", "C2")

_WEEK_ID_PATTERN_24 = re.compile(r"^wk_24_\d{2}$")
_WEEK_ID_PATTERN_48 = re.compile(r"^wk_48_\d{2}$")
_DAY_ID_PATTERN_24 = re.compile(r"^day_24_\d{2}_\d{2}$")
_DAY_ID_PATTERN_48 = re.compile(r"^day_48_\d{2}_\d{2}$")


# ── Counts ─────────────────────────────────────────────────────────


def test_24w_has_24_weeks_and_168_days():
    weeks = load_weeks(CourseLength.WEEKS_24)
    assert len(weeks) == 24
    assert sum(len(w.days) for w in weeks) == 168


def test_48w_has_48_weeks_and_336_days():
    weeks = load_weeks(CourseLength.WEEKS_48)
    assert len(weeks) == 48
    assert sum(len(w.days) for w in weeks) == 336


@pytest.mark.parametrize(
    "course_length", [CourseLength.WEEKS_24, CourseLength.WEEKS_48]
)
def test_every_week_has_exactly_seven_days(course_length):
    for week in load_weeks(course_length):
        assert len(week.days) == 7, f"{week.week_id} has {len(week.days)} days"


# ── Theme rotation ─────────────────────────────────────────────────


def test_24w_theme_rotation_follows_4_week_cycle():
    weeks = load_weeks(CourseLength.WEEKS_24)
    for idx, week in enumerate(weeks):
        expected = _THEME_CYCLE[idx % 4]
        assert week.theme_type == expected, (
            f"week {week.week_number} should be {expected}, got {week.theme_type}"
        )


def test_24w_cefr_steps_one_band_per_cycle():
    weeks = load_weeks(CourseLength.WEEKS_24)
    for idx, week in enumerate(weeks):
        cycle_index = idx // 4
        expected = _CYCLE_CEFR[cycle_index]
        assert week.cefr_level == expected, (
            f"week {week.week_number} should be CEFR {expected}, got {week.cefr_level}"
        )


def test_48w_theme_rotation_follows_source_week_pairs():
    """48w rotates themes every two calendar weeks (one source week = 14 days)."""
    weeks = load_weeks(CourseLength.WEEKS_48)
    for week in weeks:
        expected = _THEME_CYCLE[(week.week_number - 1) // 2 % 4]
        assert week.theme_type == expected, (
            f"week {week.week_number} should be {expected}, got {week.theme_type}"
        )


def test_48w_cefr_follows_level_pairing_bands() -> None:
    """48w uses six level bands across 48 calendar weeks."""
    weeks = load_weeks(CourseLength.WEEKS_48)
    # A1A2 band weeks 1-16: week metadata uses first calendar day of the week
    assert weeks[0].cefr_level == "A1"
    assert weeks[1].cefr_level == "A2"
    # B1B2 band starts at calendar week 17
    assert weeks[16].cefr_level == "B1"
    assert weeks[17].cefr_level == "B2"
    # C1C2 band starts at calendar week 33
    assert weeks[32].cefr_level == "C1"
    assert weeks[33].cefr_level == "C2"


def test_48w_days_have_populated_topics_from_composed_bands() -> None:
    weeks = load_weeks(CourseLength.WEEKS_48)
    assert weeks[0].days[0].topic.startswith("Simple Present Tense")
    assert weeks[0].days[1].topic.startswith("Simple Present")
    assert weeks[0].days[1].topic != weeks[0].days[0].topic


# ── ID format and uniqueness ───────────────────────────────────────


def test_24w_week_ids_match_pattern_and_are_unique():
    weeks = load_weeks(CourseLength.WEEKS_24)
    week_ids = [w.week_id for w in weeks]
    assert len(set(week_ids)) == len(week_ids)
    for w in weeks:
        assert _WEEK_ID_PATTERN_24.match(w.week_id), w.week_id


def test_48w_week_ids_match_pattern_and_are_unique():
    weeks = load_weeks(CourseLength.WEEKS_48)
    week_ids = [w.week_id for w in weeks]
    assert len(set(week_ids)) == len(week_ids)
    for w in weeks:
        assert _WEEK_ID_PATTERN_48.match(w.week_id), w.week_id


def test_24w_day_ids_match_pattern_and_are_unique():
    weeks = load_weeks(CourseLength.WEEKS_24)
    day_ids = [d.day_id for w in weeks for d in w.days]
    assert len(set(day_ids)) == len(day_ids) == 168
    for did in day_ids:
        assert _DAY_ID_PATTERN_24.match(did), did


def test_48w_day_ids_match_pattern_and_are_unique():
    weeks = load_weeks(CourseLength.WEEKS_48)
    day_ids = [d.day_id for w in weeks for d in w.days]
    assert len(set(day_ids)) == len(day_ids) == 336
    for did in day_ids:
        assert _DAY_ID_PATTERN_48.match(did), did


# ── Activity invariants ────────────────────────────────────────────


@pytest.mark.parametrize(
    "course_length", [CourseLength.WEEKS_24, CourseLength.WEEKS_48]
)
def test_mandatory_activities_are_subset_of_default(course_length):
    for week in load_weeks(course_length):
        for day in week.days:
            assert set(day.mandatory_activities).issubset(day.default_activities), (
                f"{day.day_id}: mandatory not a subset of default"
            )


@pytest.mark.parametrize(
    "course_length", [CourseLength.WEEKS_24, CourseLength.WEEKS_48]
)
def test_every_mandatory_activity_has_at_least_one_archetype(course_length):
    for week in load_weeks(course_length):
        for day in week.days:
            for activity in day.mandatory_activities:
                suggestions = day.suggested_archetypes.get(activity, ())
                assert suggestions, (
                    f"{day.day_id} mandatory {activity!r} has no suggested archetypes "
                    f"(week CEFR {week.cefr_level}, theme {week.theme_type})"
                )


@pytest.mark.parametrize(
    "course_length", [CourseLength.WEEKS_24, CourseLength.WEEKS_48]
)
def test_all_suggested_archetype_ids_exist(course_length):
    for week in load_weeks(course_length):
        for day in week.days:
            for activity, archetypes in day.suggested_archetypes.items():
                for aid in archetypes:
                    assert aid in ARCHETYPE_REGISTRY, (
                        f"{day.day_id} suggests unknown archetype {aid!r}"
                    )


@pytest.mark.parametrize(
    "course_length", [CourseLength.WEEKS_24, CourseLength.WEEKS_48]
)
def test_suggested_archetypes_match_their_activity(course_length):
    for week in load_weeks(course_length):
        for day in week.days:
            for activity, archetypes in day.suggested_archetypes.items():
                for aid in archetypes:
                    spec = get_archetype(aid)
                    assert spec.core_activity == activity, (
                        f"{day.day_id} suggests {aid!r} under activity {activity!r} "
                        f"but archetype core_activity is {spec.core_activity!r}"
                    )


# ── CEFR sanity ────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "course_length", [CourseLength.WEEKS_24, CourseLength.WEEKS_48]
)
def test_sub_level_range_is_within_1_to_10(course_length):
    for week in load_weeks(course_length):
        assert 1 <= week.sub_level_min <= week.sub_level_max <= 10, (
            f"{week.week_id} sub_level_range {week.sub_level_min}-{week.sub_level_max}"
        )


# ── Static helper sanity (catches loader pool typos) ───────────────


def test_candidate_pool_keys_match_theme_keys():
    assert set(_CANDIDATES_BY_THEME) == set(_MANDATORY_BY_THEME)


def test_every_theme_pool_covers_four_activities():
    for theme, by_activity in _CANDIDATES_BY_THEME.items():
        assert set(by_activity) == {"read", "write", "listen", "speak"}, theme


def test_every_pool_archetype_id_is_in_registry():
    for theme, by_activity in _CANDIDATES_BY_THEME.items():
        for activity, ids in by_activity.items():
            for aid in ids:
                assert aid in ARCHETYPE_REGISTRY, (
                    f"theme {theme!r} activity {activity!r}: unknown archetype {aid!r}"
                )


# ── Type sanity (catches accidental WeekRecord/DayRecord drift) ────


def test_load_weeks_returns_week_records_with_day_records():
    weeks = load_weeks(CourseLength.WEEKS_24)
    assert all(isinstance(w, WeekRecord) for w in weeks)
    assert all(isinstance(d, DayRecord) for w in weeks for d in w.days)
