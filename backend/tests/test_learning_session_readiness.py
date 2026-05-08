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


def test_learning_readiness_does_not_match_ok_inside_books() -> None:
    assert _looks_like_understanding("read books, play football, study") is False


def test_learning_readiness_accepts_explicit_ready_phrases() -> None:
    assert _looks_like_understanding("ok, I am ready") is True
    assert _looks_like_understanding("I understand") is True


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


class _FakeDB:
    def commit(self) -> None:
        pass


class _FakeSessionRepo:
    def save(self, session):
        return session


def _streaming_service() -> LearningSessionService:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = _FakeDB()
    service.session_repo = _FakeSessionRepo()
    return service


def _teaching_session():
    return SimpleNamespace(
        messages=[{"role": "ai", "content": "What do you do on weekends?", "type": "chat"}],
        understanding_confirmed=False,
        phase="teaching",
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
