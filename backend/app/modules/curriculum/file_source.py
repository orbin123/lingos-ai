"""Read curriculum days directly from ``source_24w.py``.

Provides the bridge between the authored dataclasses in ``source_24w.py``
and the session services.  When a day is file-authored (non-blank), its
archetype order, task specs, teacher instructions, and eval/feedback
overrides take precedence over the DB-seeded curriculum.

Day identity is ``(week_number, day_index)`` where ``day_index``
is 0..6 — the tuple position inside ``WeekSource.days``.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from app.modules.curriculum.blueprint_adapter import adapt_day_source
from app.modules.curriculum.data.source_24w import (
    WEEKS_24,
    DaySource,
    WeekSource,
)
from app.modules.sessions.exceptions import DayNotFound
from app.scoring import ArchetypeSpec, get_archetype


# Reserved key used to carry authored `teacher_agent_behaviour` through the
# existing `teacher_instructions` storage column without reintroducing the old
# planner-style instruction schema.
SCRIPTED_PLAN_KEY: str = "__scripted_plan"

_DAY_ID_RE = re.compile(r"^day_24_(\d{2})_(\d{2})$")


@dataclass(frozen=True)
class FileDayRecord:
    """Flat per-day record served from `source_24w.py`.

    Carries `topic` + `explanation_brief` under the same names the existing
    `SessionService._materialise_attempt` reads from `CurriculumDay`, so the
    file branch can reuse that helper.
    """

    day_id: str
    week_number: int
    day_index: int          # 0..6
    day_number: int         # 1..7
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


def _find_week(week_number: int) -> WeekSource:
    for w in WEEKS_24:
        if w.week_number == week_number:
            return w
    raise DayNotFound(f"week_number={week_number} not in WEEKS_24")


def _day_id(week_number: int, day_number: int) -> str:
    return f"day_24_{week_number:02d}_{day_number:02d}"


def parse_day_id(day_id: str) -> tuple[int, int]:
    """Parse a file-source `day_24_WW_DD` id into 1-based numbers."""
    match = _DAY_ID_RE.match(day_id or "")
    if not match:
        raise DayNotFound(f"day_id={day_id!r} is not a 24-week file-source day")
    return int(match.group(1)), int(match.group(2))


def get_day(week_number: int, day_index: int) -> FileDayRecord:
    """Return the day spec at `(week_number, day_index)`.

    `day_index` is 0-based. Raises `DayNotFound` if either is out of range
    or the day entry is blank (no title and no archetypes — nothing
    actionable for the chat session).
    """
    week = _find_week(week_number)
    if not (0 <= day_index < len(week.days)):
        raise DayNotFound(
            f"day_index={day_index} out of range for week {week_number} "
            f"(has {len(week.days)} days)"
        )
    day: DaySource = week.days[day_index]
    adapted = adapt_day_source(
        week=week,
        day=day,
        week_number=week_number,
        day_index=day_index,
    )
    return FileDayRecord(
        day_id=_day_id(week_number, day_index + 1),
        week_number=week_number,
        day_index=day_index,
        day_number=day_index + 1,
        topic=adapted.topic,
        explanation_brief=adapted.explanation_brief,
        theme_type=week.theme_type,
        cefr_level=week.cefr_level,
        sub_level_min=week.sub_level_min,
        sub_level_max=week.sub_level_max,
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
    """Return a populated source day by canonical `day_24_WW_DD` id."""
    week_number, day_number = parse_day_id(day_id)
    return get_day(week_number, day_number - 1)


def resolve_archetypes(day: FileDayRecord) -> tuple[ArchetypeSpec, ...]:
    """Look each archetype name up in the in-process registry."""
    return tuple(get_archetype(aid) for aid in day.task_archetypes_used)


def build_teacher_instructions(day: FileDayRecord) -> dict:
    """Return the minimal file-authored teacher context.

    File-authored days intentionally do not use the old planner-style
    instruction spectrum. The teacher receives the day title separately,
    this lesson description, and the scripted behaviour stashed under
    `SCRIPTED_PLAN_KEY` by the session layer.
    """
    out = dict(day.teacher_instructions)
    if day.explanation_brief:
        out["lesson_description"] = day.explanation_brief
    return out


def split_scripted_plan(
    teacher_instructions: dict | None,
) -> tuple[dict, list[str] | None]:
    """Separate the scripted plan from the teacher_instructions dict.

    Returns `(instr_without_script, scripted_plan_or_None)`. The input
    dict is not mutated; callers receive a shallow copy.
    """
    if not teacher_instructions:
        return {}, None
    instr = dict(teacher_instructions)
    raw = instr.pop(SCRIPTED_PLAN_KEY, None)
    if isinstance(raw, list) and raw:
        return instr, [str(s) for s in raw if str(s).strip()]
    return instr, None


def task_spec_for(day: FileDayRecord, sequence_index: int) -> dict:
    """Per-activity hint dict for the task generator, or `{}` if none.

    `sequence_index` is 0-based and matches the position in
    `day.task_archetypes_used`.
    """
    if 0 <= sequence_index < len(day.task_specs):
        return dict(day.task_specs[sequence_index])
    return {}
