"""Agent input contracts — the service→agent boundary guard.

The projection layer (``projection.py``) validates agent *output* before it
reaches a widget. These models validate agent *input* before the prompt is
built: they assert the required fields a teacher / task-generator / evaluator /
feedback agent depends on are present and well-typed, and (``extra="forbid"``)
that no unexpected key is silently smuggled in.

They are deliberately lightweight — required identity/context fields plus a
loose ``dict`` for task content (deep task-content validation is
``project_task_payload``'s job, not duplicated here).

``build_agent_input`` is the one wiring helper: it raises ``ValidationError``
when ``strict`` (so test/STRICT_CONTRACTS runs fail loudly), and otherwise
returns ``None`` so the caller can log and proceed on legacy behaviour. The
package stays pure — the strict decision (``settings.strict_contracts``) and
logging live in the service callers.
"""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import Field, ValidationError

from app.modules.sessions.contracts.base import StrictModel


class TeacherAgentInput(StrictModel):
    """Inputs the teacher agent needs to drive a scripted teaching turn."""

    topic: str
    lesson_description: str = ""
    teacher_style: str = ""
    lesson_goal: str = ""
    readiness_prompt: str = ""
    teacher_steps: tuple[dict, ...] = ()
    scripted_plan: tuple[str, ...] = ()


class TaskGenAgentInput(StrictModel):
    """Inputs the task generator needs to author one activity's content."""

    archetype_id: str
    day_topic: str
    explanation_brief: str
    cefr_level: str
    sub_level: int = 0
    task_spec: dict = Field(default_factory=dict)


class EvaluatorAgentInput(StrictModel):
    """Inputs the evaluator needs to score a submission."""

    archetype_id: str
    task_content: dict = Field(default_factory=dict)
    user_response: dict = Field(default_factory=dict)


class FeedbackAgentInput(StrictModel):
    """Inputs the feedback generator needs to produce activity feedback."""

    archetype_id: str
    task_content: dict = Field(default_factory=dict)
    evaluation: dict = Field(default_factory=dict)
    user_response: dict = Field(default_factory=dict)


_T = TypeVar("_T", bound=StrictModel)


def build_agent_input(model_cls: type[_T], *, strict: bool, **fields: Any) -> _T | None:
    """Validate a service→agent boundary input.

    Returns the validated model. When validation fails: raises
    ``ValidationError`` if ``strict`` (contract violations surface loudly),
    otherwise returns ``None`` so the caller logs and proceeds unchanged.
    """
    try:
        return model_cls(**fields)
    except ValidationError:
        if strict:
            raise
        return None


__all__ = [
    "TeacherAgentInput",
    "TaskGenAgentInput",
    "EvaluatorAgentInput",
    "FeedbackAgentInput",
    "build_agent_input",
]
