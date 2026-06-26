"""Curriculum-relative time periods for the stats dashboard.

The stats page measures progress against the learner's *curriculum* calendar
(week ``N``, day ``D`` of a 24- or 48-week course), not the wall-clock
calendar. This module turns a learner's ``UserCoursePreference`` position into
a concrete set of curriculum ``day_id``s for a requested range
(``week`` / ``month`` / ``all``) plus the goal denominator and the bucket
labels the progression chart needs.

Pure functions only — **no DB, no I/O, no randomness.** The routes layer feeds
the resolved ``day_id`` lists into queries. ``day_id``s are the canonical
``day_{24|48}_{WW}_{DD}`` strings (see
``app.modules.curriculum.file_source``); because every component is
zero-padded, plain lexicographic ordering of two ids that share a course
prefix matches their curriculum order — the history reconstruction relies on
that.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

StatsRange = Literal["week", "month", "all"]

DAYS_PER_WEEK = 7
WEEKS_PER_MONTH = 4

# Largest valid week number per course length.
_MAX_WEEK: dict[str, int] = {"24w": 24, "48w": 48}

# Above this many week-buckets the all-time chart aggregates into 4-week
# blocks so it does not turn into a comb of 24/48 thin columns.
_ALL_MAX_WEEK_BUCKETS = 16


def _course_length(value: str | None) -> str:
    return value if value in _MAX_WEEK else "24w"


def _prefix(course_length: str) -> str:
    return "24" if course_length == "24w" else "48"


def format_day_id(course_length: str, week: int, day: int) -> str:
    """Build the canonical ``day_{24|48}_{WW}_{DD}`` id (day is 1-based)."""
    return f"day_{_prefix(course_length)}_{week:02d}_{day:02d}"


def week_of_day_id(day_id: str) -> int | None:
    """Return the curriculum week encoded in a ``day_id``, or ``None``."""
    parts = (day_id or "").split("_")
    if len(parts) != 4:
        return None
    try:
        return int(parts[2])
    except ValueError:
        return None


def day_of_day_id(day_id: str) -> int | None:
    """Return the 1-based day-in-week encoded in a ``day_id``, or ``None``."""
    parts = (day_id or "").split("_")
    if len(parts) != 4:
        return None
    try:
        return int(parts[3])
    except ValueError:
        return None


def _week_day_ids(course_length: str, week: int) -> list[str]:
    return [format_day_id(course_length, week, d) for d in range(1, DAYS_PER_WEEK + 1)]


def _weeks_day_ids(course_length: str, start_week: int, end_week: int) -> list[str]:
    out: list[str] = []
    for w in range(start_week, end_week + 1):
        out.extend(_week_day_ids(course_length, w))
    return out


@dataclass(frozen=True)
class CurriculumPeriod:
    """A resolved curriculum window for one stats range.

    ``day_ids`` is the full scope used for period KPIs (completed tasks,
    period average score, time practiced). ``comparison_day_ids`` is the
    equivalent previous period used for the "change vs last period" deltas
    (``None`` when there is no prior period). ``bucket_labels`` /
    ``bucket_day_ids`` drive the score-progression chart — one entry per
    x-axis point, in order.
    """

    range: StatsRange
    course_length: str
    tasks_per_day: int
    current_week: int
    current_day: int
    weeks_completed: int
    start_week: int
    end_week: int
    day_ids: list[str]
    comparison_day_ids: list[str] | None
    expected_tasks: int
    bucket_labels: list[str]
    bucket_day_ids: list[list[str]]


def _all_time_buckets(
    course_length: str, weeks: list[int]
) -> tuple[list[str], list[list[str]]]:
    """One bucket per week, or per 4-week block once the course gets long."""
    if len(weeks) <= _ALL_MAX_WEEK_BUCKETS:
        return (
            [f"W{w}" for w in weeks],
            [_week_day_ids(course_length, w) for w in weeks],
        )

    labels: list[str] = []
    day_ids: list[list[str]] = []
    for i in range(0, len(weeks), WEEKS_PER_MONTH):
        block = weeks[i : i + WEEKS_PER_MONTH]
        first, last = block[0], block[-1]
        labels.append(f"W{first}" if first == last else f"W{first}-{last}")
        block_days: list[str] = []
        for w in block:
            block_days.extend(_week_day_ids(course_length, w))
        day_ids.append(block_days)
    return labels, day_ids


def build_period(
    range_: StatsRange,
    *,
    course_length: str,
    tasks_per_day: int,
    current_week: int,
    current_day: int,
) -> CurriculumPeriod:
    """Resolve a range against a learner's curriculum position.

    The week goal is prorated to the in-progress day (``tasks_per_day ×
    current_day``) so the completion ratio reads as "ahead/behind through
    today" rather than against a full-week mountain the learner hasn't reached
    yet. The month goal is ``× 28`` and all-time prorates to the number of
    weeks the learner has reached.
    """
    course_length = _course_length(course_length)
    max_week = _MAX_WEEK[course_length]
    current_week = max(1, min(int(current_week), max_week))
    current_day = max(1, min(int(current_day), DAYS_PER_WEEK))
    tpd = max(1, int(tasks_per_day))
    # Weeks fully behind the learner (the in-progress current week excluded).
    weeks_completed = current_week - 1

    if range_ == "week":
        start = end = current_week
        day_ids = _week_day_ids(course_length, current_week)
        comparison = (
            _week_day_ids(course_length, current_week - 1) if current_week > 1 else None
        )
        # Prorate to the in-progress day so completion reads as pace-to-date.
        expected = tpd * current_day
        labels = [f"D{d}" for d in range(1, DAYS_PER_WEEK + 1)]
        bucket_day_ids = [
            [format_day_id(course_length, current_week, d)]
            for d in range(1, DAYS_PER_WEEK + 1)
        ]

    elif range_ == "month":
        start = ((current_week - 1) // WEEKS_PER_MONTH) * WEEKS_PER_MONTH + 1
        end = min(start + WEEKS_PER_MONTH - 1, max_week)
        day_ids = _weeks_day_ids(course_length, start, end)
        prev_start = start - WEEKS_PER_MONTH
        comparison = (
            _weeks_day_ids(course_length, prev_start, start - 1)
            if prev_start >= 1
            else None
        )
        expected = tpd * DAYS_PER_WEEK * WEEKS_PER_MONTH
        labels = [f"W{w}" for w in range(start, end + 1)]
        bucket_day_ids = [
            _week_day_ids(course_length, w) for w in range(start, end + 1)
        ]

    else:  # "all"
        start, end = 1, current_week
        day_ids = _weeks_day_ids(course_length, start, end)
        comparison = _week_day_ids(course_length, 1) if current_week > 1 else None
        expected = tpd * DAYS_PER_WEEK * current_week
        labels, bucket_day_ids = _all_time_buckets(
            course_length, list(range(1, current_week + 1))
        )

    return CurriculumPeriod(
        range=range_,
        course_length=course_length,
        tasks_per_day=tpd,
        current_week=current_week,
        current_day=current_day,
        weeks_completed=weeks_completed,
        start_week=start,
        end_week=end,
        day_ids=day_ids,
        comparison_day_ids=comparison,
        expected_tasks=expected,
        bucket_labels=labels,
        bucket_day_ids=bucket_day_ids,
    )
