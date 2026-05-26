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

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.data.courses.curriculum.source_24w import WEEKS_24
from app.modules.learning_session.service import (
    LearningSessionService,
    _parse_day_id,
    _looks_like_ready_for_practice,
    _should_force_transition_to_practice,
    _tutor_asked_readiness,
)
from app.modules.sessions.exceptions import DayNotFound
from app.modules.sessions.models import AttemptStatus, SessionStatus


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
    assert instr["__scripted_plan"] == list(w1d1.teacher_agent_behaviour)

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
    assert instr["__scripted_plan"] == list(w1d2.teacher_agent_behaviour)
    assert instr["lesson_description"] == w1d2.description
    assert "Simple Past Tense" in topic


def test_persona_from_file_blank_day_raises() -> None:
    persona = LearningSessionService._persona_from_file
    # W2D1 is intentionally blank in source_24w.py — file_source must refuse it.
    with pytest.raises(DayNotFound):
        persona(None, "day_24_02_01")  # type: ignore[arg-type]


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

    v2_service = MagicMock()
    v2_service.complete_session = AsyncMock()
    monkeypatch.setattr(
        "app.modules.learning_session.service._make_v2_session_service",
        MagicMock(return_value=v2_service),
    )

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
    service._stream_teaching_turn = MagicMock()

    v2_service = MagicMock()
    v2_service.complete_session = AsyncMock()
    monkeypatch.setattr(
        "app.modules.learning_session.service._make_v2_session_service",
        MagicMock(return_value=v2_service),
    )

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
    }
    return a


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
    assert instr["__scripted_plan"] == list(w1d1.teacher_agent_behaviour)
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
    assert kwargs["teacher_instructions"]["__scripted_plan"] == list(
        w1d1.teacher_agent_behaviour
    )
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
    assert kwargs["teacher_instructions"]["__scripted_plan"] == list(
        w1d2.teacher_agent_behaviour
    )
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
    assert session.teacher_instructions["__scripted_plan"] == list(
        w1d2.teacher_agent_behaviour
    )
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
    assert existing.teacher_instructions["__scripted_plan"] == list(
        w1d2.teacher_agent_behaviour
    )
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
    assert session.teacher_instructions["__scripted_plan"] == list(
        w1d2.teacher_agent_behaviour
    )
    service.session_repo.save.assert_called_once_with(session)
    service.db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_restart_session_refreshes_w1d2_chat_persona() -> None:
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
    daily.day_id = "day_24_01_02"
    daily.status = SessionStatus.IN_PROGRESS

    service._load_session = MagicMock(return_value=session)
    service.db.get.return_value = daily
    service.db.execute.return_value.scalars.return_value = []
    service.curriculum_day_repo.get_by_day_id.return_value = None

    response = await service.restart_session(session_id="chat-w1d2", user_id=7)

    w1d2 = WEEKS_24[0].days[1]
    assert response.message == "Session restarted"
    assert response.topic == w1d2.title
    assert response.skill_name == "grammar"
    assert session.topic == w1d2.title
    assert session.teacher_instructions["__scripted_plan"] == list(
        w1d2.teacher_agent_behaviour
    )
    assert service.session_repo.save.call_count == 2
    service.db.commit.assert_called_once()


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
