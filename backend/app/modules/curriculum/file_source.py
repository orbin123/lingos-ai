"""Read curriculum days from composed level-band source data.

Provides the bridge between authored dataclasses in the band source files
and the session services. When a day is file-authored (non-blank), its
archetype order, task specs, teacher instructions, and eval/feedback
overrides take precedence over the DB-seeded curriculum.

Day identity is ``day_<24|48>_<week>_<day>`` where ``day_index`` is 0..6.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from app.modules.curriculum.blueprint_adapter import adapt_day_source
from app.modules.curriculum.data.composer import (
    compose_weeks,
    resolve_day,
    week_source_from_resolved,
)
from app.modules.curriculum.data.types import DaySource, WeekSource
from app.modules.sessions.exceptions import DayNotFound
from app.scoring import ArchetypeSpec, CourseLength, get_archetype


SCRIPTED_PLAN_KEY: str = "__scripted_plan"

_DAY_ID_RE = re.compile(r"^day_(24|48)_(\d{2})_(\d{2})$")

WEEKS_24: tuple[WeekSource, ...] = compose_weeks(CourseLength.WEEKS_24)
WEEKS_48: tuple[WeekSource, ...] = compose_weeks(CourseLength.WEEKS_48)


@dataclass(frozen=True)
class FileDayRecord:
    """Flat per-day record served from composed curriculum source data."""

    day_id: str
    week_number: int
    day_index: int
    day_number: int
    topic: str
    explanation_brief: str
    theme_type: str
    cefr_level: str
    sub_level_min: int
    sub_level_max: int
    task_archetypes_used: tuple[str, ...]
    teacher_agent_behaviour: tuple[str, ...]
    teacher_instructions: dict
    task_specs: tuple[dict, ...]
    activity_contracts: tuple[dict, ...]
    evaluator_overrides: dict
    feedback_overrides: dict
    final_review: dict


def _course_length_from_prefix(prefix: str) -> CourseLength:
    if prefix == "24":
        return CourseLength.WEEKS_24
    if prefix == "48":
        return CourseLength.WEEKS_48
    raise DayNotFound(f"unknown course prefix {prefix!r}")


def _weeks_for(course_length: CourseLength) -> tuple[WeekSource, ...]:
    if course_length is CourseLength.WEEKS_24:
        return WEEKS_24
    return WEEKS_48


def _find_week(course_length: CourseLength, week_number: int) -> WeekSource:
    for week in _weeks_for(course_length):
        if week.week_number == week_number:
            return week
    raise DayNotFound(
        f"week_number={week_number} not in "
        f"{'WEEKS_24' if course_length is CourseLength.WEEKS_24 else 'WEEKS_48'}"
    )


def _day_id(course_length: CourseLength, week_number: int, day_number: int) -> str:
    prefix = "24" if course_length is CourseLength.WEEKS_24 else "48"
    return f"day_{prefix}_{week_number:02d}_{day_number:02d}"


def parse_day_id(day_id: str) -> tuple[CourseLength, int, int]:
    """Parse ``day_24_WW_DD`` or ``day_48_WW_DD`` into course length and numbers."""
    match = _DAY_ID_RE.match(day_id or "")
    if not match:
        raise DayNotFound(f"day_id={day_id!r} is not a file-source day id")
    course_length = _course_length_from_prefix(match.group(1))
    return course_length, int(match.group(2)), int(match.group(3))


def get_day(
    week_number: int,
    day_index: int,
    *,
    course_length: CourseLength = CourseLength.WEEKS_24,
) -> FileDayRecord:
    """Return the day spec at ``(week_number, day_index)`` for ``course_length``."""
    try:
        resolved = resolve_day(course_length, week_number, day_index)
    except ValueError as exc:
        raise DayNotFound(str(exc)) from exc
    week = week_source_from_resolved(resolved)
    day: DaySource = resolved.day
    adapted = adapt_day_source(
        week=week,
        day=day,
        week_number=week_number,
        day_index=day_index,
    )
    return FileDayRecord(
        day_id=_day_id(course_length, week_number, day_index + 1),
        week_number=week_number,
        day_index=day_index,
        day_number=day_index + 1,
        topic=adapted.topic,
        explanation_brief=adapted.explanation_brief,
        theme_type=week.theme_type,
        cefr_level=resolved.cefr_level,
        sub_level_min=resolved.sub_level_min,
        sub_level_max=resolved.sub_level_max,
        task_archetypes_used=adapted.task_archetypes_used,
        teacher_agent_behaviour=adapted.teacher_agent_behaviour,
        teacher_instructions=adapted.teacher_instructions,
        task_specs=adapted.task_specs,
        activity_contracts=adapted.activity_contracts,
        evaluator_overrides=adapted.evaluator_overrides,
        feedback_overrides=adapted.feedback_overrides,
        final_review=adapted.final_review,
    )


def get_day_by_id(day_id: str) -> FileDayRecord:
    """Return a populated source day by canonical ``day_24_WW_DD`` or ``day_48_WW_DD`` id."""
    course_length, week_number, day_number = parse_day_id(day_id)
    return get_day(week_number, day_number - 1, course_length=course_length)


def resolve_archetypes(day: FileDayRecord) -> tuple[ArchetypeSpec, ...]:
    """Look each archetype name up in the in-process registry."""
    return tuple(get_archetype(aid) for aid in day.task_archetypes_used)


def build_teacher_instructions(day: FileDayRecord) -> dict:
    """Return the minimal file-authored teacher context."""
    out = dict(day.teacher_instructions)
    if day.explanation_brief:
        out["lesson_description"] = day.explanation_brief
    return out


def split_scripted_plan(
    teacher_instructions: dict | None,
) -> tuple[dict, list[str] | None]:
    """Separate the scripted plan from the teacher_instructions dict."""
    if not teacher_instructions:
        return {}, None
    instr = dict(teacher_instructions)
    raw = instr.pop(SCRIPTED_PLAN_KEY, None)
    if isinstance(raw, list) and raw:
        return instr, [str(s) for s in raw if str(s).strip()]
    return instr, None


def task_spec_for(day: FileDayRecord, sequence_index: int) -> dict:
    """Per-activity hint dict for the task generator, or ``{}`` if none."""
    if 0 <= sequence_index < len(day.task_specs):
        return dict(day.task_specs[sequence_index])
    return {}
