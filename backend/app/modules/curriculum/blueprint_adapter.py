"""Adapt authored curriculum blueprints into the current session runtime shape.

The curriculum source now describes a day as deterministic blueprints:
teacher steps, activity slots, widget keys, evaluator contracts, feedback
contracts, and final-review widgets. The existing session runtime still
expects a flatter file-day contract: archetype order, task specs, teacher
script lines, and override dictionaries.

This module is the narrow translation layer between those two worlds. It
keeps the runtime deterministic without asking the LLM to decide flow.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.modules.curriculum.data.types import (
    ActivityBlueprint,
    DaySource,
    WeekSource,
)
from app.modules.sessions.exceptions import DayNotFound


@dataclass(frozen=True)
class RuntimeDayBlueprint:
    """Flattened, runtime-ready representation of one authored day."""

    topic: str
    explanation_brief: str
    task_archetypes_used: tuple[str, ...]
    teacher_agent_behaviour: tuple[str, ...]
    teacher_instructions: dict[str, Any]
    task_specs: tuple[dict[str, Any], ...]
    activity_contracts: tuple[dict[str, Any], ...]
    evaluator_overrides: dict[str, Any]
    feedback_overrides: dict[str, Any]
    final_review: dict[str, Any]


def adapt_day_source(
    *,
    week: WeekSource,
    day: DaySource,
    week_number: int,
    day_index: int,
) -> RuntimeDayBlueprint:
    """Return the current runtime contract for a new-style ``DaySource``.

    ``day_index`` is zero-based and used only for helpful validation errors.
    """

    activities = _ordered_activities(day, week_number=week_number, day_index=day_index)
    if not day.title and not activities:
        raise DayNotFound(
            f"week {week_number} day {day_index} is blank - "
            "author it in the level-band source files before starting a session"
        )

    task_archetypes = tuple(activity.task.archetype_id for activity in activities)
    return RuntimeDayBlueprint(
        topic=day.title,
        explanation_brief=day.description,
        task_archetypes_used=task_archetypes,
        teacher_agent_behaviour=_teacher_script(day),
        teacher_instructions=_teacher_instructions(day, week),
        task_specs=tuple(_task_spec(activity) for activity in activities),
        activity_contracts=tuple(_activity_contract(activity) for activity in activities),
        evaluator_overrides=_evaluation_overrides(activities),
        feedback_overrides=_feedback_overrides(activities),
        final_review={
            "scorecard_widget": day.final_review.scorecard_widget,
            "rag_feedback_widget": day.final_review.rag_feedback_widget,
        },
    )


def _ordered_activities(
    day: DaySource,
    *,
    week_number: int,
    day_index: int,
) -> tuple[ActivityBlueprint, ...]:
    activities = tuple(sorted(day.activities, key=lambda activity: activity.sequence))
    sequences = [activity.sequence for activity in activities]
    if len(sequences) != len(set(sequences)):
        raise DayNotFound(
            f"week {week_number} day {day_index}: activity sequences must be unique"
        )
    if sequences and sequences != list(range(1, len(sequences) + 1)):
        raise DayNotFound(
            f"week {week_number} day {day_index}: activity sequences must start "
            "at 1 and be contiguous"
        )
    return activities


def _teacher_script(day: DaySource) -> tuple[str, ...]:
    return tuple(
        step.instruction
        for step in day.teacher.steps
        if step.instruction.strip()
    )


def _teacher_instructions(day: DaySource, week: WeekSource) -> dict[str, Any]:
    instructions: dict[str, Any] = {}
    if day.teacher.style:
        instructions["teacher_style"] = day.teacher.style
    if day.teacher.lesson_goal:
        instructions["lesson_goal"] = day.teacher.lesson_goal
    if day.teacher.readiness_prompt:
        instructions["readiness_prompt"] = day.teacher.readiness_prompt
    if day.focus:
        instructions["focus"] = day.focus
    if day.tags:
        instructions["tags"] = list(day.tags)
    instructions["theme_type"] = week.theme_type
    instructions["teacher_steps"] = [
        {
            "id": step.id,
            "goal": step.goal,
            "instruction": step.instruction,
            "stop_after": step.stop_after,
        }
        for step in day.teacher.steps
    ]
    return instructions


def _task_spec(activity: ActivityBlueprint) -> dict[str, Any]:
    task = activity.task
    spec: dict[str, Any] = {
        "activity_id": activity.id,
        "sequence": activity.sequence,
        "activity": task.activity,
        "task_widget": task.task_widget,
        "topic_override": task.topic_override,
        "instructions_override": task.generation_instructions,
        "widget_requirements": task.widget_requirements,
        "evaluator_type": activity.evaluation.evaluator,
        "evaluation_widget": activity.evaluation.evaluation_widget,
        "feedback_type": activity.feedback.generator,
        "feedback_widget": activity.feedback.feedback_widget,
        "mandatory": activity.mandatory,
    }
    if task.static_payload:
        spec["payload"] = dict(task.static_payload)
    if activity.evaluation.rubric:
        spec["evaluation_rubric"] = dict(activity.evaluation.rubric)
    if activity.evaluation.overrides:
        spec["evaluator_overrides"] = dict(activity.evaluation.overrides)
    if activity.feedback.overrides:
        spec["feedback_overrides"] = dict(activity.feedback.overrides)
    return {key: value for key, value in spec.items() if value not in ("", {}, None)}


def _activity_contract(activity: ActivityBlueprint) -> dict[str, Any]:
    return {
        "activity_id": activity.id,
        "sequence": activity.sequence,
        "archetype_id": activity.task.archetype_id,
        "activity": activity.task.activity,
        "task_widget": activity.task.task_widget,
        "evaluator_type": activity.evaluation.evaluator,
        "evaluation_widget": activity.evaluation.evaluation_widget,
        "feedback_type": activity.feedback.generator,
        "feedback_widget": activity.feedback.feedback_widget,
        "mandatory": activity.mandatory,
    }


def _evaluation_overrides(
    activities: tuple[ActivityBlueprint, ...],
) -> dict[str, Any]:
    by_sequence = {
        str(activity.sequence): {
            "activity_id": activity.id,
            "archetype_id": activity.task.archetype_id,
            "rubric": dict(activity.evaluation.rubric),
            "overrides": dict(activity.evaluation.overrides),
        }
        for activity in activities
        if activity.evaluation.rubric or activity.evaluation.overrides
    }
    return {"by_sequence": by_sequence} if by_sequence else {}


def _feedback_overrides(
    activities: tuple[ActivityBlueprint, ...],
) -> dict[str, Any]:
    by_sequence = {
        str(activity.sequence): {
            "activity_id": activity.id,
            "archetype_id": activity.task.archetype_id,
            "overrides": dict(activity.feedback.overrides),
        }
        for activity in activities
        if activity.feedback.overrides
    }
    return {"by_sequence": by_sequence} if by_sequence else {}
