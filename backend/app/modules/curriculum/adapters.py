"""Adapters that translate the V2 curriculum data model into the
CourseTopic-shaped dicts the legacy LangGraph chat layer was built
against. Keeps the chat agents (`PlannerAgent`, `nodes.py`) decoupled
from the V2 ORM models.
"""

from __future__ import annotations

from typing import Any

from app.modules.curriculum.models import CurriculumDay, CurriculumWeek, TaskArchetype


def v2_course_topic(
    day: CurriculumDay,
    week: CurriculumWeek,
    archetype: TaskArchetype,
) -> dict[str, Any]:
    """Build a CourseTopic-compatible dict from V2 curriculum rows.

    The legacy planner prompt was written against `CourseTopic` attribute
    access. Callers consume this dict either by `[key]` lookup (new code)
    or via a small `SimpleNamespace` wrapper for backward compatibility.
    """
    weight_map = dict(archetype.weight_map or {})
    if weight_map:
        dominant_sub_skill = max(weight_map, key=weight_map.get)
    else:
        dominant_sub_skill = archetype.core_activity

    theme = getattr(week.theme_type, "value", week.theme_type)
    language_focus = f"{theme} — {day.explanation_brief or ''}".rstrip(" —")

    sub_level = (int(week.sub_level_min) + int(week.sub_level_max)) // 2

    return {
        "week": int(week.week_number),
        "day": int(day.day_number),
        "topic_id": day.day_id,
        "communication_goal": week.learning_goal or "",
        "language_focus": language_focus,
        "sub_skill": dominant_sub_skill,
        "sub_level": sub_level,
        "display_label": day.topic,
    }
