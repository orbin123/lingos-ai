"""Pydantic schemas for learning session HTTP + WebSocket payloads."""

from typing import Optional

from pydantic import BaseModel


# --- REST -------------------------------------------------------------


class StartSessionRequest(BaseModel):
    """Empty body — everything is derived from the JWT + active enrollment."""

    pass


class StartSessionResponse(BaseModel):
    session_id: str
    topic: str
    skill_name: str
    task_type: str
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
