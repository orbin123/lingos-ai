"""Typed state passed between LangGraph nodes for the learning session."""

from typing import Any, Literal, Optional, TypedDict


PhaseType = Literal[
    "teaching",
    "practice_task",
    "evaluation",
    "scorecard",
    "feedback",
    "follow_up",
    "ended",
]


class LearningSessionState(TypedDict, total=False):
    session_id: str
    user_id: int
    phase: PhaseType
    messages: list[dict]
    topic: str
    skill_name: str
    activity_type: str
    user_level: int
    task_content: Optional[dict]
    task_type: Optional[str]
    user_submission: Optional[dict]
    evaluation: Optional[dict]
    feedback: Optional[Any]
    learner_profile: dict[str, Any]
    understanding_confirmed: bool
    outgoing_events: list[dict]
