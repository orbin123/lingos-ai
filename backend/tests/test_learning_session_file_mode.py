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

from unittest.mock import MagicMock

import pytest

from app.core.config import settings
from app.data.courses.curriculum_v2.source_24w import WEEKS_24
from app.modules.learning_session.service import (
    LearningSessionService,
    _parse_day_id,
    _looks_like_ready_for_practice,
)
from app.modules.sessions.exceptions import DayNotFound
from app.modules.sessions.models import AttemptStatus


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


def test_persona_from_file_blank_day_raises() -> None:
    persona = LearningSessionService._persona_from_file
    # W2D1 is intentionally blank in source_24w.py — file_source must refuse it.
    with pytest.raises(DayNotFound):
        persona(None, "day_24_02_01")  # type: ignore[arg-type]


# ── Full create_session flow (no DB) ───────────────────────────────


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
    """End-to-end coverage of `create_session` in file mode.

    Uses mocks instead of a real DB so we can verify two things without
    spinning up Postgres:
      1. `PlannerAgent.generate` is never awaited.
      2. The `session_repo.create` call receives a teacher_instructions
         dict that carries `__scripted_plan` matching W1D1's authored
         `teacher_agent_behaviour`.
    """
    monkeypatch.setattr(settings, "CURRICULUM_SOURCE", "file")

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
    monkeypatch.setattr(settings, "CURRICULUM_SOURCE", "db")

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
