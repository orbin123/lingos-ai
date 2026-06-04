"""Unit coverage for the file-mode helpers on `LearningSessionService`.

The full `create_session` end-to-end test would require a Postgres
fixture (the `LearningSession` model uses JSONB columns that SQLite
can't compile), so we exercise the file-mode branch points in
isolation:

  - `_parse_day_id` decodes the `day_24_WW_DD` format file_source emits.
  - `_persona_from_file` reads `source_24w.py` and stashes
    `__scripted_plan` inside the returned teacher_instructions dict.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.curriculum.data.source_24w import WEEKS_24
from app.modules.curriculum.file_source import get_day_by_id as file_get_day_by_id
from app.modules.learning_session.service import (
    LearningSessionService,
    _parse_day_id,
    _looks_like_ready_for_practice,
    _should_force_transition_to_practice,
    _tutor_asked_readiness,
)
from app.modules.learning_session.schemas import WSIncomingMessage, WSOutgoingMessage
from app.modules.sessions.exceptions import DayNotFound
from app.modules.sessions.models import AttemptStatus, SessionStatus


def _mock_no_existing_scorecard(monkeypatch) -> None:
    scorecard_repo = MagicMock()
    scorecard_repo.return_value.get_for_session.return_value = None
    monkeypatch.setattr(
        "app.modules.learning_session.service.ScorecardRepository",
        scorecard_repo,
    )


def _teacher_script(day) -> list[str]:
    return [step.instruction for step in day.teacher.steps]


def test_parse_day_id_returns_week_and_day_numbers() -> None:
    assert _parse_day_id("day_24_01_01") == (1, 1)
    assert _parse_day_id("day_24_05_03") == (5, 3)
    assert _parse_day_id("day_48_12_07") == (12, 7)


def test_parse_day_id_rejects_garbage() -> None:
    with pytest.raises(ValueError):
        _parse_day_id("not-a-day-id")
    with pytest.raises(ValueError):
        _parse_day_id("day_24_1_1")  # numbers must be zero-padded


def test_persona_from_file_returns_w1d1_and_stashes_scripted_plan() -> None:
    # `_persona_from_file` is a method but doesn't touch self.db / repos,
    # so we can call it on an unbound instance via __get__-style trick:
    persona = LearningSessionService._persona_from_file
    topic, skill_name, sub_level, instr = persona(None, "day_24_01_01")  # type: ignore[arg-type]

    w1d1 = WEEKS_24[0].days[0]
    assert topic == w1d1.title
    assert skill_name == "grammar"
    assert sub_level == WEEKS_24[0].sub_level_min

    # The reserved key carries the authored scripted lines verbatim.
    assert isinstance(instr, dict)
    assert instr["__scripted_plan"] == _teacher_script(w1d1)

    assert instr["lesson_description"] == w1d1.description
    assert "learning_goal" not in instr
    assert "sub_skill_context" not in instr


def test_persona_from_file_returns_w1d2_and_stashes_scripted_plan() -> None:
    persona = LearningSessionService._persona_from_file
    topic, skill_name, sub_level, instr = persona(None, "day_24_01_02")  # type: ignore[arg-type]

    w1d2 = WEEKS_24[0].days[1]
    assert topic == w1d2.title
    assert skill_name == "grammar"
    assert sub_level == WEEKS_24[0].sub_level_min
    assert isinstance(instr, dict)
    assert instr["__scripted_plan"] == _teacher_script(w1d2)
    assert instr["lesson_description"] == w1d2.description
    assert "Simple Past Tense" in topic


def test_persona_from_file_blank_day_raises() -> None:
    persona = LearningSessionService._persona_from_file
    # All 24 weeks are authored; invalid day_id is refused by file_source.
    with pytest.raises(DayNotFound):
        persona(None, "day_24_99_01")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_resume_auto_completes_all_evaluated_daily_session(monkeypatch) -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.attempts_repo = MagicMock()

    chat = MagicMock()
    chat.session_id = "chat-session"
    chat.daily_session_id = 42
    chat.user_id = 7
    chat.task_queue = [{"status": "pending"}]
    chat.current_task_index = 0
    chat.phase = "feedback"

    daily_open = MagicMock()
    daily_open.id = 42
    daily_open.session_id = "daily-session"
    daily_open.status = SessionStatus.IN_PROGRESS
    daily_done = MagicMock()
    daily_done.status = SessionStatus.COMPLETED
    service.db.get.side_effect = [daily_open, daily_done]

    service.attempts_repo.list_for_session.return_value = [
        MagicMock(status=AttemptStatus.EVALUATED),
        MagicMock(status=AttemptStatus.EVALUATED),
    ]
    service._load_session = MagicMock(return_value=chat)
    service._state_from_row = MagicMock(return_value={})
    service._enrich_state_with_profile = MagicMock()
    service._sync_task_queue_from_attempts = MagicMock()

    v2_service = MagicMock()
    v2_service.complete_session = AsyncMock()
    monkeypatch.setattr(
        "app.modules.learning_session.service._make_v2_session_service",
        MagicMock(return_value=v2_service),
    )
    _mock_no_existing_scorecard(monkeypatch)

    messages = [
        msg async for msg in service.resume_messages_stream("chat-session")
    ]

    v2_service.complete_session.assert_awaited_once_with(
        session_id="daily-session",
        user_id=7,
    )
    assert messages[-1].actions == ["Go to dashboard"]
    assert "Next activity" not in (messages[-1].actions or [])


@pytest.mark.asyncio
async def test_initial_open_auto_completes_all_evaluated_daily_session(monkeypatch) -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.attempts_repo = MagicMock()

    chat = MagicMock()
    chat.session_id = "chat-session"
    chat.daily_session_id = 42
    chat.user_id = 7

    daily_open = MagicMock()
    daily_open.id = 42
    daily_open.session_id = "daily-session"
    daily_open.status = SessionStatus.IN_PROGRESS
    daily_done = MagicMock()
    daily_done.status = SessionStatus.COMPLETED
    service.db.get.side_effect = [daily_open, daily_done]

    service.attempts_repo.list_for_session.return_value = [
        MagicMock(status=AttemptStatus.EVALUATED),
        MagicMock(status=AttemptStatus.EVALUATED),
    ]
    service._load_session = MagicMock(return_value=chat)
    service._state_from_row = MagicMock(return_value={})
    service._enrich_state_with_profile = MagicMock()
    service._sync_task_queue_from_attempts = MagicMock()
    service._stream_teaching_turn = MagicMock()

    v2_service = MagicMock()
    v2_service.complete_session = AsyncMock()
    monkeypatch.setattr(
        "app.modules.learning_session.service._make_v2_session_service",
        MagicMock(return_value=v2_service),
    )
    _mock_no_existing_scorecard(monkeypatch)

    messages = [
        msg async for msg in service.initial_messages_stream("chat-session")
    ]

    v2_service.complete_session.assert_awaited_once_with(
        session_id="daily-session",
        user_id=7,
    )
    service._stream_teaching_turn.assert_not_called()
    assert messages[-1].actions == ["Go to dashboard"]


@pytest.mark.asyncio
async def test_resume_keeps_next_activity_when_attempt_is_pending(monkeypatch) -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.attempts_repo = MagicMock()

    chat = MagicMock()
    chat.session_id = "chat-session"
    chat.daily_session_id = 42
    chat.user_id = 7
    chat.task_queue = [{"status": "pending"}]
    chat.current_task_index = 0
    chat.phase = "feedback"

    daily = MagicMock()
    daily.id = 42
    daily.status = SessionStatus.IN_PROGRESS
    service.db.get.return_value = daily
    service.attempts_repo.list_for_session.return_value = [
        MagicMock(status=AttemptStatus.PENDING)
    ]
    service._load_session = MagicMock(return_value=chat)
    service._state_from_row = MagicMock(return_value={})
    service._enrich_state_with_profile = MagicMock()
    service._sync_task_queue_from_attempts = MagicMock()

    make_v2 = MagicMock()
    monkeypatch.setattr(
        "app.modules.learning_session.service._make_v2_session_service",
        make_v2,
    )

    messages = [
        msg async for msg in service.resume_messages_stream("chat-session")
    ]

    make_v2.assert_not_called()
    assert messages[-1].actions == ["Next activity", "Go to dashboard"]


# ── Full create_session flow (no DB) ───────────────────────────────────────


def _fake_attempt(*, archetype_id: str, sequence: int) -> MagicMock:
    """Quack like an ActivityAttempt for `_queue_from_attempts`."""
    a = MagicMock()
    a.archetype_id = archetype_id
    a.sequence = sequence
    a.is_mandatory = True
    a.status = AttemptStatus.PENDING
    a.task_content = {
        "archetype_id": archetype_id,
        "widget": "fill_in_blanks",
        "ui_widget": "FillInBlanks",
        "activity_contract": {
            "activity_id": f"activity-{sequence}",
            "sequence": sequence,
            "archetype_id": archetype_id,
            "task_widget": "fill_in_blanks",
            "evaluation_widget": "activity_score",
            "feedback_widget": "feedback_card",
        },
    }
    return a


def _w1d1_task_queue() -> list[dict]:
    day = file_get_day_by_id("day_24_01_01")
    queue = []
    for contract in day.activity_contracts:
        queue.append(
            {
                "sequence": contract["sequence"],
                "archetype_id": contract["archetype_id"],
                "is_mandatory": contract["mandatory"],
                "status": "pending",
                "activity_id": contract["activity_id"],
                "task_widget": contract["task_widget"],
                "evaluator_type": contract["evaluator_type"],
                "evaluation_widget": contract["evaluation_widget"],
                "feedback_type": contract["feedback_type"],
                "feedback_widget": contract["feedback_widget"],
                "activity_contract": dict(contract),
            }
        )
    return queue


def _w1d1_chat(*, phase: str = "teaching") -> MagicMock:
    day = file_get_day_by_id("day_24_01_01")
    chat = MagicMock()
    chat.session_id = "chat-w1d1"
    chat.daily_session_id = 42
    chat.user_id = 7
    chat.phase = phase
    chat.topic = day.topic
    chat.skill_name = day.theme_type
    chat.task_type = "read"
    chat.activity_type = "read"
    chat.user_level = day.sub_level_min
    chat.teacher_instructions = dict(day.teacher_instructions)
    chat.task_queue = _w1d1_task_queue()
    chat.current_task_index = 0
    chat.messages = []
    chat.pre_generated_tasks = {}
    chat.user_submission = None
    chat.evaluation = None
    chat.feedback = None
    chat.understanding_confirmed = False
    chat.current_activity_order = 1
    return chat


def _w1d1_daily() -> MagicMock:
    daily = MagicMock()
    daily.id = 42
    daily.session_id = "daily-w1d1"
    daily.day_id = "day_24_01_01"
    daily.status = SessionStatus.IN_PROGRESS
    return daily


async def _one_teaching_message(session, state):  # noqa: ANN001
    yield WSOutgoingMessage(
        type="chat_message",
        role="assistant",
        content="Welcome to simple present.",
    )


def _assert_w1d1_blueprint_event(message) -> None:  # noqa: ANN001
    day = file_get_day_by_id("day_24_01_01")

    assert message.type == "ui_event"
    assert message.widget == "session_blueprint"
    assert message.phase == "teaching"
    assert message.payload_kind == "session_blueprint"
    assert message.event_id

    payload = message.payload
    assert payload["phase"] == "teaching"
    assert payload["payload_kind"] == "session_blueprint"
    blueprint = payload["blueprint"]
    assert blueprint["version"] == "learning_session.event.v1"
    assert blueprint["teaching"]["teacher_style"] == day.teacher_instructions[
        "teacher_style"
    ]
    assert blueprint["teaching"]["lesson_goal"] == day.teacher_instructions[
        "lesson_goal"
    ]
    assert blueprint["teaching"]["readiness_prompt"] == day.teacher_instructions[
        "readiness_prompt"
    ]
    assert len(blueprint["teaching"]["steps"]) == len(day.teacher_agent_behaviour)
    assert blueprint["activities"] == list(day.activity_contracts)
    assert blueprint["final_review"] == {
        "scorecard_widget": "final_scorecard",
        "rag_feedback_widget": "rag_feedback",
    }


def test_queue_from_attempts_remembers_runtime_blueprint_contract() -> None:
    queue = LearningSessionService._queue_from_attempts(
        [
            _fake_attempt(archetype_id="READ_CLOZE", sequence=1),
            _fake_attempt(archetype_id="WRITE_OPEN_SENT", sequence=2),
        ]
    )

    assert queue[0]["sequence"] == 1
    assert queue[0]["activity_id"] == "activity-1"
    assert queue[0]["task_widget"] == "fill_in_blanks"
    assert queue[0]["evaluation_widget"] == "activity_score"
    assert queue[0]["feedback_widget"] == "feedback_card"
    assert queue[0]["activity_contract"]["archetype_id"] == "READ_CLOZE"


@pytest.mark.asyncio
async def test_initial_stream_emits_session_blueprint_before_teaching() -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service._load_session = MagicMock(return_value=_w1d1_chat())
    service._state_from_row = MagicMock()
    service._enrich_state_with_profile = MagicMock()
    service._auto_complete_daily_if_ready = AsyncMock(return_value=_w1d1_daily())
    service._stream_teaching_turn = _one_teaching_message
    service.db.get.return_value = _w1d1_daily()

    state = {
        "task_queue": _w1d1_task_queue(),
        "messages": [],
        "daily_plan": {},
    }
    service._state_from_row.return_value = state

    messages = [
        msg async for msg in service.initial_messages_stream("chat-w1d1")
    ]

    _assert_w1d1_blueprint_event(messages[0])
    assert messages[1].type == "chat_message"


@pytest.mark.asyncio
async def test_resume_stream_emits_session_blueprint_before_replay() -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    chat = _w1d1_chat()
    chat.messages = [
        {
            "role": "ai",
            "content": "Welcome back. Ready to try the practice task?",
            "type": "chat",
        }
    ]
    service._load_session = MagicMock(return_value=chat)
    service._state_from_row = MagicMock()
    service._enrich_state_with_profile = MagicMock()
    service._sync_task_queue_from_attempts = MagicMock()
    service._auto_complete_daily_if_ready = AsyncMock(return_value=_w1d1_daily())
    service.db.get.return_value = _w1d1_daily()
    service._state_from_row.return_value = {
        "task_queue": _w1d1_task_queue(),
        "messages": chat.messages,
        "daily_plan": {},
    }

    messages = [
        msg async for msg in service.resume_messages_stream("chat-w1d1")
    ]

    _assert_w1d1_blueprint_event(messages[0])
    assert messages[1].type == "chat_stream_start"


@pytest.mark.asyncio
async def test_create_session_file_mode_skips_planner_and_persists_script(
    monkeypatch,
) -> None:
    """End-to-end coverage of ``create_session`` when a file-authored day exists.

    Uses mocks instead of a real DB so we can verify two things without
    spinning up Postgres:
      1. ``PlannerAgent.generate`` is never awaited.
      2. The ``session_repo.create`` call receives teacher_instructions
         that carry ``__scripted_plan`` matching W1D1's authored
         ``teacher_agent_behaviour``.
    """

    async def _explode(*args, **kwargs):
        raise AssertionError("PlannerAgent.generate must not be called in file mode")

    monkeypatch.setattr(
        "app.modules.learning_session.service.PlannerAgent.generate", _explode,
    )

    # Build a service whose repos are all mocks so no DB is touched.
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.session_repo = MagicMock()
    service.daily_repo = MagicMock()
    service.attempts_repo = MagicMock()
    service.curriculum_day_repo = MagicMock()
    service.archetype_repo = MagicMock()
    service.profile_repo = MagicMock()

    daily = MagicMock()
    daily.id = 42
    daily.session_id = "ds-uuid"
    daily.day_id = "day_24_01_01"

    # `_resolve_daily_session` is async — replace with an async stub.
    async def _resolve(*, user_id, daily_session_id):  # noqa: ARG001
        return daily
    service._resolve_daily_session = _resolve  # type: ignore[method-assign]

    service.session_repo.get_by_daily_session_id.return_value = None
    service.attempts_repo.list_for_session.return_value = [
        _fake_attempt(archetype_id="READ_CLOZE", sequence=1),
        _fake_attempt(archetype_id="WRITE_OPEN_SENT", sequence=2),
    ]

    response = await service.create_session(user_id=7, daily_session_id=None)

    assert response.session_id
    assert response.daily_session_id == 42

    # `session_repo.create` was called once with the file-derived persona.
    service.session_repo.create.assert_called_once()
    kwargs = service.session_repo.create.call_args.kwargs

    w1d1 = WEEKS_24[0].days[0]
    assert kwargs["topic"] == w1d1.title
    assert kwargs["skill_name"] == "grammar"
    assert kwargs["user_level"] == WEEKS_24[0].sub_level_min
    assert kwargs["activity_type"] == "read"  # READ_CLOZE → read

    instr = kwargs["teacher_instructions"]
    assert isinstance(instr, dict)
    assert instr["__scripted_plan"] == _teacher_script(w1d1)
    assert instr["lesson_description"] == w1d1.description
    assert "lesson_context" not in instr


@pytest.mark.asyncio
async def test_create_session_db_mode_uses_source_persona_for_authored_w1d1(
    monkeypatch,
) -> None:

    async def _explode(*args, **kwargs):
        raise AssertionError("PlannerAgent.generate must not run for sourced W1D1")

    monkeypatch.setattr(
        "app.modules.learning_session.service.PlannerAgent.generate", _explode,
    )

    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.session_repo = MagicMock()
    service.daily_repo = MagicMock()
    service.attempts_repo = MagicMock()
    service.curriculum_day_repo = MagicMock()
    service.archetype_repo = MagicMock()
    service.profile_repo = MagicMock()

    daily = MagicMock()
    daily.id = 42
    daily.session_id = "ds-uuid"
    daily.day_id = "day_24_01_01"

    async def _resolve(*, user_id, daily_session_id):  # noqa: ARG001
        return daily
    service._resolve_daily_session = _resolve  # type: ignore[method-assign]

    service.session_repo.get_by_daily_session_id.return_value = None
    service.attempts_repo.list_for_session.return_value = [
        _fake_attempt(archetype_id="READ_CLOZE", sequence=1),
    ]

    await service.create_session(user_id=7, daily_session_id=None)

    kwargs = service.session_repo.create.call_args.kwargs
    w1d1 = WEEKS_24[0].days[0]
    assert kwargs["topic"] == w1d1.title
    assert kwargs["skill_name"] == "grammar"
    assert kwargs["teacher_instructions"]["__scripted_plan"] == _teacher_script(w1d1)
    assert "subject-verb" in kwargs["teacher_instructions"]["lesson_description"]


@pytest.mark.asyncio
async def test_create_session_file_mode_uses_source_persona_for_authored_w1d2(
    monkeypatch,
) -> None:

    async def _explode(*args, **kwargs):
        raise AssertionError("PlannerAgent.generate must not run for sourced W1D2")

    monkeypatch.setattr(
        "app.modules.learning_session.service.PlannerAgent.generate", _explode,
    )

    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.session_repo = MagicMock()
    service.daily_repo = MagicMock()
    service.attempts_repo = MagicMock()
    service.curriculum_day_repo = MagicMock()
    service.archetype_repo = MagicMock()
    service.profile_repo = MagicMock()

    daily = MagicMock()
    daily.id = 43
    daily.session_id = "ds-uuid-w1d2"
    daily.day_id = "day_24_01_02"

    async def _resolve(*, user_id, daily_session_id):  # noqa: ARG001
        return daily
    service._resolve_daily_session = _resolve  # type: ignore[method-assign]

    service.session_repo.get_by_daily_session_id.return_value = None
    service.attempts_repo.list_for_session.return_value = [
        _fake_attempt(archetype_id="READ_ERROR_SPOT", sequence=1),
    ]

    await service.create_session(user_id=7, daily_session_id=None)

    kwargs = service.session_repo.create.call_args.kwargs
    w1d2 = WEEKS_24[0].days[1]
    assert kwargs["topic"] == w1d2.title
    assert kwargs["skill_name"] == "grammar"
    assert kwargs["teacher_instructions"]["__scripted_plan"] == _teacher_script(w1d2)
    assert "completed actions" in kwargs["teacher_instructions"]["lesson_description"]


def test_resume_refreshes_stale_w1d2_chat_persona() -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.session_repo = MagicMock()

    session = MagicMock()
    session.topic = "Simple Present Tense"
    session.skill_name = "grammar"
    session.user_level = 1
    session.teacher_instructions = {"lesson_description": "Old day 1 content"}

    refreshed = service._maybe_refresh_file_persona(
        session,
        "day_24_01_02",
    )

    w1d2 = WEEKS_24[0].days[1]
    assert refreshed is True
    assert session.topic == w1d2.title
    assert session.skill_name == "grammar"
    assert session.user_level == WEEKS_24[0].sub_level_min
    assert session.teacher_instructions["__scripted_plan"] == _teacher_script(w1d2)
    assert session.teacher_instructions["lesson_description"] == w1d2.description
    service.session_repo.save.assert_called_once_with(session)
    service.db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_session_resume_refreshes_existing_w1d2_chat_persona() -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.session_repo = MagicMock()
    service.daily_repo = MagicMock()
    service.attempts_repo = MagicMock()

    daily = MagicMock()
    daily.id = 43
    daily.day_id = "day_24_01_02"

    existing = MagicMock()
    existing.session_id = "chat-w1d2"
    existing.topic = "Simple Present Tense"
    existing.skill_name = "grammar"
    existing.user_level = 1
    existing.task_type = "read"
    existing.teacher_instructions = {"lesson_description": "Old day 1 content"}

    async def _resolve(*, user_id, daily_session_id):  # noqa: ARG001
        return daily
    service._resolve_daily_session = _resolve  # type: ignore[method-assign]
    service.session_repo.get_by_daily_session_id.return_value = existing

    response = await service.create_session(user_id=7, daily_session_id=None)

    w1d2 = WEEKS_24[0].days[1]
    assert response.message == "Session resumed"
    assert response.topic == w1d2.title
    assert existing.teacher_instructions["__scripted_plan"] == _teacher_script(w1d2)
    service.session_repo.save.assert_called_once_with(existing)
    service.db.commit.assert_called_once()


def test_restart_refreshes_w1d2_chat_persona_without_immediate_commit() -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.session_repo = MagicMock()

    session = MagicMock()
    session.topic = "Old DB topic"
    session.skill_name = "old"
    session.user_level = 9
    session.teacher_instructions = {"lesson_description": "Old DB brief"}

    refreshed = service._maybe_refresh_file_persona(
        session,
        "day_24_01_02",
        commit=False,
    )

    w1d2 = WEEKS_24[0].days[1]
    assert refreshed is True
    assert session.topic == w1d2.title
    assert session.teacher_instructions["__scripted_plan"] == _teacher_script(w1d2)
    service.session_repo.save.assert_called_once_with(session)
    service.db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_restart_session_refreshes_w1d2_chat_persona(monkeypatch) -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.session_repo = MagicMock()
    service.curriculum_day_repo = MagicMock()
    service.archetype_repo = MagicMock()
    service.profile_repo = MagicMock()

    session = MagicMock()
    session.session_id = "chat-w1d2"
    session.daily_session_id = 43
    session.user_id = 7
    session.topic = "Old DB topic"
    session.skill_name = "old"
    session.user_level = 9
    session.task_type = "read"
    session.task_queue = []
    session.teacher_instructions = {"lesson_description": "Old DB brief"}

    daily = MagicMock()
    daily.id = 43
    daily.session_id = "daily-w1d2"
    daily.day_id = "day_24_01_02"
    daily.status = SessionStatus.IN_PROGRESS

    service._load_session = MagicMock(return_value=session)
    service._sync_task_queue_from_attempts = MagicMock()
    service.db.get.return_value = daily
    service.curriculum_day_repo.get_by_day_id.return_value = None

    # V2 reset is delegated to SessionService.reset_session_full (tested
    # directly in test_session_lifecycle.py); mock it here.
    v2_service = MagicMock()
    v2_service.reset_session_full = AsyncMock(return_value=daily)
    monkeypatch.setattr(
        "app.modules.learning_session.service._make_v2_session_service",
        MagicMock(return_value=v2_service),
    )

    response = await service.restart_session(session_id="chat-w1d2", user_id=7)

    w1d2 = WEEKS_24[0].days[1]
    assert response.message == "Session restarted"
    assert response.topic == w1d2.title
    assert response.skill_name == "grammar"
    assert session.topic == w1d2.title
    assert session.teacher_instructions["__scripted_plan"] == _teacher_script(w1d2)
    assert service.session_repo.save.call_count == 2
    service.db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_read_cloze_submission_emits_validated_contract_payloads(
    monkeypatch,
) -> None:
    """M2 schema boundary: a contract-enabled archetype (READ_CLOZE) has its
    evaluation + feedback validated against the strict contracts before the WS
    events are emitted, so the wire payloads carry the full contract shape."""
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.session_repo = MagicMock()
    service._next_pending_attempt = MagicMock(return_value=None)
    service._sync_task_queue_from_attempts = MagicMock()

    async def _noop_complete(_session, _state):
        return
        yield  # pragma: no cover

    service._complete_and_announce = _noop_complete

    chat = MagicMock()
    chat.session_id = "chat-w1d1"
    chat.daily_session_id = 42
    chat.user_id = 7
    chat.skill_name = "grammar"
    chat.topic = "Simple Present"
    chat.task_type = "fill_in_blanks"
    chat.task_queue = [{"status": "pending"}]
    chat.messages = []

    daily = MagicMock()
    daily.session_id = "daily-w1d1"
    service.db.get.return_value = daily

    attempt = MagicMock()
    attempt.id = 101
    attempt.archetype_id = "READ_CLOZE"  # real value → contract path runs
    attempt.sequence = 1
    attempt.task_content = {
        "widget": "fill_in_blanks",
        "activity_contract": {
            "archetype_id": "READ_CLOZE",
            "task_widget": "fill_blanks",
            "evaluation_widget": "read_listen_evaluation",
            "feedback_widget": "read_listen_feedback",
        },
    }
    evaluation = MagicMock()
    evaluation.raw_score = 8.0
    evaluation.rubric_scores = {"accuracy": 8.0}
    evaluation.base_reward = 55
    evaluation.weighted_points = {"grammar": 55.0}
    evaluation.evaluator_notes = None
    feedback = MagicMock()
    feedback.score = 8
    feedback.summary = "Good work."
    feedback.did_well = ["Correct verb endings."]
    feedback.mistakes = [
        {
            "issue": "Missing -s",
            "user_wrote": "She drink",
            "correction": "She drinks",
            "rule": "3rd person -s",
            "sub_skills_affected": ["verb_forms"],
            "legacy_extra": "dropped",  # not in contract → must not leak through
        }
    ]
    feedback.next_tip = "Keep practising."
    feedback.sub_skill_breakdown = {"grammar": 8}

    v2_service = MagicMock()
    v2_service.submit_activity = AsyncMock(
        return_value=(attempt, evaluation, feedback)
    )
    monkeypatch.setattr(
        "app.modules.learning_session.service._make_v2_session_service",
        MagicMock(return_value=v2_service),
    )

    messages = [
        msg
        async for msg in service._handle_task_submission_stream(
            chat,
            {"current_sequence": 1, "current_task_index": 0},
            WSIncomingMessage(type="task_submission", answers={"q1": "works"}),
        )
    ]

    scorecard_event = next(
        m for m in messages if m.type == "ui_event" and m.widget == "scorecard"
    )
    feedback_event = next(
        m for m in messages if m.type == "ui_event" and m.widget == "feedback_card"
    )

    # Evaluation went through ActivityEvaluationOutput → tier + percentage derived.
    evaluation_payload = scorecard_event.payload["evaluation"]
    assert evaluation_payload["tier"] == "excellent"
    assert evaluation_payload["percentage"] == 80.0
    assert evaluation_payload["archetype_id"] == "READ_CLOZE"

    # Feedback went through ActivityFeedbackOutput → contract-shaped mistakes.
    feedback_payload = feedback_event.payload["feedback"]
    assert feedback_payload["archetype_id"] == "READ_CLOZE"
    assert feedback_payload["score"] == 8
    assert feedback_payload["next_tip"] == "Keep practising."
    mistake = feedback_payload["mistakes"][0]
    assert mistake["correction"] == "She drinks"
    assert "legacy_extra" not in mistake  # strict contract dropped the extra key


@pytest.mark.asyncio
async def test_task_submission_unexpected_error_yields_ws_error(monkeypatch) -> None:
    """A non-domain failure (DB/LLM/RAG) during submit must surface a recoverable
    WS error and keep the handler alive instead of killing the connection."""
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.session_repo = MagicMock()

    chat = MagicMock()
    chat.session_id = "chat-w1d1"
    chat.daily_session_id = 42
    chat.user_id = 7
    chat.task_queue = [{"status": "pending"}]
    chat.messages = []

    daily = MagicMock()
    daily.session_id = "daily-w1d1"
    service.db.get.return_value = daily

    v2_service = MagicMock()
    v2_service.submit_activity = AsyncMock(side_effect=RuntimeError("pinecone boom"))
    monkeypatch.setattr(
        "app.modules.learning_session.service._make_v2_session_service",
        MagicMock(return_value=v2_service),
    )

    messages = [
        msg
        async for msg in service._handle_task_submission_stream(
            chat,
            {"current_sequence": 1, "current_task_index": 0},
            WSIncomingMessage(type="task_submission", answers={"q1": "works"}),
        )
    ]

    # The generator completed (no propagation) and emitted a single error event.
    assert len(messages) == 1
    assert messages[0].type == "error"
    assert "try again" in (messages[0].content or "").lower()


@pytest.mark.asyncio
async def test_task_submission_events_expose_activity_contract(monkeypatch) -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.session_repo = MagicMock()
    service._next_pending_attempt = MagicMock(return_value=None)
    service._sync_task_queue_from_attempts = MagicMock()

    async def _noop_complete(_session, _state):
        return
        yield  # pragma: no cover

    service._complete_and_announce = _noop_complete

    chat = MagicMock()
    chat.session_id = "chat-w1d1"
    chat.daily_session_id = 42
    chat.user_id = 7
    chat.skill_name = "grammar"
    chat.topic = "Simple Present"
    chat.task_type = "fill_in_blanks"
    chat.task_queue = [{"status": "pending"}]
    chat.messages = []

    daily = MagicMock()
    daily.session_id = "daily-w1d1"
    service.db.get.return_value = daily

    contract = {
        "activity_id": "read_cloze_simple_present",
        "sequence": 1,
        "archetype_id": "READ_CLOZE",
        "task_widget": "fill_blanks",
        "evaluation_widget": "read_listen_evaluation",
        "feedback_widget": "read_listen_feedback",
    }
    attempt = MagicMock()
    # Projection now runs unconditionally for every archetype (the migration
    # gate is gone), so the attempt needs a real archetype_id, not a MagicMock.
    attempt.id = 1
    attempt.sequence = 1
    attempt.archetype_id = "READ_CLOZE"
    attempt.task_content = {
        "widget": "fill_in_blanks",
        "activity_contract": contract,
        "evaluation_widget": "read_listen_evaluation",
        "feedback_widget": "read_listen_feedback",
    }
    evaluation = MagicMock()
    evaluation.raw_score = 8.0
    evaluation.rubric_scores = {"accuracy": 8.0}
    evaluation.base_reward = 55
    evaluation.weighted_points = {"grammar": 55.0}
    evaluation.evaluator_notes = None
    feedback = MagicMock()
    feedback.score = 8
    feedback.summary = "Good work."
    feedback.did_well = ["Submitted carefully."]
    feedback.mistakes = []
    feedback.next_tip = "Keep practising."
    feedback.sub_skill_breakdown = {"grammar": 8}

    v2_service = MagicMock()
    v2_service.submit_activity = AsyncMock(
        return_value=(attempt, evaluation, feedback)
    )
    monkeypatch.setattr(
        "app.modules.learning_session.service._make_v2_session_service",
        MagicMock(return_value=v2_service),
    )

    state = {
        "current_sequence": 1,
        "current_task_index": 0,
    }
    messages = [
        msg
        async for msg in service._handle_task_submission_stream(
            chat,
            state,
            WSIncomingMessage(type="task_submission", answers={"q1": "works"}),
        )
    ]

    scorecard_event = next(
        msg for msg in messages if msg.type == "ui_event" and msg.widget == "scorecard"
    )
    feedback_event = next(
        msg
        for msg in messages
        if msg.type == "ui_event" and msg.widget == "feedback_card"
    )
    assert scorecard_event.payload["activity_contract"] == contract
    assert scorecard_event.payload["task_widget"] == "fill_in_blanks"
    assert scorecard_event.payload["evaluation_widget"] == "read_listen_evaluation"
    assert scorecard_event.payload["feedback_widget"] == "read_listen_feedback"
    assert scorecard_event.phase == "evaluation"
    assert scorecard_event.payload_kind == "evaluation"
    assert scorecard_event.sequence == 1
    assert scorecard_event.activity_id == "read_cloze_simple_present"
    assert scorecard_event.archetype_id == "READ_CLOZE"
    assert scorecard_event.event_id
    assert scorecard_event.payload["phase"] == "evaluation"
    assert scorecard_event.payload["payload_kind"] == "evaluation"
    assert scorecard_event.payload["evaluation"]["raw_score"] == 8.0
    assert feedback_event.payload["widget"] == "fill_in_blanks"
    assert feedback_event.payload["activity_contract"] == contract
    assert feedback_event.payload["feedback_widget"] == "read_listen_feedback"
    assert feedback_event.phase == "feedback"
    assert feedback_event.payload_kind == "feedback"
    assert feedback_event.payload["phase"] == "feedback"
    assert feedback_event.payload["feedback"]["summary"] == "Good work."


@pytest.mark.asyncio
async def test_task_delivery_events_are_phase_aware() -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    contract = {
        "activity_id": "read_cloze_simple_present",
        "sequence": 1,
        "archetype_id": "READ_CLOZE",
        "task_widget": "fill_blanks",
        "evaluation_widget": "read_listen_evaluation",
        "feedback_widget": "read_listen_feedback",
    }

    messages = [
        msg
        async for msg in service._stream_outgoing_events(
            [
                {
                    "type": "ui_event",
                    "widget": "fill_in_blanks",
                    "payload": {
                        "widget": "fill_in_blanks",
                        "activity_contract": contract,
                        "items": [{"id": "q1", "answer": "works"}],
                        "_session": {
                            "current_task_index": 0,
                            "total_tasks": 4,
                            "sequence": 1,
                            "daily_session_id": 42,
                        },
                    },
                }
            ],
            state={"task_type": "fill_in_blanks"},
        )
    ]

    task_event = messages[0]
    assert task_event.type == "ui_event"
    assert task_event.widget == "fill_in_blanks"
    assert task_event.phase == "task"
    assert task_event.payload_kind == "task"
    assert task_event.payload["phase"] == "task"
    assert task_event.payload["payload_kind"] == "task"
    assert task_event.payload["task"]["items"] == [{"id": "q1", "answer": "works"}]
    assert task_event.payload["activity_contract"] == contract


@pytest.mark.asyncio
async def test_complete_and_announce_emits_final_review_events(
    monkeypatch,
) -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.attempts_repo = MagicMock()
    service.session_repo = MagicMock()

    chat = MagicMock()
    chat.session_id = "chat-w1d1"
    chat.daily_session_id = 42
    chat.user_id = 7
    chat.task_queue = [{"status": "evaluated"}]
    chat.messages = []

    daily = MagicMock()
    daily.id = 42
    daily.session_id = "daily-w1d1"
    daily.day_id = "day_24_01_01"
    daily.status = SessionStatus.IN_PROGRESS
    service.db.get.return_value = daily
    service.attempts_repo.list_for_session.return_value = [
        MagicMock(status=AttemptStatus.EVALUATED)
    ]

    scorecard = SimpleNamespace(
        points_earned={"grammar": 55},
        subskill_totals_after={"grammar": 3055},
        dashboard_after={"grammar": 6.1},
        completed_at=datetime(2026, 5, 28, tzinfo=timezone.utc),
        points_applied=True,
        activities=[
            {
                "attempt_id": 1,
                "sequence": 1,
                "archetype_id": "READ_CLOZE",
                "raw_score": 8.0,
            }
        ],
        mentor_note="You are improving your subject-verb agreement.",
    )
    v2_service = MagicMock()
    v2_service.complete_session = AsyncMock(
        return_value=(scorecard, MagicMock())
    )
    monkeypatch.setattr(
        "app.modules.learning_session.service._make_v2_session_service",
        MagicMock(return_value=v2_service),
    )
    _mock_no_existing_scorecard(monkeypatch)

    class FakeSkillRepository:
        def __init__(self, db):  # noqa: ANN001
            self.db = db

        def display_label_map(self) -> dict[str, str]:
            return {"grammar": "Grammar"}

    monkeypatch.setattr(
        "app.modules.learning_session.service.SkillRepository",
        FakeSkillRepository,
    )

    messages = [
        msg
        async for msg in service._complete_and_announce(chat, {})
    ]

    final_scorecard = next(
        msg for msg in messages if msg.widget == "final_scorecard"
    )
    rag_feedback = next(msg for msg in messages if msg.widget == "rag_feedback")
    completed = next(msg for msg in messages if msg.widget == "session_completed")

    assert final_scorecard.phase == "final_scorecard"
    assert final_scorecard.payload_kind == "final_scorecard"
    assert final_scorecard.payload["points_earned"] == {"grammar": 55}
    assert final_scorecard.payload["skill_labels"] == {"grammar": "Grammar"}
    assert final_scorecard.payload["scorecard"]["mentor_note"] == (
        "You are improving your subject-verb agreement."
    )
    assert rag_feedback.phase == "rag_feedback"
    assert rag_feedback.payload["available"] is True
    assert rag_feedback.payload["mentor_note"] == (
        "You are improving your subject-verb agreement."
    )
    assert completed.phase == "completed"
    assert messages[-1].actions == ["Go to dashboard"]


def test_ready_gate_requires_previous_readiness_prompt() -> None:
    previous = "Nice. Ready to try the practice task?"

    assert _looks_like_ready_for_practice("ready", previous_tutor_message=previous)
    assert _looks_like_ready_for_practice("yes", previous_tutor_message=previous)
    assert not _looks_like_ready_for_practice(
        "I spend my mornings training machine learning models.",
        previous_tutor_message="Tell me one daily routine.",
    )
    assert not _looks_like_ready_for_practice(
        "I understand",
        previous_tutor_message="Tell me one daily routine.",
    )
    assert not _looks_like_ready_for_practice(
        "not ready",
        previous_tutor_message=previous,
    )


def test_looks_like_ready_for_practice_typo() -> None:
    """Common short-affirmative typos (yys, yse, okk, …) should pass the gate."""
    previous = "Great. Ready to try the practice task?"

    for typo in ("yys", "yse", "yeas", "yse!", "okk", "okey", "redy", "sury"):
        assert _looks_like_ready_for_practice(
            typo, previous_tutor_message=previous,
        ), f"expected typo {typo!r} to be treated as an affirmative"

    # Longer non-affirmative sentences must still be rejected even though they
    # contain a near-affirmative substring. The typo branch only fires when
    # the entire reply is a single short token.
    assert not _looks_like_ready_for_practice(
        "I think yys is what they meant, but please explain again.",
        previous_tutor_message=previous,
    )
    assert not _looks_like_ready_for_practice(
        "I would normally say yys here.",
        previous_tutor_message=previous,
    )


def test_readiness_prompt_soft_transitions() -> None:
    """Soft transition phrasings the teacher LLM emits must count as readiness prompts."""
    soft_transitions = (
        "Now, let's get started with the practice task. Good luck!",
        "Great! Let's begin the practice task. Please follow the instructions carefully.",
        "Time for the practice task!",
        "Ready for the practice exercise?",
        "Let's move on to the practice activity.",
        "Begin the practice task whenever you're set.",
        "Let's start with the practice task.",
    )
    for phrase in soft_transitions:
        assert _tutor_asked_readiness(phrase), (
            f"expected {phrase!r} to be recognised as a readiness prompt"
        )

    # Should not trigger on unrelated tutor messages.
    assert not _tutor_asked_readiness(
        "Now tell me one daily routine sentence."
    )
    assert not _tutor_asked_readiness(
        "Use 'usually' in a sentence about a habit."
    )


def test_turn_ceiling_force_transition_after_authored_plan() -> None:
    """After teacher exhausts the authored plan + mentions practice, plain
    "okay" must force a transition even when the strict gate misses it.
    """
    scripted = [
        "TURN 1 — Open the lesson",
        "TURN 2 — Subject-verb agreement",
        "TURN 3 — Frequency adverbs",
        "TURN 4 — Wrap-up: ask 'Ready to try the practice task?'",
    ]
    state = {
        "daily_plan": {
            "teacher_instructions": {"__scripted_plan": scripted},
        },
    }
    messages = [
        {"role": "ai", "content": "Hi! Today we learn the simple present.", "type": "chat"},
        {"role": "user", "content": "I analyze data every day.", "type": "chat"},
        {"role": "ai", "content": "Good. Now use 'he' or 'she'.", "type": "chat"},
        {"role": "user", "content": "He analyzes data every day.", "type": "chat"},
        {"role": "ai", "content": "Nice. Add a frequency adverb.", "type": "chat"},
        {"role": "user", "content": "She usually analyzes data.", "type": "chat"},
        {"role": "ai", "content": "Are you ready to try the practice task?", "type": "chat"},
        {"role": "user", "content": "yys", "type": "chat"},
        # Recovery message that the strict gate does not match.
        {
            "role": "ai",
            "content": "Got it — I think you meant yes. Let's begin the practice task. Good luck!",
            "type": "chat",
        },
    ]

    # Plain "okay" with no recognised readiness prompt should still
    # transition via the escape valve.
    assert _should_force_transition_to_practice(
        user_text="okay",
        messages=messages,
        state=state,
    )

    # Negation must still block the escape valve.
    assert not _should_force_transition_to_practice(
        user_text="not yet",
        messages=messages,
        state=state,
    )

    # Empty conversation: cannot force.
    assert not _should_force_transition_to_practice(
        user_text="ok",
        messages=[],
        state=state,
    )

    # No prior tutor mentioned 'practice task': cannot force.
    no_mention = [
        {"role": "ai", "content": "Step 1 explanation.", "type": "chat"},
        {"role": "ai", "content": "Step 2 explanation.", "type": "chat"},
        {"role": "ai", "content": "Step 3 explanation.", "type": "chat"},
        {"role": "ai", "content": "Step 4 explanation.", "type": "chat"},
    ]
    assert not _should_force_transition_to_practice(
        user_text="okay",
        messages=no_mention,
        state=state,
    )


# ── Phase 1: task_queue sync, resume checkpoint, restart scorecard ──────────


@pytest.mark.asyncio
async def test_sync_task_queue_from_attempts_reflects_attempt_statuses() -> None:
    """The cached chat task_queue is rebuilt to match V2 attempt statuses."""
    service = LearningSessionService.__new__(LearningSessionService)
    service.attempts_repo = MagicMock()

    a1 = _fake_attempt(archetype_id="READ_CLOZE", sequence=1)
    a1.status = AttemptStatus.EVALUATED
    a2 = _fake_attempt(archetype_id="WRITE_SENT_TRANS", sequence=2)
    a2.status = AttemptStatus.PENDING
    service.attempts_repo.list_for_session.return_value = [a1, a2]

    chat = MagicMock()
    chat.daily_session_id = 42
    # Stale cache: both still "pending" even though seq 1 is evaluated.
    chat.task_queue = [{"status": "pending"}, {"status": "pending"}]

    service._sync_task_queue_from_attempts(chat)

    service.attempts_repo.list_for_session.assert_called_once_with(42)
    assert [item["sequence"] for item in chat.task_queue] == [1, 2]
    assert [item["status"] for item in chat.task_queue] == ["evaluated", "pending"]


@pytest.mark.asyncio
async def test_resume_lands_on_pending_activity_without_replaying_feedback(
    monkeypatch,
) -> None:
    """After completing activity 1, resume jumps to the pending activity 2 and
    never re-emits the completed activity's evaluation/feedback widgets."""
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.session_repo = MagicMock()
    service.attempts_repo = MagicMock()

    chat = _w1d1_chat(phase="practice_task")
    chat.understanding_confirmed = True
    chat.current_task_index = 1

    daily = _w1d1_daily()
    service._load_session = MagicMock(return_value=chat)
    service._state_from_row = MagicMock(return_value={"task_queue": chat.task_queue})
    service._enrich_state_with_profile = MagicMock()
    service._sync_task_queue_from_attempts = MagicMock()
    service._auto_complete_daily_if_ready = AsyncMock(return_value=daily)
    service._session_blueprint_message = MagicMock(
        return_value=WSOutgoingMessage(type="ui_event", widget="session_blueprint")
    )

    pending = _fake_attempt(archetype_id="WRITE_SENT_TRANS", sequence=2)
    service._next_pending_attempt = MagicMock(return_value=pending)
    service._prepare_attempt_for_delivery = AsyncMock(return_value=pending)

    messages = [
        msg async for msg in service.resume_messages_stream("chat-w1d1")
    ]

    widgets = {m.widget for m in messages if m.widget}
    assert "scorecard" not in widgets
    assert "feedback_card" not in widgets
    assert "pronunciation_result" not in widgets
    # Resume lands on the pending activity's task widget.
    assert any(m.payload_kind == "task" for m in messages)


@pytest.mark.asyncio
async def test_restart_session_delegates_v2_reset_and_resyncs_queue(
    monkeypatch,
) -> None:
    """Restart delegates the V2 reset (scorecard drop + day reopen) to
    SessionService.reset_session_full and re-syncs the chat queue so a restarted
    day starts clean. The reset behaviour itself is unit-tested directly on
    SessionService in test_session_lifecycle.py."""
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.session_repo = MagicMock()
    service.curriculum_day_repo = MagicMock()
    service.archetype_repo = MagicMock()
    service._sync_task_queue_from_attempts = MagicMock()
    service._maybe_refresh_file_persona = MagicMock(return_value=False)

    session = MagicMock()
    session.session_id = "chat-restart"
    session.daily_session_id = 43
    session.user_id = 7
    session.topic = "T"
    session.skill_name = "grammar"
    session.task_type = "read"
    session.task_queue = []

    daily = MagicMock()
    daily.id = 43
    daily.session_id = "daily-restart"
    daily.day_id = "day_24_05_03"
    daily.status = SessionStatus.COMPLETED

    service._load_session = MagicMock(return_value=session)
    service.db.get.return_value = daily
    service.curriculum_day_repo.get_by_day_id.return_value = None

    v2_service = MagicMock()
    v2_service.reset_session_full = AsyncMock(return_value=daily)
    monkeypatch.setattr(
        "app.modules.learning_session.service._make_v2_session_service",
        MagicMock(return_value=v2_service),
    )

    await service.restart_session(session_id="chat-restart", user_id=7)

    # The V2 reset is delegated, not done with raw deletes in the chat layer.
    v2_service.reset_session_full.assert_awaited_once_with(
        session_id="daily-restart", user_id=7
    )
    # The chat queue is rebuilt from the (now reset) attempts.
    service._sync_task_queue_from_attempts.assert_called_once_with(session)
    service.db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_next_activity_is_noop_when_phase_is_practice_task() -> None:
    """Duplicate Next activity clicks must not re-deliver the pending task."""
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.attempts_repo = MagicMock()
    service.session_repo = MagicMock()

    session = MagicMock()
    session.phase = "practice_task"
    session.current_task_index = 2
    session.messages = []

    state = {"phase": "practice_task", "current_sequence": 3, "messages": []}

    messages = [
        msg
        async for msg in service._stream_followup_response(
            session, state, "Next activity",
        )
    ]

    assert messages == []
    service.attempts_repo.first_pending.assert_not_called()


@pytest.mark.asyncio
async def test_next_activity_delivers_once_then_noops(monkeypatch) -> None:
    service = LearningSessionService.__new__(LearningSessionService)
    service.db = MagicMock()
    service.attempts_repo = MagicMock()
    service.session_repo = MagicMock()
    service._task_type_for_attempt = MagicMock(return_value="fill_in_blanks")
    service._apply_update = MagicMock()
    service._stream_outgoing_events = MagicMock(return_value=_empty_async_iter())

    session = MagicMock()
    session.phase = "feedback"
    session.current_task_index = 1
    session.messages = []

    state = {"phase": "feedback", "current_sequence": 2, "messages": []}

    attempt = MagicMock()
    attempt.sequence = 3
    attempt.task_content = {"widget": "fill_in_blanks", "ui_widget": "FillInBlanks"}
    attempt.archetype_id = "WRITE_EMAIL"
    service.attempts_repo.first_pending.return_value = attempt
    service._prepare_attempt_for_delivery = AsyncMock(return_value=attempt)

    delivery_calls: list[int] = []

    async def _fake_task_delivery_node(_state):
        delivery_calls.append(1)
        return {"outgoing_events": []}

    monkeypatch.setattr(
        "app.modules.learning_session.service.task_delivery_node",
        _fake_task_delivery_node,
    )

    first = [
        msg
        async for msg in service._stream_followup_response(
            session, state, "Next activity",
        )
    ]
    assert first == []
    assert delivery_calls == [1]
    assert session.phase == "practice_task"

    second = [
        msg
        async for msg in service._stream_followup_response(
            session, state, "Next activity",
        )
    ]
    assert second == []
    assert delivery_calls == [1]


async def _empty_async_iter():
    return
    yield  # pragma: no cover — makes this an async generator
