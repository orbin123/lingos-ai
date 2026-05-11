"""Pydantic schemas for learning session HTTP + WebSocket payloads."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# --- REST -------------------------------------------------------------


class LearningSessionSnapshotRead(BaseModel):
    """Read-only snapshot of a completed chat session for the history page."""

    session_id: str
    topic: str
    skill_name: str
    task_type: str
    phase: str
    messages: list[dict[str, Any]]
    pre_generated_tasks: dict[str, Any] | None
    user_submission: dict[str, Any] | None
    evaluation: dict[str, Any] | None
    feedback: dict[str, Any] | None
    task_queue: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime


class StartSessionRequest(BaseModel):
    """Start a chat session.

    When ``user_task_id`` is supplied, the session practices that exact
    dashboard task. Without it, the service keeps the older behavior of
    generating a fresh session from the active enrollment.
    """

    user_task_id: Optional[int] = None


class StartSessionResponse(BaseModel):
    session_id: str
    topic: str
    skill_name: str
    task_type: str
    user_task_id: Optional[int] = None
    message: str = "Session ready"


# --- WebSocket --------------------------------------------------------


class WSIncomingMessage(BaseModel):
    """Message shape sent FROM the frontend chat composer."""

    type: str  # "user_message" | "task_submission" | "follow_up_action"
    content: Optional[str] = None
    answers: Optional[dict] = None
    action: Optional[str] = None


class WSOutgoingMessage(BaseModel):
    """Message shape sent FROM the backend back to the frontend."""

    type: str  # "chat_message" | "chat_stream_*" | "ui_event" | "error"
    role: Optional[str] = None
    content: Optional[str] = None
    stream_id: Optional[str] = None
    widget: Optional[str] = None
    payload: Optional[dict] = None
    actions: Optional[list[str]] = None
