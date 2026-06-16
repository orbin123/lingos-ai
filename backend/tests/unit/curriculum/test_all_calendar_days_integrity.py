"""Full-calendar structural lint — all 168 (24w) + 336 (48w) chat session days.

Headless guard so manual QA is only needed when a learner reports a runtime
LLM issue. Failures name the exact ``day_id`` (e.g. ``day_48_12_03``).
"""

from __future__ import annotations

import warnings

import pytest

from app.modules.curriculum import file_source
from app.modules.curriculum.day_lint import (
    lint_day_by_id,
    lint_persona_round_trip,
    lint_static_payloads,
    lint_day_structure,
)
from app.modules.curriculum.data.composer import compose_weeks
from app.scoring import CourseLength


def _build_calendar_cases() -> tuple[
    list[tuple[CourseLength, int, int]],
    list[str],
]:
    cases: list[tuple[CourseLength, int, int]] = []
    ids: list[str] = []
    for course_length in (CourseLength.WEEKS_24, CourseLength.WEEKS_48):
        for week in compose_weeks(course_length):
            for day_index in range(len(week.days)):
                record = file_source.get_day(
                    week.week_number,
                    day_index,
                    course_length=course_length,
                )
                cases.append((course_length, week.week_number, day_index))
                ids.append(record.day_id)
    return cases, ids


CALENDAR_CASES, CALENDAR_IDS = _build_calendar_cases()


def _assert_no_errors(issues, *, day_id: str) -> None:  # noqa: ANN001
    errors = [issue for issue in issues if issue.severity == "error"]
    if not errors:
        for issue in issues:
            if issue.severity == "warning":
                warnings.warn(
                    f"{issue.day_id} [{issue.check}] {issue.message}",
                    stacklevel=2,
                )
        return
    lines = [
        f"{issue.check}: {issue.message}"
        + (
            f" (archetype={issue.archetype_id}, seq={issue.sequence})"
            if issue.archetype_id
            else ""
        )
        for issue in errors
    ]
    pytest.fail(f"{day_id}:\n" + "\n".join(lines))


@pytest.mark.parametrize(
    "course_length,week_number,day_index",
    CALENDAR_CASES,
    ids=CALENDAR_IDS,
)
def test_calendar_day_structure(
    course_length: CourseLength,
    week_number: int,
    day_index: int,
) -> None:
    day = file_source.get_day(
        week_number,
        day_index,
        course_length=course_length,
    )
    _assert_no_errors(lint_day_structure(day), day_id=day.day_id)


@pytest.mark.parametrize(
    "course_length,week_number,day_index",
    CALENDAR_CASES,
    ids=CALENDAR_IDS,
)
def test_calendar_day_persona_round_trip(
    course_length: CourseLength,
    week_number: int,
    day_index: int,
) -> None:
    day = file_source.get_day(
        week_number,
        day_index,
        course_length=course_length,
    )
    _assert_no_errors(lint_persona_round_trip(day), day_id=day.day_id)


@pytest.mark.parametrize(
    "course_length,week_number,day_index",
    CALENDAR_CASES,
    ids=CALENDAR_IDS,
)
def test_calendar_day_static_payloads(
    course_length: CourseLength,
    week_number: int,
    day_index: int,
) -> None:
    day = file_source.get_day(
        week_number,
        day_index,
        course_length=course_length,
    )
    _assert_no_errors(lint_static_payloads(day), day_id=day.day_id)


def test_calendar_inventory_counts() -> None:
    assert len(CALENDAR_CASES) == 168 + 336
    assert len(set(CALENDAR_IDS)) == len(CALENDAR_IDS)


def test_lint_day_by_id_matches_composed_checks() -> None:
    """Sanity: bundled lint covers structure + persona + static payloads."""
    sample = "day_48_01_02"
    issues = lint_day_by_id(sample)
    assert all(issue.day_id == sample for issue in issues)
