"""Feedback-agent + RAG-feedback output contracts.

Mirrors the frontend reference ``ActivityFeedbackOutput`` and ``RagFeedback``
(``feedback/source.ts``). The feedback agent turns an evaluation into
user-facing wording; the RAG agent turns the whole day plus learner memory into
a single carry-forward note.
"""

from __future__ import annotations

from pydantic import Field

from app.modules.sessions.contracts.base import StrictModel


class FeedbackMistake(StrictModel):
    issue: str
    user_wrote: str = ""
    correction: str = ""
    rule: str = ""
    sub_skills_affected: tuple[str, ...] = ()


class ActivityFeedbackOutput(StrictModel):
    """User-facing feedback for one activity."""

    activity_id: str
    archetype_id: str
    score: int = Field(ge=0, le=10)
    summary: str
    did_well: tuple[str, ...] = ()
    mistakes: tuple[FeedbackMistake, ...] = ()
    next_tip: str = ""
    sub_skill_breakdown: dict[str, int] = Field(default_factory=dict)


class RagFeedbackOutput(StrictModel):
    """Day-level memory-backed feedback emitted as the ``rag_feedback`` event."""

    day_id: str
    summary: str
    recurring_weaknesses: tuple[str, ...] = ()
    focus_next: tuple[str, ...] = ()
    memory_written: bool = False


__all__ = [
    "FeedbackMistake",
    "ActivityFeedbackOutput",
    "RagFeedbackOutput",
]
