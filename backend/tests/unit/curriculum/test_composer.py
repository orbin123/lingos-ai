"""Unit tests for level-band curriculum composer."""

from __future__ import annotations

import pytest

from app.modules.curriculum.data.composer import compose_weeks, resolve_day
from app.scoring import CourseLength


@pytest.mark.parametrize(
    ("calendar_week", "expected_band", "expected_source_week"),
    [
        (1, "A1A2", 1),
        (8, "A1A2", 8),
        (9, "B1B2", 1),
        (16, "B1B2", 8),
        (17, "C1C2", 1),
        (24, "C1C2", 8),
    ],
)
def test_24w_band_and_source_week_mapping(
    calendar_week: int,
    expected_band: str,
    expected_source_week: int,
) -> None:
    resolved = resolve_day(CourseLength.WEEKS_24, calendar_week, 0)
    assert resolved.band == expected_band
    assert resolved.source_week == expected_source_week
    assert resolved.pass_index == 0
    assert resolved.source_day == 0


@pytest.mark.parametrize(
    ("calendar_week", "day_index", "expected_pass", "expected_cefr"),
    [
        (1, 0, 0, "A1"),
        (1, 1, 1, "A2"),
        (1, 2, 0, "A1"),
        (2, 0, 1, "A2"),  # calendar week 2 opens source week 1 depth pass
        (9, 0, 0, "A2"),  # A1A2 source week 5 base pass
        (17, 0, 0, "B1"),
        (17, 1, 1, "B2"),
        (33, 0, 0, "C1"),
        (33, 1, 1, "C2"),
    ],
)
def test_48w_pass_index_and_level_pairing(
    calendar_week: int,
    day_index: int,
    expected_pass: int,
    expected_cefr: str,
) -> None:
    resolved = resolve_day(CourseLength.WEEKS_48, calendar_week, day_index)
    assert resolved.pass_index == expected_pass
    assert resolved.cefr_level == expected_cefr


def test_48w_source_week_doubles_every_two_calendar_weeks() -> None:
    w1d0 = resolve_day(CourseLength.WEEKS_48, 1, 0)
    w2d0 = resolve_day(CourseLength.WEEKS_48, 2, 0)
    assert (w1d0.source_week, w1d0.source_day) == (1, 0)
    assert (w2d0.source_week, w2d0.source_day) == (1, 3)


def test_compose_weeks_24w_has_populated_first_day() -> None:
    weeks = compose_weeks(CourseLength.WEEKS_24)
    assert len(weeks) == 24
    assert weeks[0].days[0].title.startswith("Simple Present Tense")


def test_compose_weeks_48w_first_depth_pass_uses_depth_day() -> None:
    weeks = compose_weeks(CourseLength.WEEKS_48)
    assert len(weeks) == 48
    base = weeks[0].days[0]
    depth = weeks[0].days[1]
    assert base.title
    assert depth.title != base.title
    assert "Questions" in depth.title or "Negatives" in depth.title
    assert weeks[0].cefr_level == "A1"
    assert weeks[1].cefr_level == "A2"


def test_24w_cefr_steps_six_bands() -> None:
    weeks = compose_weeks(CourseLength.WEEKS_24)
    expected = (
        ["A1"] * 4
        + ["A2"] * 4
        + ["B1"] * 4
        + ["B2"] * 4
        + ["C1"] * 4
        + ["C2"] * 4
    )
    assert [w.cefr_level for w in weeks] == expected
