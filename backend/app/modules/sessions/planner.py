"""Code-driven session planner.

Reads a `CurriculumDay`, the user's activity preferences, and the
`tasks_per_day` count, and returns an ordered list of archetypes that make
up the session skeleton.

Deterministic and LLM-free. The Task Generator (Phase 4) only fills in the
content for each archetype the planner picked — it does not get to change
the order or composition.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.modules.curriculum.models import CurriculumDay
from app.modules.sessions.exceptions import (
    InvalidTasksPerDay,
    NoActivitiesPlanned,
)


@dataclass(frozen=True)
class PlannedActivity:
    sequence: int
    archetype_id: str
    is_mandatory: bool
    activity: str  # read | write | listen | speak


_ACTIVITY_ORDER: tuple[str, ...] = ("read", "write", "listen", "speak")


def plan_session(
    day: CurriculumDay,
    *,
    tasks_per_day: int,
    allowed_activities: set[str],
) -> list[PlannedActivity]:
    """Return the ordered session skeleton.

    Algorithm:
      1. For each MANDATORY activity in canonical order, pick its first
         CEFR-eligible archetype suggestion. Skip if the user has disabled
         that activity (mandatory ⊕ disabled is allowed — the user simply
         loses that slot).
      2. Walk OPTIONAL activities in canonical order, adding one archetype
         per activity until we hit `tasks_per_day`.
      3. Stop when full. Empty result raises NoActivitiesPlanned.
    """
    if not (2 <= tasks_per_day <= 4):
        raise InvalidTasksPerDay(f"tasks_per_day must be 2..4, got {tasks_per_day}")

    suggested = day.suggested_archetypes or {}
    mandatory = set(day.mandatory_activities or [])

    used_activities: set[str] = set()
    out: list[PlannedActivity] = []
    seq = 1

    # Pass 1: mandatory activities.
    for activity in _ACTIVITY_ORDER:
        if activity not in mandatory:
            continue
        if activity not in allowed_activities:
            continue
        archetype = _first_suggestion(suggested.get(activity, ()))
        if archetype is None:
            continue
        out.append(
            PlannedActivity(
                sequence=seq,
                archetype_id=archetype,
                is_mandatory=True,
                activity=activity,
            )
        )
        used_activities.add(activity)
        seq += 1

    # Pass 2: optional activities, in canonical order.
    for activity in _ACTIVITY_ORDER:
        if len(out) >= tasks_per_day:
            break
        if activity in used_activities:
            continue
        if activity not in allowed_activities:
            continue
        archetype = _first_suggestion(suggested.get(activity, ()))
        if archetype is None:
            continue
        out.append(
            PlannedActivity(
                sequence=seq,
                archetype_id=archetype,
                is_mandatory=False,
                activity=activity,
            )
        )
        used_activities.add(activity)
        seq += 1

    if not out:
        raise NoActivitiesPlanned(
            f"day {day.day_id!r}: no activities matched (allowed={sorted(allowed_activities)}, "
            f"mandatory={sorted(mandatory)})"
        )

    return out


def _first_suggestion(suggestions) -> str | None:
    """Pick the first archetype from a suggestion list (deterministic order)."""
    if not suggestions:
        return None
    # Suggestions come in as list (DB) or tuple (in-memory loader). Both indexable.
    return list(suggestions)[0]
