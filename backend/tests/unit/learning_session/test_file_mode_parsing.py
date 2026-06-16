"""Pure file-mode parsing/persona helpers on LearningSessionService.

Split out of the former monolithic test_learning_session_file_mode.py —
these exercise ``_parse_day_id`` and ``LearningSessionService._persona_from_file``
in isolation (no DB, no mocks).
"""

from __future__ import annotations

import pytest

from app.modules.curriculum.data.source_24w import WEEKS_24
from app.modules.curriculum.data.source_L_A1A2 import WEEKS_A1A2
from app.modules.learning_session.service import (
    LearningSessionService,
    _parse_day_id,
)
from app.modules.sessions.exceptions import DayNotFound


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


def test_persona_from_file_returns_day_48_01_02_depth_and_stashes_scripted_plan() -> None:
    """48w even-pass parity with W1D1: the depth day persona must carry the
    distinct depth title, the A2 sub-level, and the depth teacher script."""
    persona = LearningSessionService._persona_from_file
    topic, skill_name, sub_level, instr = persona(None, "day_48_01_02")  # type: ignore[arg-type]

    # `day_48_01_02` is the depth pass of source week 1, day 1 (A1A2 band).
    depth = WEEKS_A1A2[0].days[0].depth_day
    assert depth is not None
    assert topic == depth.title
    assert topic != WEEKS_A1A2[0].days[0].title  # distinct from the base day
    assert skill_name == "grammar"
    # Depth pass of a local week 1-4 day steps up to the upper CEFR (A1 → A2).
    assert sub_level == 3

    assert isinstance(instr, dict)
    assert instr["__scripted_plan"] == _teacher_script(depth)
    assert instr["lesson_description"] == depth.description
    assert "learning_goal" not in instr
    assert "sub_skill_context" not in instr


def test_persona_from_file_blank_day_raises() -> None:
    persona = LearningSessionService._persona_from_file
    # All 24 weeks are authored; invalid day_id is refused by file_source.
    with pytest.raises(DayNotFound):
        persona(None, "day_24_99_01")  # type: ignore[arg-type]
