"""Thin runtime bridge between the daily blueprint and chat UI events.

This module deliberately does not decide the lesson flow. The curriculum
blueprint and V2 session rows already decide what activities exist and in
which order. The orchestrator only turns that deterministic session data
into structured WebSocket events the current and future frontend can render.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.modules.curriculum.file_source import SCRIPTED_PLAN_KEY
from app.modules.learning_session.schemas import WSOutgoingMessage
from app.modules.sessions.widget_mapping import normalize_widget_key


SESSION_EVENT_VERSION = "learning_session.event.v1"
SESSION_PHASE_FLOW = (
    "teaching",
    "task",
    "evaluation",
    "feedback",
    "next_task",
    "final_scorecard",
    "rag_feedback",
    "completed",
)


def activity_contract_from_content(
    content: dict[str, Any],
    *,
    sequence: int | None = None,
    archetype_id: str | None = None,
    is_mandatory: bool | None = None,
) -> dict[str, Any]:
    """Return deterministic activity metadata from persisted task content."""

    contract = dict(content.get("activity_contract") or {})
    if sequence is not None:
        contract.setdefault("sequence", int(sequence))
    if archetype_id:
        contract.setdefault("archetype_id", archetype_id)
    if is_mandatory is not None:
        contract.setdefault("mandatory", bool(is_mandatory))

    for key in (
        "activity_id",
        "task_widget",
        "evaluator_type",
        "evaluation_widget",
        "feedback_type",
        "feedback_widget",
    ):
        value = content.get(key)
        if value not in (None, "", {}):
            contract.setdefault(key, value)

    widget = content.get("widget") or content.get("ui_widget")
    if widget not in (None, "", {}):
        contract.setdefault("task_widget", normalize_widget_key(str(widget)))

    return {
        key: value for key, value in contract.items() if value not in (None, "", {})
    }


def runtime_blueprint_from_attempts(
    attempts: list[Any],
    *,
    teacher_instructions: dict[str, Any] | None = None,
    final_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the small chat-side reminder of the deterministic day shape."""

    activities = []
    for attempt in sorted(attempts, key=lambda item: int(getattr(item, "sequence", 0))):
        content = dict(getattr(attempt, "task_content", None) or {})
        contract = activity_contract_from_content(
            content,
            sequence=int(getattr(attempt, "sequence", 0) or 0),
            archetype_id=str(getattr(attempt, "archetype_id", "") or ""),
            is_mandatory=bool(getattr(attempt, "is_mandatory", True)),
        )
        activities.append(contract)

    return {
        "version": SESSION_EVENT_VERSION,
        "phase_flow": list(SESSION_PHASE_FLOW),
        "teaching": {
            "phase": "teaching",
            "scripted_step_count": len(
                (teacher_instructions or {}).get("__scripted_plan") or []
            ),
        },
        "activities": activities,
        "final_review": final_review
        or {
            "scorecard_widget": "final_scorecard",
            "rag_feedback_widget": "rag_feedback",
        },
    }


def runtime_blueprint_from_session(
    *,
    session: Any,
    task_queue: list[dict[str, Any]] | None = None,
    attempts: list[Any] | None = None,
    final_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the full deterministic chat container from persisted session data."""

    queue = (
        task_queue
        if task_queue is not None
        else list(getattr(session, "task_queue", None) or [])
    )
    activities = _activities_from_task_queue(queue)
    if not activities and attempts:
        activities = runtime_blueprint_from_attempts(attempts).get("activities", [])

    return {
        "version": SESSION_EVENT_VERSION,
        "phase_flow": list(SESSION_PHASE_FLOW),
        "teaching": _teaching_blueprint(
            getattr(session, "teacher_instructions", None),
            topic=getattr(session, "topic", None),
            skill_name=getattr(session, "skill_name", None),
        ),
        "activities": activities,
        "final_review": _final_review_blueprint(final_review),
    }


@dataclass(frozen=True)
class SessionEvent:
    """Structured event plus old `ui_event` compatibility fields."""

    widget: str
    phase: str
    payload_kind: str
    payload: dict[str, Any]
    event_id: str
    activity_contract: dict[str, Any]
    activity_id: str | None = None
    sequence: int | None = None
    archetype_id: str | None = None
    task_widget: str | None = None
    evaluation_widget: str | None = None
    feedback_widget: str | None = None

    def to_ws_message(self) -> WSOutgoingMessage:
        return WSOutgoingMessage(
            type="ui_event",
            widget=self.widget,
            payload=self.payload,
            event_id=self.event_id,
            event_type="ui_event",
            phase=self.phase,
            activity_id=self.activity_id,
            sequence=self.sequence,
            archetype_id=self.archetype_id,
            task_widget=self.task_widget,
            evaluation_widget=self.evaluation_widget,
            feedback_widget=self.feedback_widget,
            activity_contract=self.activity_contract,
            payload_kind=self.payload_kind,
        )


class SessionEventOrchestrator:
    """Create phase-aware UI events from already-determined session data."""

    def session_blueprint_event(
        self,
        *,
        blueprint: dict[str, Any],
        session_meta: dict[str, Any] | None = None,
    ) -> WSOutgoingMessage:
        event_id = uuid4().hex
        payload = {
            "event_id": event_id,
            "event_type": "ui_event",
            "event_version": SESSION_EVENT_VERSION,
            "phase": "teaching",
            "payload_kind": "session_blueprint",
            "blueprint": blueprint,
            "_session": dict(session_meta or {}),
        }
        return WSOutgoingMessage(
            type="ui_event",
            widget="session_blueprint",
            payload=payload,
            event_id=event_id,
            event_type="ui_event",
            phase="teaching",
            payload_kind="session_blueprint",
        )

    def task_event(
        self,
        *,
        widget: str,
        task_payload: dict[str, Any],
        session_meta: dict[str, Any] | None = None,
    ) -> WSOutgoingMessage:
        return self._ui_event(
            widget=widget,
            phase="task",
            payload_kind="task",
            base_payload=task_payload,
            named_payload_key="task",
            named_payload=task_payload,
            session_meta=session_meta,
        ).to_ws_message()

    def evaluation_event(
        self,
        *,
        widget: str,
        evaluation_payload: dict[str, Any],
        evaluation: dict[str, Any],
        session_meta: dict[str, Any] | None = None,
    ) -> WSOutgoingMessage:
        return self._ui_event(
            widget=widget,
            phase="evaluation",
            payload_kind="evaluation",
            base_payload=evaluation_payload,
            named_payload_key="evaluation",
            named_payload=evaluation,
            session_meta=session_meta,
        ).to_ws_message()

    def feedback_event(
        self,
        *,
        widget: str,
        feedback_payload: dict[str, Any],
        feedback: dict[str, Any],
        session_meta: dict[str, Any] | None = None,
    ) -> WSOutgoingMessage:
        return self._ui_event(
            widget=widget,
            phase="feedback",
            payload_kind="feedback",
            base_payload=feedback_payload,
            named_payload_key="feedback",
            named_payload=feedback,
            session_meta=session_meta,
        ).to_ws_message()

    def next_task_event(
        self,
        *,
        payload: dict[str, Any],
        session_meta: dict[str, Any] | None = None,
    ) -> WSOutgoingMessage:
        return self._ui_event(
            widget="session_transition",
            phase="next_task",
            payload_kind="transition",
            base_payload=payload,
            named_payload_key="transition",
            named_payload=payload,
            session_meta=session_meta,
        ).to_ws_message()

    def final_scorecard_event(
        self,
        *,
        widget: str,
        scorecard_payload: dict[str, Any],
        session_meta: dict[str, Any] | None = None,
    ) -> WSOutgoingMessage:
        return self._ui_event(
            widget=widget,
            phase="final_scorecard",
            payload_kind="final_scorecard",
            base_payload=scorecard_payload,
            named_payload_key="scorecard",
            named_payload=scorecard_payload,
            session_meta=session_meta,
        ).to_ws_message()

    def rag_feedback_event(
        self,
        *,
        widget: str,
        feedback_payload: dict[str, Any],
        session_meta: dict[str, Any] | None = None,
    ) -> WSOutgoingMessage:
        return self._ui_event(
            widget=widget,
            phase="rag_feedback",
            payload_kind="rag_feedback",
            base_payload=feedback_payload,
            named_payload_key="rag_feedback",
            named_payload=feedback_payload,
            session_meta=session_meta,
        ).to_ws_message()

    def completed_event(
        self,
        *,
        payload: dict[str, Any],
        session_meta: dict[str, Any] | None = None,
    ) -> WSOutgoingMessage:
        return self._ui_event(
            widget="session_completed",
            phase="completed",
            payload_kind="completed",
            base_payload=payload,
            named_payload_key="completed",
            named_payload=payload,
            session_meta=session_meta,
        ).to_ws_message()

    def _ui_event(
        self,
        *,
        widget: str,
        phase: str,
        payload_kind: str,
        base_payload: dict[str, Any],
        named_payload_key: str,
        named_payload: dict[str, Any],
        session_meta: dict[str, Any] | None,
    ) -> SessionEvent:
        normalized_widget = normalize_widget_key(str(widget))
        payload = dict(base_payload or {})
        contract = activity_contract_from_content(payload)
        meta = dict(session_meta or payload.get("_session") or {})
        sequence = _coerce_int(contract.get("sequence") or meta.get("sequence"))
        activity_id = _optional_str(
            contract.get("activity_id") or payload.get("activity_id")
        )
        archetype_id = _optional_str(
            contract.get("archetype_id") or payload.get("archetype_id")
        )

        task_widget = _optional_str(
            payload.get("task_widget") or contract.get("task_widget")
        )
        if phase == "task" or (
            task_widget is None and phase in {"evaluation", "feedback"}
        ):
            task_widget = normalized_widget
        evaluation_widget = _optional_str(
            contract.get("evaluation_widget") or payload.get("evaluation_widget")
        )
        feedback_widget = _optional_str(
            contract.get("feedback_widget") or payload.get("feedback_widget")
        )

        event_id = uuid4().hex
        structured = {
            "event_id": event_id,
            "event_type": "ui_event",
            "event_version": SESSION_EVENT_VERSION,
            "phase": phase,
            "activity_id": activity_id,
            "sequence": sequence,
            "archetype_id": archetype_id,
            "task_widget": task_widget,
            "evaluation_widget": evaluation_widget,
            "feedback_widget": feedback_widget,
            "activity_contract": contract,
            "payload_kind": payload_kind,
            named_payload_key: named_payload,
            "_session": meta,
        }
        payload.update(
            {key: value for key, value in structured.items() if value is not None}
        )

        return SessionEvent(
            widget=normalized_widget,
            phase=phase,
            payload_kind=payload_kind,
            payload=payload,
            event_id=event_id,
            activity_contract=contract,
            activity_id=activity_id,
            sequence=sequence,
            archetype_id=archetype_id,
            task_widget=task_widget,
            evaluation_widget=evaluation_widget,
            feedback_widget=feedback_widget,
        )


def _coerce_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: Any) -> str | None:
    if value in (None, "", {}):
        return None
    return str(value)


def _activities_from_task_queue(
    task_queue: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    activities: list[dict[str, Any]] = []
    for item in task_queue:
        if not isinstance(item, dict):
            continue
        contract = dict(item.get("activity_contract") or {})
        for key in (
            "activity_id",
            "sequence",
            "archetype_id",
            "activity",
            "task_widget",
            "evaluator_type",
            "evaluation_widget",
            "feedback_type",
            "feedback_widget",
        ):
            value = item.get(key)
            if value not in (None, "", {}):
                contract.setdefault(key, value)
        if "mandatory" not in contract and "is_mandatory" in item:
            contract["mandatory"] = bool(item.get("is_mandatory"))
        if "sequence" in contract:
            coerced = _coerce_int(contract["sequence"])
            if coerced is not None:
                contract["sequence"] = coerced
        activities.append(
            {
                key: value
                for key, value in contract.items()
                if value not in (None, "", {})
            }
        )
    return sorted(activities, key=lambda item: int(item.get("sequence") or 0))


def _teaching_blueprint(
    teacher_instructions: Any,
    *,
    topic: Any = None,
    skill_name: Any = None,
) -> dict[str, Any]:
    instructions = (
        dict(teacher_instructions or {})
        if isinstance(teacher_instructions, dict)
        else {}
    )
    steps = _teacher_steps(instructions)
    teaching = {
        "teacher_style": instructions.get("teacher_style"),
        "lesson_goal": instructions.get("lesson_goal"),
        "readiness_prompt": instructions.get("readiness_prompt"),
        "lesson_description": instructions.get("lesson_description"),
        "focus": instructions.get("focus"),
        "topic": topic,
        "skill_name": skill_name,
        "steps": steps,
        "scripted_step_count": len(steps),
    }
    return {
        key: value for key, value in teaching.items() if value not in (None, "", {}, [])
    }


def _teacher_steps(instructions: dict[str, Any]) -> list[dict[str, Any]]:
    raw_steps = instructions.get("teacher_steps")
    if isinstance(raw_steps, list) and raw_steps:
        steps = []
        for index, step in enumerate(raw_steps, start=1):
            if not isinstance(step, dict):
                continue
            cleaned = {
                "sequence": index,
                "id": step.get("id"),
                "goal": step.get("goal"),
                "instruction": step.get("instruction"),
                "stop_after": step.get("stop_after"),
            }
            steps.append(
                {
                    key: value
                    for key, value in cleaned.items()
                    if value not in (None, "", {})
                }
            )
        return steps

    scripted = instructions.get(SCRIPTED_PLAN_KEY)
    if not isinstance(scripted, list):
        return []
    return [
        {"sequence": index, "instruction": str(instruction)}
        for index, instruction in enumerate(scripted, start=1)
        if str(instruction).strip()
    ]


def _final_review_blueprint(
    final_review: dict[str, Any] | None,
) -> dict[str, str]:
    review = dict(final_review or {})
    return {
        "scorecard_widget": str(review.get("scorecard_widget") or "final_scorecard"),
        "rag_feedback_widget": str(review.get("rag_feedback_widget") or "rag_feedback"),
    }
