"""Planner agent compatibility layer for learning-session chat."""

from __future__ import annotations

from typing import Any


class PlannerAgent:
    """Build a small teacher plan from the V2 course topic payload.

    File-authored days bypass this planner and pass their own title,
    description, and scripted behavior to the teacher. This class exists for
    DB-backed days and for legacy imports used by the LangGraph nodes.
    """

    async def generate(
        self,
        *,
        user_id: int,
        course_slug: str,
        topic_entry: dict[str, Any],
        learner_profile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return await generate_daily_plan(
            user_id=user_id,
            course_slug=course_slug,
            topic_entry=topic_entry,
            learner_profile=learner_profile or {},
        )


async def generate_daily_plan(
    *,
    user_id: int,
    course_slug: str,
    topic_entry: dict[str, Any],
    learner_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the teacher context shape consumed by chat-session nodes."""

    profile = learner_profile or {}
    display_label = str(
        topic_entry.get("display_label")
        or topic_entry.get("topic")
        or "today's English topic"
    )
    language_focus = str(topic_entry.get("language_focus") or "")
    communication_goal = str(topic_entry.get("communication_goal") or "")

    return {
        "user_id": user_id,
        "course_slug": course_slug,
        "topic_entry": dict(topic_entry),
        "teacher_instructions": {
            "lesson_description": language_focus or communication_goal,
            "lesson_context": communication_goal,
            "personalisation_context": profile.get("personalisation_context") or "",
            "interests": profile.get("interests") or "",
            "primary_goals": profile.get("primary_goals") or "",
            "self_assessed_level": profile.get("self_assessed_level") or "beginner",
            "display_label": display_label,
        },
    }
