from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

import pytest

from app.core.config import settings
from app.ai.graphs.nodes import task_delivery_node
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


class LegacyFillBlankTaskGenerator:
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
        return GeneratedTask(
            content={
                "phase": "test",
                "archetype_id": archetype.archetype_id,
                "archetype_name": archetype.name,
                "ui_widget": archetype.ui_widget,
                "widget": "fill_in_blanks",
                "core_activity": archetype.core_activity,
                "topic": day_topic,
                "instruction": "Fill each blank with the correct form of 'to be'.",
                "source": {
                    "type": "passage",
                    "text": "I ___ a learner. She ___ my teacher.",
                },
                "activities": [
                    {
                        "activity_type": "fill_in_the_blanks",
                        "questions": {
                            "Q1": "I ___ a learner.",
                            "Q2": "She ___ my teacher.",
                        },
                        "answers": {"Q1": "am", "Q2": "is"},
                    }
                ],
            }
        )


class OpenTextRoutineTaskGenerator:
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
        return GeneratedTask(
            content={
                "phase": "test",
                "archetype_id": archetype.archetype_id,
                "archetype_name": archetype.name,
                "ui_widget": archetype.ui_widget,
                "widget": "open_text",
                "core_activity": archetype.core_activity,
                "topic": task_spec.get("topic_override") if task_spec else day_topic,
                "instructions": "Write routine sentences.",
                "items": [
                    {
                        "item_id": "routine_i",
                        "prompt": "Write one I routine sentence.",
                        "sample_answer": "I usually study English.",
                        "answer_hints": ["Use I.", "Use a frequency adverb."],
                    },
                    {
                        "item_id": "routine_he",
                        "prompt": "Write one he routine sentence.",
                        "sample_answer": "He often walks to school.",
                        "answer_hints": ["Use he.", "Add -s to the verb."],
                    },
                    {
                        "item_id": "routine_she",
                        "prompt": "Write one she routine sentence.",
                        "sample_answer": "She always eats breakfast.",
                        "answer_hints": ["Use she.", "Add -s to the verb."],
                    },
                ],
            }
        )


class CaptureEvaluator:
    def __init__(self) -> None:
        self.overrides: dict | None = None
        self.calls: list[dict[str, Any]] = []

    async def evaluate(
        self,
        *,
        archetype: ArchetypeSpec,
        task_content: dict,
        user_response: dict | None,
        evaluator_overrides: dict | None = None,
    ) -> EvaluationResult:
        self.overrides = evaluator_overrides
        self.calls.append(
            {
                "archetype_id": archetype.archetype_id,
                "task_content": task_content,
                "user_response": user_response,
            }
        )
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


class FakeTeacherLLM:
    def __init__(self, turns: list[str]) -> None:
        self.turns = list(turns)

    async def generate_text(self, **_kwargs) -> str:
        return self.turns.pop(0)

    async def stream_text(self, **_kwargs) -> AsyncIterator[str]:
        text = self.turns.pop(0)
        midpoint = max(1, len(text) // 2)
        yield text[:midpoint]
        yield text[midpoint:]


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


def test_authoring_w1d1_delivery_emits_fill_in_blanks_widget(monkeypatch) -> None:
    monkeypatch.setattr(settings, "AUTHORING_CHAT_MODE", True)
    service = _service()
    started = asyncio.run(service.start_session(week=1, day=1))
    session = service.store.get(started.session_id)
    assert session is not None
    session.messages.append(
        {
            "role": "ai",
            "content": "Ready to try the practice task?",
            "type": "chat",
        }
    )

    async def collect_events():
        return [
            event
            async for event in service.process_message_stream(
                started.session_id,
                WSIncomingMessage(type="user_message", content="yes"),
            )
        ]

    events = asyncio.run(collect_events())

    task_event = next(event for event in events if event.type == "ui_event")
    assert task_event.widget == "fill_in_blanks"
    assert task_event.payload["widget"] == "fill_in_blanks"
    assert task_event.payload["instructions"] == (
        "Fill each blank with the correct simple present verb."
    )
    assert [item["correct_answer"] for item in task_event.payload["items"]] == [
        "brush",
        "eats",
        "walks",
        "drink",
    ]


def test_authoring_delivery_normalizes_legacy_fill_blank_payload(monkeypatch) -> None:
    monkeypatch.setattr(settings, "AUTHORING_CHAT_MODE", True)
    service = _service(task=LegacyFillBlankTaskGenerator())
    started = asyncio.run(service.start_session(week=1, day=1))
    session = service.store.get(started.session_id)
    assert session is not None
    session.messages.append(
        {
            "role": "ai",
            "content": "Ready to try the practice task?",
            "type": "chat",
        }
    )

    async def collect_events():
        return [
            event
            async for event in service.process_message_stream(
                started.session_id,
                WSIncomingMessage(type="user_message", content="yes"),
            )
        ]

    events = asyncio.run(collect_events())

    task_event = next(event for event in events if event.type == "ui_event")
    assert task_event.widget == "fill_in_blanks"
    assert task_event.payload["instructions"] == (
        "Fill each blank with the correct form of 'to be'."
    )
    assert task_event.payload["passage"] == "I ___ a learner. She ___ my teacher."
    assert task_event.payload["total_blanks"] == 2
    assert [item["item_id"] for item in task_event.payload["items"]] == ["Q1", "Q2"]
    assert [item["correct_answer"] for item in task_event.payload["items"]] == [
        "am",
        "is",
    ]


def test_task_delivery_node_normalizes_legacy_fill_blank_payload() -> None:
    update = asyncio.run(
        task_delivery_node(
            {
                "task_content": {
                    "widget": "FillInBlanks",
                    "instruction": "Fill the blanks.",
                    "source": {"type": "passage", "text": "He ___ here."},
                    "activities": [
                        {
                            "activity_type": "fill_in_the_blanks",
                            "questions": {"Q1": "He ___ here."},
                            "answers": {"Q1": "is"},
                        }
                    ],
                },
                "task_type": "fill_in_blanks",
                "task_queue": [{"sequence": 1}],
                "current_task_index": 0,
                "daily_session_id": 0,
            }
        )
    )

    task_event = next(
        event for event in update["outgoing_events"] if event["type"] == "ui_event"
    )
    assert task_event["widget"] == "fill_in_blanks"
    assert task_event["payload"]["instructions"] == "Fill the blanks."
    assert task_event["payload"]["passage"] == "He ___ here."
    assert task_event["payload"]["total_blanks"] == 1
    assert task_event["payload"]["items"][0]["correct_answer"] == "is"


def test_task_delivery_node_derives_blanks_from_passage_only_payload() -> None:
    update = asyncio.run(
        task_delivery_node(
            {
                "task_content": {
                    "widget": "fill_in_blanks",
                    "instructions": "Fill each blank with the correct form of 'to be'.",
                    "passage": "My name ____ John. I ____ a student.",
                    "answers": {"blank_1": "is", "blank_2": "am"},
                },
                "task_type": "fill_in_blanks",
                "task_queue": [{"sequence": 1}],
                "current_task_index": 0,
                "daily_session_id": 0,
            }
        )
    )

    task_event = next(
        event for event in update["outgoing_events"] if event["type"] == "ui_event"
    )
    assert task_event["payload"]["passage"] == "My name ___ John. I ___ a student."
    assert task_event["payload"]["total_blanks"] == 2
    assert [item["blank_id"] for item in task_event["payload"]["items"]] == [
        "blank_1",
        "blank_2",
    ]
    assert [item["correct_answer"] for item in task_event["payload"]["items"]] == [
        "is",
        "am",
    ]


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


def test_authoring_write_open_sent_submission_scores_and_feedbacks(
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "AUTHORING_CHAT_MODE", True)
    evaluator = CaptureEvaluator()
    feedback = CaptureFeedback()
    monkeypatch.setattr(
        "app.modules.learning_session.authoring.get_day",
        lambda week, day_index: _file_day(
            task_archetypes_used=("WRITE_OPEN_SENT",),
            task_specs=(
                {
                    "topic_override": (
                        "Write simple present routine sentences"
                    ),
                    "instructions_override": (
                        "Ask for affirmative routine sentences using "
                        "I/he/she and frequency adverbs."
                    ),
                },
            ),
        ),
    )
    service = _service(
        task=OpenTextRoutineTaskGenerator(),
        evaluator=evaluator,
        feedback=feedback,
    )
    started = asyncio.run(service.start_session(week=1, day=1))
    session = service.store.get(started.session_id)
    assert session is not None
    session.phase = "practice_task"

    async def collect_events():
        return [
            event
            async for event in service.process_message_stream(
                started.session_id,
                WSIncomingMessage(
                    type="task_submission",
                    answers={
                        "routine_i": "I usually study English.",
                        "routine_he": "He often walks to school.",
                        "routine_she": "She always eats breakfast.",
                    },
                ),
            )
        ]

    events = asyncio.run(collect_events())

    assert evaluator.calls[-1]["archetype_id"] == "WRITE_OPEN_SENT"
    assert evaluator.calls[-1]["task_content"]["widget"] == "open_text"
    assert len(evaluator.calls[-1]["task_content"]["items"]) == 3
    scorecard = next(
        event for event in events
        if event.type == "ui_event" and event.widget == "scorecard"
    )
    feedback_card = next(
        event for event in events
        if event.type == "ui_event" and event.widget == "feedback_card"
    )
    assert scorecard.payload["overall_score"] == 8
    assert feedback_card.payload["score"] == 8
    assert feedback_card.payload["widget"] == "open_text"


def test_authoring_teaching_flow_reaches_practice_after_ready(
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "AUTHORING_CHAT_MODE", True)
    fake_llm = FakeTeacherLLM(
        [
            "Hi! Today is about tense. Tell me one real daily routine.",
            "Nice. Use he or she plus verb-s. Ready to try the practice task?",
        ]
    )
    monkeypatch.setattr(
        "app.ai.agents.teacher.get_default_llm_client",
        lambda: fake_llm,
    )
    service = _service()
    started = asyncio.run(service.start_session(week=1, day=1))

    async def collect_initial():
        return [
            event
            async for event in service.initial_messages_stream(started.session_id)
        ]

    initial = asyncio.run(collect_initial())
    assert any(
        event.type == "chat_stream_end"
        and "Tell me one real daily routine" in (event.content or "")
        for event in initial
    )

    async def send_routine():
        return [
            event
            async for event in service.process_message_stream(
                started.session_id,
                WSIncomingMessage(
                    type="user_message",
                    content="I work every morning.",
                ),
            )
        ]

    routine_events = asyncio.run(send_routine())
    assert any(
        event.type == "chat_stream_end"
        and "Ready to try the practice task?" in (event.content or "")
        for event in routine_events
    )

    async def send_ready():
        return [
            event
            async for event in service.process_message_stream(
                started.session_id,
                WSIncomingMessage(type="user_message", content="ready"),
            )
        ]

    ready_events = asyncio.run(send_ready())
    assert any(event.type == "ui_event" for event in ready_events)
    assert service.store.get(started.session_id).phase == "practice_task"
