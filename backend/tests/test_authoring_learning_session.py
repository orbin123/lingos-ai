from __future__ import annotations

import asyncio
from typing import Any

import pytest

from app.core.config import settings
from app.data.courses.curriculum_v2.source_24w import WEEKS_24
from app.modules.curriculum.file_source import FileDayRecord
from app.modules.learning_session.authoring import (
    AuthoringLearningSessionService,
    AuthoringModeDisabled,
    AuthoringSessionStore,
    _looks_like_ready_for_practice,
)
from app.modules.learning_session.schemas import WSIncomingMessage
from app.modules.sessions.evaluator import EvaluationResult
from app.modules.sessions.exceptions import DayNotFound
from app.modules.sessions.feedback_generator import FeedbackResult
from app.modules.sessions.task_generator import GeneratedTask
from app.scoring import ArchetypeSpec


class CaptureTaskGenerator:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any] | None] = []

    async def generate(
        self,
        *,
        archetype: ArchetypeSpec,
        day_topic: str,
        explanation_brief: str,
        cefr_level: str,
        sub_level: int,
        user_interests: list[str] | None = None,
        task_spec: dict | None = None,
    ) -> GeneratedTask:
        self.calls.append(task_spec)
        return GeneratedTask(
            content={
                "phase": "test",
                "archetype_id": archetype.archetype_id,
                "archetype_name": archetype.name,
                "ui_widget": archetype.ui_widget,
                "widget": "fill_in_blanks",
                "core_activity": archetype.core_activity,
                "topic": task_spec.get("topic_override") if task_spec else day_topic,
                "instructions": "Answer the item.",
                "items": [
                    {
                        "item_id": "q1",
                        "sentence_with_blank": "He ___ daily.",
                        "correct_answer": "works",
                        "explanation": "Third person singular takes -s.",
                    }
                ],
            }
        )


class CaptureEvaluator:
    def __init__(self) -> None:
        self.overrides: dict | None = None

    async def evaluate(
        self,
        *,
        archetype: ArchetypeSpec,
        task_content: dict,
        user_response: dict | None,
        evaluator_overrides: dict | None = None,
    ) -> EvaluationResult:
        self.overrides = evaluator_overrides
        return EvaluationResult(
            raw_score=8.0,
            rubric_scores={rubric: 8.0 for rubric in archetype.rubric},
            evaluator_notes="Clear answer.",
        )


class CaptureFeedback:
    def __init__(self) -> None:
        self.overrides: dict | None = None
        self.task_content: dict | None = None

    async def generate(
        self,
        *,
        archetype: ArchetypeSpec,
        evaluation: EvaluationResult,
        user_response: dict | None,
        task_content: dict | None = None,
        feedback_overrides: dict | None = None,
    ) -> FeedbackResult:
        self.overrides = feedback_overrides
        self.task_content = task_content
        return FeedbackResult(
            score=8,
            summary="Specific useful feedback.",
            did_well=("Used the target form.",),
            mistakes=(),
            next_tip="Keep the subject in mind.",
            sub_skill_breakdown={skill: 8 for skill in archetype.weight_map},
        )


def _service(
    *,
    task: CaptureTaskGenerator | None = None,
    evaluator: CaptureEvaluator | None = None,
    feedback: CaptureFeedback | None = None,
) -> AuthoringLearningSessionService:
    return AuthoringLearningSessionService(
        store=AuthoringSessionStore(),
        task_generator=task or CaptureTaskGenerator(),
        evaluator=evaluator or CaptureEvaluator(),
        feedback_generator=feedback or CaptureFeedback(),
    )


def _file_day(**overrides: Any) -> FileDayRecord:
    data = {
        "day_id": "day_24_01_01",
        "week_number": 1,
        "day_index": 0,
        "day_number": 1,
        "topic": "Original topic",
        "explanation_brief": "Original brief",
        "theme_type": "grammar",
        "cefr_level": "A1",
        "sub_level_min": 1,
        "sub_level_max": 2,
        "task_archetypes_used": ("READ_CLOZE",),
        "teacher_agent_behaviour": ("Teach the original step.",),
        "teacher_instructions": {},
        "task_specs": (),
        "evaluator_overrides": {},
        "feedback_overrides": {},
    }
    data.update(overrides)
    return FileDayRecord(**data)


def test_authoring_start_refuses_when_disabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "AUTHORING_CHAT_MODE", False)
    with pytest.raises(AuthoringModeDisabled):
        asyncio.run(_service().start_session(week=1, day=1))


def test_authoring_start_reads_source_24w(monkeypatch) -> None:
    monkeypatch.setattr(settings, "AUTHORING_CHAT_MODE", True)
    response = asyncio.run(_service().start_session(week=1, day=1))
    assert response.topic == WEEKS_24[0].days[0].title
    assert response.skill_name == "grammar"
    assert response.daily_session_id == 0


def test_authoring_ready_gate_requires_previous_readiness_prompt() -> None:
    previous = "Great, you have the pattern. Ready to try the practice task?"

    assert _looks_like_ready_for_practice("ok", previous_tutor_message=previous)
    assert not _looks_like_ready_for_practice(
        "She work every morning.",
        previous_tutor_message="Change this sentence to she.",
    )
    assert not _looks_like_ready_for_practice(
        "got it",
        previous_tutor_message=previous,
    )
    assert not _looks_like_ready_for_practice(
        "I don't understand",
        previous_tutor_message=previous,
    )


def test_authoring_blank_day_returns_day_not_found(monkeypatch) -> None:
    monkeypatch.setattr(settings, "AUTHORING_CHAT_MODE", True)
    with pytest.raises(DayNotFound):
        asyncio.run(_service().start_session(week=2, day=1))


def test_authoring_passes_task_specs_to_task_generator(monkeypatch) -> None:
    monkeypatch.setattr(settings, "AUTHORING_CHAT_MODE", True)
    task = CaptureTaskGenerator()
    spec = {
        "topic_override": "Authored topic",
        "widget_requirements": "Generate one cloze blank.",
    }
    monkeypatch.setattr(
        "app.modules.learning_session.authoring.get_day",
        lambda week, day_index: _file_day(task_specs=(spec,)),
    )
    asyncio.run(_service(task=task).start_session(week=1, day=1))
    assert task.calls == [spec]


def test_authoring_restart_rereads_file_source(monkeypatch) -> None:
    monkeypatch.setattr(settings, "AUTHORING_CHAT_MODE", True)
    calls = [_file_day(topic="First topic"), _file_day(topic="Second topic")]

    def fake_get_day(week: int, day_index: int) -> FileDayRecord:  # noqa: ARG001
        return calls.pop(0)

    monkeypatch.setattr("app.modules.learning_session.authoring.get_day", fake_get_day)
    service = _service()
    started = asyncio.run(service.start_session(week=1, day=1))
    assert started.topic == "First topic"
    restarted = asyncio.run(service.restart_session(session_id=started.session_id))
    assert restarted.topic == "Second topic"


def test_authoring_submit_passes_eval_and_feedback_overrides(
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "AUTHORING_CHAT_MODE", True)
    monkeypatch.setattr(settings, "AUTHORING_CHAT_COURSE_LENGTH", "24w")
    evaluator = CaptureEvaluator()
    feedback = CaptureFeedback()
    monkeypatch.setattr(
        "app.modules.learning_session.authoring.get_day",
        lambda week, day_index: _file_day(
            evaluator_overrides={"score_focus": "subject verb agreement"},
            feedback_overrides={"tone": "direct"},
        ),
    )
    service = _service(evaluator=evaluator, feedback=feedback)
    started = asyncio.run(service.start_session(week=1, day=1))
    session = service.store.get(started.session_id)
    assert session is not None
    session.phase = "practice_task"

    async def collect_events():
        return [
            event
            async for event in service.process_message_stream(
                started.session_id,
                WSIncomingMessage(type="task_submission", answers={"q1": "works"}),
            )
        ]

    events = asyncio.run(collect_events())

    assert evaluator.overrides == {"score_focus": "subject verb agreement"}
    assert feedback.overrides == {"tone": "direct"}
    assert feedback.task_content is not None
    assert any(event.type == "ui_event" and event.widget == "feedback_card" for event in events)
