import asyncio
from types import SimpleNamespace

import pytest

import app.modules.learning_session.service as service_module
from app.ai.agents.teacher import _build_user_prompt
from app.modules.learning_session.schemas import WSIncomingMessage
from app.modules.learning_session.service import (
    LearningSessionService,
    _looks_like_understanding,
)
from app.modules.tasks.models import UserTaskStatus


def test_learning_readiness_does_not_match_ok_inside_books() -> None:
    assert _looks_like_understanding("read books, play football, study") is False


def test_learning_readiness_accepts_explicit_ready_phrases() -> None:
    assert _looks_like_understanding("ok, I am ready") is True
    assert _looks_like_understanding("I understand") is True


def test_learning_readiness_rejects_plain_yes_after_concept_question() -> None:
    assert (
        _looks_like_understanding(
            "yes",
            previous_tutor_message="What kind of routines do you have?",
        )
        is False
    )
    assert (
        _looks_like_understanding(
            "okay",
            previous_tutor_message="How would this sentence change with she?",
        )
        is False
    )


def test_learning_readiness_accepts_ack_after_readiness_question() -> None:
    assert (
        _looks_like_understanding(
            "yes",
            previous_tutor_message="Does this feel clear? Are you ready to practice?",
        )
        is True
    )
    assert (
        _looks_like_understanding(
            "okay",
            previous_tutor_message="If that feels clear, say ready and I will give you the task.",
        )
        is True
    )


def test_learning_readiness_rejects_negated_understanding() -> None:
    assert (
        _looks_like_understanding(
            "i didn't understand the subject and frequency relation"
        )
        is False
    )
    assert _looks_like_understanding("I don't understand this yet") is False
    assert _looks_like_understanding("not ready") is False
    assert _looks_like_understanding("what is a subject?") is False
    assert _looks_like_understanding("I understand now, ready") is True


def test_daily_queue_picks_first_incomplete_task() -> None:
    bundle = [
        SimpleNamespace(id=1, status=UserTaskStatus.COMPLETED),
        SimpleNamespace(id=2, status=UserTaskStatus.PENDING),
        SimpleNamespace(id=3, status=UserTaskStatus.PENDING),
    ]

    assert (
        LearningSessionService._resolve_active_queue_index(
            bundle=bundle,
            requested_user_task_id=None,
        )
        == 1
    )


def test_daily_queue_respects_requested_incomplete_task() -> None:
    bundle = [
        SimpleNamespace(id=1, status=UserTaskStatus.COMPLETED),
        SimpleNamespace(id=2, status=UserTaskStatus.PENDING),
        SimpleNamespace(id=3, status=UserTaskStatus.PENDING),
    ]

    assert (
        LearningSessionService._resolve_active_queue_index(
            bundle=bundle,
            requested_user_task_id=3,
        )
        == 2
    )


class _FakeDB:
    def commit(self) -> None:
        pass


class _FakeSessionRepo:
    def save(self, session):
        return session


class _FakeSession(SimpleNamespace):
    current_task_index: int = 0
    enrollment_id: int | None = None


def _streaming_service() -> LearningSessionService:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = _FakeDB()
    service.session_repo = _FakeSessionRepo()
    return service


def _teaching_session():
    return _FakeSession(
        messages=[{"role": "ai", "content": "What do you do on weekends?", "type": "chat"}],
        understanding_confirmed=False,
        phase="teaching",
        current_task_index=0,
    )


def _teaching_state(session) -> dict:
    return {
        "phase": "teaching",
        "messages": list(session.messages),
        "topic": "Present Simple",
        "skill_name": "grammar",
        "task_type": "fill_in_blanks",
        "user_level": 5,
        "learner_profile": {},
    }


@pytest.mark.asyncio
async def test_teacher_streams_back_after_intro_answer(monkeypatch) -> None:
    async def fake_stream_teaching_turn(**kwargs):
        yield "Nice answer. "
        yield "For a habit, say I play football."

    monkeypatch.setattr(
        service_module, "stream_teaching_turn", fake_stream_teaching_turn
    )
    service = _streaming_service()
    session = _teaching_session()
    incoming = WSIncomingMessage(
        type="user_message",
        content="i go to play football, basket ball and badminton.",
    )

    events = [
        event
        async for event in service._handle_user_message_stream(
            session, _teaching_state(session), incoming
        )
    ]

    assert [event.type for event in events] == [
        "chat_stream_start",
        "chat_stream_delta",
        "chat_stream_delta",
        "chat_stream_end",
    ]
    assert events[-1].content == "Nice answer. For a habit, say I play football."
    assert session.messages[-1]["content"] == events[-1].content


@pytest.mark.asyncio
async def test_teacher_stream_timeout_falls_back(monkeypatch) -> None:
    async def stuck_stream_teaching_turn(**kwargs):
        await asyncio.sleep(60)
        yield "too late"

    monkeypatch.setattr(
        service_module, "stream_teaching_turn", stuck_stream_teaching_turn
    )
    monkeypatch.setattr(
        service_module, "_TEACHING_STREAM_FIRST_CHUNK_TIMEOUT_S", 0.01
    )
    service = _streaming_service()
    session = _teaching_session()
    incoming = WSIncomingMessage(
        type="user_message",
        content="i go to play football, basket ball and badminton.",
    )

    events = [
        event
        async for event in service._handle_user_message_stream(
            session, _teaching_state(session), incoming
        )
    ]

    assert events[0].type == "chat_stream_start"
    assert events[-1].type == "chat_stream_end"
    assert "turn it into a full present-simple sentence" in events[-1].content


def test_teacher_fallback_advances_by_learner_turn_count() -> None:
    state = {
        "topic": "Present Simple",
        "messages": [
            {"role": "ai", "content": "What do you do every day?", "type": "chat"},
            {"role": "user", "content": "I read.", "type": "chat"},
            {"role": "ai", "content": "What about she?", "type": "chat"},
            {"role": "user", "content": "She reads.", "type": "chat"},
            {"role": "ai", "content": "Add a frequency word.", "type": "chat"},
            {"role": "user", "content": "She often reads.", "type": "chat"},
        ],
    }

    fallback = LearningSessionService._teaching_fallback_for_state(state)

    assert "frequency clue" in fallback
    assert "always, often, or a few times a week" in fallback


@pytest.mark.asyncio
async def test_teacher_forces_readiness_checkpoint_after_enough_concept_turns(
    monkeypatch,
) -> None:
    async def should_not_stream_teaching_turn(**kwargs):
        raise AssertionError("teacher should ask readiness, not another probe")
        yield ""

    monkeypatch.setattr(
        service_module, "stream_teaching_turn", should_not_stream_teaching_turn
    )
    service = _streaming_service()
    session = _FakeSession(
        messages=[
            {"role": "ai", "content": "What routine do you have?", "type": "chat"},
            {"role": "user", "content": "yes", "type": "chat"},
            {"role": "ai", "content": "Use we with a base verb.", "type": "chat"},
            {"role": "user", "content": "we play cricket", "type": "chat"},
            {"role": "ai", "content": "Now try he or she.", "type": "chat"},
            {"role": "user", "content": "he sings well", "type": "chat"},
            {"role": "ai", "content": "Add a frequency word.", "type": "chat"},
        ],
        understanding_confirmed=False,
        phase="teaching",
        current_task_index=0,
    )
    state = {
        "phase": "teaching",
        "messages": list(session.messages),
        "topic": "Present Simple",
        "skill_name": "grammar",
        "task_type": "fill_in_blanks",
        "user_level": 5,
        "learner_profile": {},
    }

    events = [
        event
        async for event in service._handle_user_message_stream(
            session,
            state,
            WSIncomingMessage(type="user_message", content="he sings often"),
        )
    ]

    assert events[-1].type == "chat_stream_end"
    assert "Does this feel clear enough to start the practice task?" in events[-1].content
    assert session.phase == "teaching"


@pytest.mark.asyncio
async def test_teacher_does_not_force_readiness_when_latest_turn_is_question(
    monkeypatch,
) -> None:
    async def fake_stream_teaching_turn(**kwargs):
        yield "Good question. "
        yield "The subject is the person or thing doing the action."

    monkeypatch.setattr(
        service_module, "stream_teaching_turn", fake_stream_teaching_turn
    )
    service = _streaming_service()
    session = _FakeSession(
        messages=[
            {"role": "ai", "content": "What routine do you have?", "type": "chat"},
            {"role": "user", "content": "we play cricket", "type": "chat"},
            {"role": "ai", "content": "Now try he or she.", "type": "chat"},
            {"role": "user", "content": "he sings well", "type": "chat"},
            {"role": "ai", "content": "Add a frequency word.", "type": "chat"},
            {"role": "user", "content": "he sings often", "type": "chat"},
            {"role": "ai", "content": "Find the subject first.", "type": "chat"},
        ],
        understanding_confirmed=False,
        phase="teaching",
        current_task_index=0,
    )
    state = {
        "phase": "teaching",
        "messages": list(session.messages),
        "topic": "Present Simple",
        "skill_name": "grammar",
        "task_type": "fill_in_blanks",
        "user_level": 5,
        "learner_profile": {},
    }

    events = [
        event
        async for event in service._handle_user_message_stream(
            session,
            state,
            WSIncomingMessage(type="user_message", content="what is subject?"),
        )
    ]

    assert events[-1].type == "chat_stream_end"
    assert "person or thing doing the action" in events[-1].content


@pytest.mark.asyncio
async def test_end_session_farewell_offers_dashboard_action() -> None:
    service = _streaming_service()
    session = _teaching_session()
    state = {
        "messages": [
            {"role": "user", "content": "End session", "type": "chat"},
        ],
    }

    events = [
        event
        async for event in service._stream_followup_response(
            session,
            state,
            "End session",
        )
    ]

    assert events[-1].type == "chat_stream_end"
    assert events[-1].actions == ["Go to dashboard"]
    assert session.phase == "ended"


@pytest.mark.asyncio
async def test_next_activity_streams_next_queued_task() -> None:
    service = _streaming_service()
    service.user_task_repo = SimpleNamespace(
        get_by_id=lambda user_task_id: SimpleNamespace(
            id=user_task_id,
            task_id=20,
            status=SimpleNamespace(value="pending"),
            completed_at=None,
            task=SimpleNamespace(
                title="Second activity",
                task_type=SimpleNamespace(value="fill_in_blanks"),
                difficulty=5,
                content={"widget": "fill_in_blanks", "items": []},
                task_skills=[],
            ),
        )
    )
    session = _FakeSession(
        session_id="daily-session",
        user_id=1,
        messages=[],
        phase="feedback",
        current_task_index=0,
        task_queue=[
            {"user_task_id": 1, "sequence_index": 0, "status": "completed"},
            {"user_task_id": 2, "sequence_index": 1, "status": "pending"},
        ],
        user_task_id=1,
        user_submission={"b1": "go"},
        evaluation={"percentage": 80},
        feedback={"overall_message": "Nice"},
        understanding_confirmed=True,
    )
    state = {
        "messages": [{"role": "user", "content": "Next activity", "type": "chat"}],
        "task_queue": list(session.task_queue),
        "current_task_index": 0,
    }

    events = [
        event
        async for event in service._stream_followup_response(
            session,
            state,
            "Next activity",
        )
    ]

    assert events[0].type == "chat_stream_start"
    assert any(event.type == "chat_stream_end" for event in events)
    assert events[-1].type == "ui_event"
    assert events[-1].widget == "fill_in_blanks"
    assert session.phase == "practice_task"
    assert session.current_task_index == 1


@pytest.mark.asyncio
async def test_queued_submission_keeps_scorecard(monkeypatch) -> None:
    async def fake_evaluation_node(state):
        return {
            "phase": "scorecard",
            "evaluation": {"percentage": 50, "total": 2, "correct_count": 1},
            "outgoing_events": [
                {
                    "type": "ui_event",
                    "widget": "scorecard",
                    "payload": {"overall_score": 50},
                }
            ],
            "messages": list(state.get("messages", []))
            + [{"role": "ai", "content": "[scorecard delivered]", "type": "ui_event"}],
        }

    async def fake_feedback_node(state):
        return {
            "phase": "feedback",
            "feedback": {"overall_message": "Review this one.", "errors": [], "score": 50},
            "outgoing_events": [
                {
                    "type": "ui_event",
                    "widget": "feedback_card",
                    "payload": {"overall_message": "Review this one.", "errors": [], "score": 50},
                },
                {
                    "type": "chat_message",
                    "role": "assistant",
                    "content": "Review this one.",
                    "actions": ["Next activity", "Go to dashboard"],
                },
            ],
            "messages": list(state.get("messages", [])),
        }

    monkeypatch.setattr(service_module, "evaluation_node", fake_evaluation_node)
    monkeypatch.setattr(service_module, "feedback_node", fake_feedback_node)

    service = _streaming_service()
    session = _FakeSession(
        messages=[],
        user_submission=None,
        phase="practice_task",
        current_task_index=1,
    )
    state = {
        "messages": [],
        "current_task_index": 1,
        "task_content": {"items": []},
        "task_type": "fill_in_blanks",
    }

    events = [
        event
        async for event in service._handle_task_submission_stream(
            session,
            state,
            WSIncomingMessage(type="task_submission", answers={"b1": "go"}),
        )
    ]

    assert [event.widget for event in events if event.type == "ui_event"] == [
        "scorecard",
        "feedback_card"
    ]


@pytest.mark.asyncio
async def test_question_answer_checks_if_doubt_is_clarified(monkeypatch) -> None:
    async def fake_stream_answer_question(state, question):
        yield "A tense shows when an action happens."

    monkeypatch.setattr(
        service_module,
        "stream_answer_question",
        fake_stream_answer_question,
    )
    service = _streaming_service()
    session = _FakeSession(messages=[], phase="follow_up", current_task_index=0)
    state = {"messages": [{"role": "user", "content": "What is tense?", "type": "chat"}]}

    events = [
        event
        async for event in service._stream_followup_response(
            session,
            state,
            "What is tense?",
        )
    ]

    assert events[-1].content.endswith("Did that clarify your doubt?")
    assert session.phase == "follow_up"


@pytest.mark.asyncio
async def test_yes_after_clarified_doubt_shows_followup_actions() -> None:
    service = _streaming_service()
    session = _FakeSession(messages=[], phase="follow_up", current_task_index=0)
    state = {
        "messages": [
            {
                "role": "ai",
                "content": "A tense shows when an action happens. Did that clarify your doubt?",
                "type": "chat",
            },
            {"role": "user", "content": "yes", "type": "chat"},
        ]
    }

    events = [
        event
        async for event in service._stream_followup_response(session, state, "yes")
    ]

    assert events[-1].actions == ["Go to dashboard"]
    assert session.phase == "feedback"


def test_teacher_prompt_uses_recent_turns_and_blocks_repetition() -> None:
    prompt = _build_user_prompt(
        topic="Present Simple",
        sub_skill="grammar",
        task_type="fill_in_blanks",
        user_level=5,
        learner_profile={},
        conversation=[
            {
                "role": "ai",
                "content": (
                    "What do you think is an example of a daily routine "
                    "using the Present Simple?"
                ),
                "type": "chat",
            },
            {
                "role": "user",
                "content": "I go for a walk every day",
                "type": "chat",
            },
        ],
        stream_text=True,
    )

    assert "Recent conversation:" in prompt
    assert "Teaching agenda:" in prompt
    assert "Current teaching target: base_verb_subjects" in prompt
    assert "Tutor: What do you think is an example" in prompt
    assert "Learner: I go for a walk every day" in prompt
    assert "Do not restate the opening explanation" in prompt
    assert "Ask a new probing question" in prompt
    assert "not another personal preference question" in prompt


def test_teacher_prompt_warns_against_treating_ack_as_concept_answer() -> None:
    prompt = _build_user_prompt(
        topic="Present Simple",
        sub_skill="grammar",
        task_type="fill_in_blanks",
        user_level=5,
        learner_profile={},
        conversation=[
            {"role": "ai", "content": "What kind of routines do you have?", "type": "chat"},
            {"role": "user", "content": "yes", "type": "chat"},
        ],
        stream_text=True,
    )

    assert "Plain acknowledgements like \"yes\", \"yeah\", \"ok\", or \"okay\"" in prompt
    assert "Do not treat them as answers to concept-check questions" in prompt


def test_teacher_prompt_advances_to_next_concept_after_multiple_turns() -> None:
    prompt = _build_user_prompt(
        topic="Present Simple",
        sub_skill="grammar",
        task_type="fill_in_blanks",
        user_level=5,
        learner_profile={},
        conversation=[
            {"role": "ai", "content": "What do you do every day?", "type": "chat"},
            {"role": "user", "content": "I go for a walk.", "type": "chat"},
            {"role": "ai", "content": "What changes with he or she?", "type": "chat"},
            {"role": "user", "content": "She goes for a walk.", "type": "chat"},
        ],
        stream_text=True,
    )

    assert "Current teaching target: third_person_s" in prompt
    assert "frequency_clues (upcoming)" in prompt


def test_teacher_prompt_pauses_for_clarification() -> None:
    prompt = _build_user_prompt(
        topic="Present Simple",
        sub_skill="grammar",
        task_type="fill_in_blanks",
        user_level=5,
        learner_profile={},
        conversation=[
            {"role": "ai", "content": "Do you feel ready to practice?", "type": "chat"},
            {
                "role": "user",
                "content": "i didn't understand the subject and frequency relation",
                "type": "chat",
            },
        ],
        stream_text=True,
    )

    assert "Current teaching target: clarify_confusion" in prompt
    assert "Learner needs clarification: yes" in prompt
    assert "Do not move to the practice task" in prompt
    assert "Do not ask if they are ready in this turn" in prompt
