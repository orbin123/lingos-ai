"""LangGraph node implementations for the learning session loop.

The chat layer is layered on top of the V2 sessions service:
  * V2 DailySession owns the activities, task content, scoring, and feedback.
  * LearningSession owns the conversation (messages, phase, teacher persona).

These nodes therefore stay small. Evaluation + feedback DB writes are not
done here — the service layer calls `SessionService.submit_activity()`
when a task is submitted, then asks `feedback_node` only to format the
result as a conversational message.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.orm import Session

from app.ai.agents.planner import generate_daily_plan
from app.ai.agents.teacher import generate_teaching_turn
from app.ai.graphs.state import LearningSessionState
from app.ai.llm import get_default_llm_client
from app.modules.curriculum.adapters import v2_course_topic
from app.modules.curriculum.repository import (
    CurriculumDayRepository,
    TaskArchetypeRepository,
)
from app.modules.sessions.models import DailySession
from app.modules.sessions.repository import ActivityAttemptRepository

logger = logging.getLogger(__name__)


async def plan_loader_node(
    state: LearningSessionState,
    *,
    db: Session,
) -> dict[str, Any]:
    """Build a per-session teacher plan from the V2 curriculum.

    Required state fields:
        daily_session_id (int) — the V2 DailySession this chat is layered on.

    Optional:
        course_slug — defaults to "{course_length}-week".
    """
    user_id = state.get("user_id")
    daily_session_id = state.get("daily_session_id")
    if user_id is None or daily_session_id is None:
        raise ValueError(
            "plan_loader_node requires user_id and daily_session_id in state"
        )

    daily = db.get(DailySession, int(daily_session_id))
    if daily is None:
        raise LookupError(f"DailySession id={daily_session_id} not found")

    day = CurriculumDayRepository(db).get_by_day_id(daily.day_id)
    if day is None:
        raise LookupError(f"CurriculumDay day_id={daily.day_id!r} not found")
    week = day.week  # eager-loaded relationship
    if week is None:
        raise LookupError(
            f"CurriculumWeek for day_id={daily.day_id!r} not found"
        )

    attempts = ActivityAttemptRepository(db).list_for_session(daily.id)
    if not attempts:
        raise LookupError(
            f"DailySession id={daily_session_id} has no activity attempts"
        )
    first_attempt = attempts[0]
    archetype = TaskArchetypeRepository(db).get(first_attempt.archetype_id)
    if archetype is None:
        raise LookupError(
            f"TaskArchetype archetype_id={first_attempt.archetype_id!r} not found"
        )

    topic_dict = v2_course_topic(day, week, archetype)
    course_slug = state.get("course_slug") or f"{daily.course_length}-course"

    plan_json = await generate_daily_plan(
        user_id=int(user_id),
        course_slug=course_slug,
        topic_entry=topic_dict,
        learner_profile=state.get("learner_profile") or {},
    )

    return {
        "daily_plan": plan_json,
        "current_activity_order": 1,
        "course_slug": course_slug,
        "week": topic_dict["week"],
        "day": topic_dict["day"],
        "topic": day.topic,
        "skill_name": topic_dict["sub_skill"],
        "user_level": topic_dict["sub_level"],
        "daily_session_uuid": daily.session_id,
        "task_type": archetype.core_activity,
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


async def task_delivery_node(state: LearningSessionState) -> dict[str, Any]:
    """Hand the practice task to the frontend as a UI widget.

    The V2 ActivityAttempt already has `task_content` materialised by the
    V2 task generator. The chat layer just relays it as a UI event.
    """
    task_content = state.get("task_content") or {}
    task_type = state.get("task_type") or "fill_in_blanks"
    queue = list(state.get("task_queue") or [])
    current_index = int(state.get("current_task_index") or 0)
    total = len(queue) or 1

    widget = task_content.get("widget") or task_content.get("ui_widget") or task_type

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
                    "sequence": state.get("current_sequence"),
                    "daily_session_id": state.get("daily_session_id"),
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
        return {
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
