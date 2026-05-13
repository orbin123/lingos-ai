"""LangGraph node implementations for the learning session loop.

Each node is async, receives the current `LearningSessionState`, and
returns a partial state dict that LangGraph merges back in. The nodes
are intentionally small — heavy lifting lives in the existing agents
(TaskGeneratorAgent, EvaluationService, generate_feedback).
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.orm import Session

from app.ai.agents.evaluator import EvaluationService
from app.ai.agents.feedback import generate_feedback
from app.ai.agents.planner import generate_daily_plan
from app.ai.agents.task_generator import TaskGeneratorAgent
from app.ai.agents.teacher import generate_teaching_turn
from app.ai.graphs.state import LearningSessionState
from app.ai.llm import get_default_llm_client
from app.modules.curriculum.repository import (
    DailyPlanRepository,
    UserEnrollmentRepository,
)
from app.modules.curriculum.topics import get_course_topic
from app.tasks.schemas.full_tasks_templates import get_full_template_by_id

logger = logging.getLogger(__name__)


async def plan_loader_node(
    state: LearningSessionState,
    *,
    db: Session,
) -> dict[str, Any]:
    """Load (or generate + persist) the DailyPlan for today's session.

    Runs once at the very start of every new session. Subsequent runs for
    the same (user, course, week, day) hit the cache in `daily_plans`.

    Required state fields:
        user_id, enrollment_id

    Optional (used as overrides; otherwise looked up via the enrollment):
        course_slug, week, day
    """
    user_id = state.get("user_id")
    enrollment_id = state.get("enrollment_id")
    if user_id is None or enrollment_id is None:
        raise ValueError(
            "plan_loader_node requires user_id and enrollment_id in state"
        )

    course_slug = state.get("course_slug")
    week = state.get("week")
    day = state.get("day")
    duration_weeks: int | None = None

    enrollment_repo = UserEnrollmentRepository(db)
    enrollment = enrollment_repo.get_by_id(enrollment_id)
    if enrollment is None:
        raise LookupError(f"Enrollment {enrollment_id} not found")
    course = enrollment.course
    duration_weeks = course.duration_weeks
    if course_slug is None:
        course_slug = course.slug
    if week is None:
        week = enrollment.current_week
    if day is None:
        day = enrollment.current_day_in_week

    plan_repo = DailyPlanRepository(db)
    existing = plan_repo.get_for_day(
        user_id=user_id, course_slug=course_slug, week=week, day=day,
    )
    if existing is not None:
        return {
            "daily_plan": dict(existing.plan_json),
            "current_activity_order": 1,
            "course_slug": course_slug,
            "week": week,
            "day": day,
        }

    topic_entry = get_course_topic(
        duration_weeks=duration_weeks, week=week, day=day,
    )
    if topic_entry is None:
        raise LookupError(
            f"No course topic for duration_weeks={duration_weeks}, "
            f"week={week}, day={day}"
        )

    plan_json = await generate_daily_plan(
        user_id=user_id,
        course_slug=course_slug,
        topic_entry=topic_entry,
        learner_profile=state.get("learner_profile") or {},
    )
    plan_repo.upsert(
        user_id=user_id,
        course_slug=course_slug,
        week=week,
        day=day,
        topic_id=topic_entry.topic_id,
        plan_json=plan_json,
    )

    return {
        "daily_plan": plan_json,
        "current_activity_order": 1,
        "course_slug": course_slug,
        "week": week,
        "day": day,
    }


async def teach_node(state: LearningSessionState) -> dict[str, Any]:
    """Produce a short concept-teaching turn before practice starts."""
    topic = state.get("topic") or "today's English topic"
    user_level = int(state.get("user_level", 5))
    task_type = state.get("task_type") or "fill_in_blanks"
    skill_name = state.get("skill_name") or "grammar"
    learner_profile = state.get("learner_profile") or {}
    daily_plan = state.get("daily_plan") or {}
    teacher_instructions = daily_plan.get("teacher_instructions") if daily_plan else None

    teaching = await generate_teaching_turn(
        topic=topic,
        sub_skill=skill_name,
        task_type=task_type,
        user_level=user_level,
        learner_profile=learner_profile,
        conversation=list(state.get("messages", [])),
        teacher_instructions=teacher_instructions,
    )
    chat_messages = teaching.messages

    outgoing = [
        {"type": "chat_message", "role": "assistant", "content": msg}
        for msg in chat_messages
    ]

    new_messages = list(state.get("messages", []))
    for msg in chat_messages:
        new_messages.append({"role": "ai", "content": msg, "type": "chat"})

    return {
        "phase": "teaching",
        "outgoing_events": outgoing,
        "messages": new_messages,
    }


def _find_plan_activity(
    state: LearningSessionState,
) -> dict[str, Any] | None:
    """Return the daily-plan activity dict matching current_activity_order.

    None if no plan is loaded yet or the order is missing/out of range.
    """
    daily_plan = state.get("daily_plan") or {}
    activities = daily_plan.get("activities") if daily_plan else None
    if not activities:
        return None
    order = state.get("current_activity_order") or 1
    for activity in activities:
        if int(activity.get("order") or 0) == int(order):
            return activity
    return None


async def task_delivery_node(state: LearningSessionState) -> dict[str, Any]:
    """Hand the practice task to the frontend as a UI widget.

    Two paths:
      1. Plan-aware: if `daily_plan` is loaded and `task_content` has not
         been pre-generated, generate the task using the activity's
         `template_id` from the plan. Widget comes from the plan activity.
      2. Legacy/pre-generated: existing flow — read `task_content` and
         derive widget from it. Used when there is no plan yet (sessions
         created before the Planner refactor or when the plan_loader fails).
    """
    task_content = state.get("task_content") or {}
    task_type = state.get("task_type") or "fill_in_blanks"
    queue = list(state.get("task_queue") or [])
    current_index = int(state.get("current_task_index") or 0)
    total = len(queue) or 1
    plan_activity = _find_plan_activity(state)

    updated_state_patch: dict[str, Any] = {}

    if plan_activity is not None:
        widget = plan_activity.get("widget") or task_content.get("widget") or task_type
        if not task_content:
            try:
                template = get_full_template_by_id(plan_activity["template_id"])
                generator = TaskGeneratorAgent()
                profile = dict(state.get("learner_profile") or {})
                daily_plan = state.get("daily_plan") or {}
                profile.setdefault("sub_level", daily_plan.get("sub_level") or 5)
                profile.setdefault(
                    "course_topic", daily_plan.get("topic_name") or state.get("topic") or ""
                )
                profile.setdefault(
                    "topic", daily_plan.get("topic_name") or state.get("topic") or ""
                )
                task_content = await generator.generate(template, profile)
                task_content.setdefault("widget", widget)
                updated_state_patch["task_content"] = task_content
                updated_state_patch["task_type"] = task_content.get("widget") or task_type
            except Exception:
                logger.exception(
                    "task_delivery_node on-demand generation failed "
                    "(template_id=%s); falling back to pre-generated task_content",
                    plan_activity.get("template_id"),
                )
    else:
        widget = task_content.get("widget") or task_type

    intro = (
        f"Great! Here is activity {current_index + 1} of {total}."
        if total > 1
        else "Great! Here is your practice task."
    )

    outgoing = [
        {"type": "chat_message", "role": "assistant", "content": intro},
        {
            "type": "ui_event",
            "widget": widget,
            "payload": {
                **task_content,
                "_session": {
                    "current_task_index": current_index,
                    "total_tasks": total,
                    "user_task_id": state.get("user_task_id"),
                },
            },
        },
    ]

    new_messages = list(state.get("messages", []))
    new_messages.append({"role": "ai", "content": intro, "type": "chat"})
    new_messages.append(
        {
            "role": "ai",
            "content": f"[task delivered: {task_type}]",
            "type": "ui_event",
        }
    )

    return {
        "phase": "practice_task",
        "outgoing_events": outgoing,
        "messages": new_messages,
        **updated_state_patch,
    }


# Task types that require the LLM-based async writing evaluator
_OPEN_TEXT_TASK_TYPES = frozenset({"curriculum_grammar_open_text"})
_GRAMMAR_SPEAK_TASK_TYPES = frozenset({"curriculum_grammar_speak"})


async def evaluation_node(state: LearningSessionState) -> dict[str, Any]:
    """Score the user's submission and emit a scorecard widget."""
    task_content = state.get("task_content") or {}
    user_submission = state.get("user_submission") or {}
    task_type = state.get("task_type") or "fill_in_blanks"
    skill_name = state.get("skill_name", "")
    topic = state.get("topic", "")
    queue = list(state.get("task_queue") or [])
    current_index = int(state.get("current_task_index") or 0)

    evaluator = EvaluationService()
    plan_activity = _find_plan_activity(state)
    evaluation_focus = (
        plan_activity.get("evaluation_focus") if plan_activity else None
    )

    if task_type in _OPEN_TEXT_TASK_TYPES:
        evaluation = await evaluator.evaluate_open_text_writing(
            task_content=task_content,
            user_answers=user_submission,
            user_level=int(state.get("user_level") or 5),
            learner_profile=state.get("learner_profile") or {},
            evaluation_focus=evaluation_focus,
        )
    elif task_type in _GRAMMAR_SPEAK_TASK_TYPES:
        evaluation = await evaluator.evaluate_grammar_speaking(
            task_content=task_content,
            user_answers=user_submission,
            user_level=int(state.get("user_level") or 5),
            learner_profile=state.get("learner_profile") or {},
            evaluation_focus=evaluation_focus,
        )
    else:
        evaluation = evaluator.evaluate(
            activity_type=task_type,
            task_content=task_content,
            user_answers=user_submission,
        )

    overall_score = int(round(float(evaluation.get("percentage", 0.0))))
    payload = {
        "overall_score": overall_score,
        "skill_name": skill_name,
        "topic": topic,
        "total": evaluation.get("total", 0),
        "correct_count": evaluation.get("correct_count", 0),
        "questions": evaluation.get("questions", {}),
        "subskill_score": evaluation.get("subskill_score"),  # None for rule-based tasks
        "_session": {
            "current_task_index": current_index,
            "total_tasks": len(queue) or 1,
            "user_task_id": state.get("user_task_id"),
        },
    }

    outgoing = [
        {
            "type": "ui_event",
            "widget": "scorecard",
            "payload": payload,
        }
    ]

    new_messages = list(state.get("messages", []))
    new_messages.append(
        {
            "role": "ai",
            "content": f"[scorecard delivered: {overall_score}%]",
            "type": "ui_event",
        }
    )

    return {
        "phase": "scorecard",
        "evaluation": evaluation,
        "outgoing_events": outgoing,
        "messages": new_messages,
    }


async def feedback_node(state: LearningSessionState) -> dict[str, Any]:
    """Generate corrective feedback, emit a feedback card + follow-up CTA."""
    task_content = state.get("task_content") or {}
    user_submission = state.get("user_submission") or {}
    evaluation = state.get("evaluation") or {}
    score = int(round(float(evaluation.get("percentage", 0.0))))

    try:
        feedback_obj = await generate_feedback(
            task_content=task_content,
            user_answers=user_submission,
            evaluation_report=evaluation,
            score=score,
        )
        feedback_dict = feedback_obj.model_dump()
    except Exception:
        logger.exception("feedback_node LLM call failed; using fallback feedback")
        feedback_dict = {
            "overall_message": (
                "Good effort. Review the highlighted answers and try the "
                "task again to lock in the rule."
            ),
            "errors": [],
            "score": score,
            "overall_level": "okay",
            "practice_suggestion": "Write 5 sentences using today's pattern.",
        }

    overall_message = feedback_dict.get("overall_message", "")
    queue = list(state.get("task_queue") or [])
    current_index = int(state.get("current_task_index") or 0)
    has_next = any(
        int(item.get("sequence_index") or index) > current_index
        and item.get("status") != "completed"
        for index, item in enumerate(queue)
    )
    follow_up_actions = (
        ["Next activity", "Go to dashboard"]
        if has_next
        else ["Go to dashboard"]
    )

    outgoing: list[dict] = [
        {
            "type": "ui_event",
            "widget": "feedback_card",
            "payload": {
                **feedback_dict,
                "_session": {
                    "current_task_index": current_index,
                    "total_tasks": len(queue) or 1,
                    "has_next": has_next,
                },
            },
        },
        {
            "type": "chat_message",
            "role": "assistant",
            "content": overall_message,
            "actions": follow_up_actions,
        },
    ]

    new_messages = list(state.get("messages", []))
    new_messages.append(
        {
            "role": "ai",
            "content": "[feedback card delivered]",
            "type": "ui_event",
        }
    )
    if overall_message:
        new_messages.append(
            {"role": "ai", "content": overall_message, "type": "chat"}
        )

    return {
        "phase": "feedback",
        "feedback": feedback_dict,
        "outgoing_events": outgoing,
        "messages": new_messages,
    }


async def followup_node(state: LearningSessionState) -> dict[str, Any]:
    """Branch on the user's follow-up choice."""
    messages = list(state.get("messages", []))
    last_user = next(
        (m for m in reversed(messages) if m.get("role") == "user"),
        None,
    )
    raw_action = (last_user or {}).get("content", "") or ""
    action = raw_action.strip().lower()

    end_signals = ("go to dashboard", "end session", "end", "stop", "bye", "goodbye")
    another_signals = (
        "next activity",
        "try another task",
        "another task",
        "next task",
        "more",
    )
    question_signals = ("ask a question", "question", "doubt", "clarif")

    if any(sig in action for sig in end_signals):
        farewell = (
            "Great work. Go back to the dashboard to review today's "
            "activities and advance when you're ready."
        )
        new_messages = messages + [
            {"role": "ai", "content": farewell, "type": "chat"}
        ]
        return {
            "phase": "ended",
            "outgoing_events": [
                {
                    "type": "chat_message",
                    "role": "assistant",
                    "content": farewell,
                    "actions": ["Go to dashboard"],
                }
            ],
            "messages": new_messages,
        }

    if any(sig in action for sig in another_signals):
        prompt_msg = "Use the Next activity button when you're ready to continue."
        new_messages = messages + [
            {"role": "ai", "content": prompt_msg, "type": "chat"}
        ]
        update: dict[str, Any] = {
            "phase": "teaching",
            "outgoing_events": [
                {
                    "type": "chat_message",
                    "role": "assistant",
                    "content": prompt_msg,
                    "actions": ["Next activity", "Go to dashboard"],
                }
            ],
            "messages": new_messages,
        }
        # If a plan is loaded, advance the activity pointer so the next
        # task_delivery picks up the next template_id from the plan.
        daily_plan = state.get("daily_plan") or {}
        activities = daily_plan.get("activities") if daily_plan else None
        if activities:
            current_order = int(state.get("current_activity_order") or 1)
            next_order = current_order + 1
            if next_order > len(activities):
                # No more activities in the plan — mark the day complete.
                farewell = (
                    "Today's activities are complete. Go back to the dashboard "
                    "to review the day and advance when you're ready."
                )
                update = {
                    "phase": "ended",
                    "outgoing_events": [
                        {
                            "type": "chat_message",
                            "role": "assistant",
                            "content": farewell,
                            "actions": ["Go to dashboard"],
                        }
                    ],
                    "messages": messages + [
                        {"role": "ai", "content": farewell, "type": "chat"}
                    ],
                }
            else:
                update["current_activity_order"] = next_order
                # Clear task_content so the next task_delivery_node regenerates.
                update["task_content"] = None
        return update

    if action in question_signals:
        prompt_msg = "Sure — what would you like to know?"
        new_messages = messages + [
            {"role": "ai", "content": prompt_msg, "type": "chat"}
        ]
        return {
            "phase": "follow_up",
            "outgoing_events": [
                {"type": "chat_message", "role": "assistant", "content": prompt_msg}
            ],
            "messages": new_messages,
        }

    answer = await _answer_question(state, raw_action)
    if "clarify" not in answer.lower() and "doubt" not in answer.lower():
        answer = f"{answer.rstrip()} Did that clarify your doubt?"
    new_messages = messages + [
        {"role": "ai", "content": answer, "type": "chat"}
    ]
    return {
        "phase": "follow_up",
        "outgoing_events": [
            {"type": "chat_message", "role": "assistant", "content": answer}
        ],
        "messages": new_messages,
    }


async def _answer_question(state: LearningSessionState, question: str) -> str:
    """Free-form Q&A grounded in the current topic."""
    topic = state.get("topic") or "the current English topic"
    user_level = int(state.get("user_level", 5))

    if not question.strip():
        return "Sure — what would you like to know?"

    system = (
        "You are a friendly English tutor answering a learner's follow-up "
        f"question about '{topic}'. The learner is at sub-level {user_level}/10. "
        "Reply with a short, clear chat message (1-3 sentences). Use simple "
        "language and one example if helpful."
    )
    try:
        client = get_default_llm_client()
        return await client.generate_text(
            system_prompt=system,
            user_prompt=question,
            temperature=0.4,
        )
    except Exception:
        logger.exception("followup Q&A LLM call failed; using fallback")
        return (
            "Good question — let's revisit that next session when I can pull "
            "up extra examples."
        )


async def stream_answer_question(
    state: LearningSessionState, question: str
) -> AsyncIterator[str]:
    """Stream free-form Q&A grounded in the current topic."""
    topic = state.get("topic") or "the current English topic"
    user_level = int(state.get("user_level", 5))

    if not question.strip():
        yield "Sure — what would you like to know?"
        return

    system = (
        "You are a friendly English tutor answering a learner's follow-up "
        f"question about '{topic}'. The learner is at sub-level {user_level}/10. "
        "Reply with a short, clear chat message (1-3 sentences). Use simple "
        "language and one example if helpful."
    )
    try:
        client = get_default_llm_client()
        async for chunk in client.stream_text(
            system_prompt=system,
            user_prompt=question,
            temperature=0.4,
        ):
            yield chunk
    except Exception:
        logger.exception("followup Q&A streaming LLM call failed; using fallback")
        yield (
            "Good question — let's revisit that next session when I can pull "
            "up extra examples."
        )
