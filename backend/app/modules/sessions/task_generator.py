"""TaskGenerator interface + Phase 3 deterministic stub.

Mirrors the Evaluator / FeedbackGenerator pattern. The session shell pulls
`task_content` from whichever generator is wired in; Phase 4 swaps the
default to the LLM-driven implementation.

`task_content` is the JSONB blob the frontend renders. Shape varies by
archetype (passages for read, prompts for write, audio for listen, …) but
every payload carries the common keys defined in `_BASE_FIELDS` below so
the widget shell can render a minimal view even when the archetype-specific
fields are missing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.scoring import ArchetypeSpec


_BASE_FIELDS = ("phase", "archetype_id", "archetype_name", "ui_widget", "core_activity")


@dataclass(frozen=True)
class GeneratedTask:
    """Wrapper that distinguishes the rendered content from optional notes.

    `content` is what gets stored in `activity_attempts.task_content` and
    shipped to the frontend. `evaluator_notes` is optional internal context
    the Evaluator may consult (e.g. "expected key points: …") and is NOT
    surfaced through the next-activity API. Phase 4 MVP leaves it empty.
    """

    content: dict
    evaluator_notes: str | None = None


class TaskGenerator(Protocol):
    """Produce the `task_content` JSON for one activity in a session."""

    async def generate(
        self,
        *,
        archetype: ArchetypeSpec,
        day_topic: str,
        explanation_brief: str,
        cefr_level: str,
        sub_level: int,
        user_interests: list[str] | None = None,
    ) -> GeneratedTask: ...


class StubTaskGenerator:
    """Deterministic offline TaskGenerator. Used in tests and as fallback.

    Returns the same shape as the Phase 3 `_stub_task_content` helper so
    existing widget code keeps working without an LLM call.
    """

    async def generate(
        self,
        *,
        archetype: ArchetypeSpec,
        day_topic: str,
        explanation_brief: str,
        cefr_level: str,
        sub_level: int,
        user_interests: list[str] | None = None,
    ) -> GeneratedTask:
        content = {
            "phase": "stub",
            "archetype_id": archetype.archetype_id,
            "archetype_name": archetype.name,
            "ui_widget": archetype.ui_widget,
            "core_activity": archetype.core_activity,
            "topic": day_topic,
            "explanation_brief": explanation_brief,
            "instructions": (
                f"Practice {archetype.name.lower()} on the topic '{day_topic}'."
            ),
            "cefr_level": cefr_level,
            "sub_level": sub_level,
        }
        return GeneratedTask(content=content)


def assert_has_base_fields(content: dict) -> None:
    """Validate a content payload carries the keys widgets rely on.

    Used by tests and at production-defensive seams. Raises ValueError
    rather than silently shipping a payload the frontend can't render.
    """
    missing = [f for f in _BASE_FIELDS if f not in content]
    if missing:
        raise ValueError(f"task content missing required base fields: {missing}")
