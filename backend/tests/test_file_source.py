"""Smoke tests for `app.modules.curriculum.file_source`.

Confirms the in-process accessor over `source_24w.py` returns populated
Week 1 source days and refuses to serve blank days.
"""

from __future__ import annotations

import pytest

from app.modules.curriculum import file_source
from app.modules.sessions.exceptions import DayNotFound
from app.data.courses.curriculum.source_24w import DaySource, WeekSource


def test_get_day_returns_populated_w1_d1() -> None:
    day = file_source.get_day(1, 0)

    assert day.week_number == 1
    assert day.day_index == 0
    assert day.day_number == 1
    assert day.day_id == "day_24_01_01"
    assert day.cefr_level == "A1"
    assert day.theme_type == "grammar"
    assert day.topic.startswith("Simple Present Tense")
    assert "READ_CLOZE" in day.task_archetypes_used
    assert len(day.teacher_agent_behaviour) > 0


def test_get_day_by_id_returns_populated_w1_d1() -> None:
    day = file_source.get_day_by_id("day_24_01_01")

    assert day.week_number == 1
    assert day.day_number == 1
    assert day.topic.startswith("Simple Present Tense")


def test_get_day_by_id_returns_populated_w1_d2() -> None:
    day = file_source.get_day_by_id("day_24_01_02")

    assert day.week_number == 1
    assert day.day_number == 2
    assert day.day_id == "day_24_01_02"
    assert day.topic.startswith("Simple Past Tense")
    assert "completed actions" in day.explanation_brief
    assert list(day.task_archetypes_used) == [
        "READ_ERROR_SPOT",
        "LISTEN_CLOZE",
        "WRITE_ERROR_CORR",
        "SPEAK_READ_ALOUD",
    ]
    assert len(day.teacher_agent_behaviour) == 4
    assert len(day.task_specs) == len(day.task_archetypes_used)
    read_spec = file_source.task_spec_for(day, 0)
    assert "exactly 5" in read_spec["instructions_override"]
    assert "one grammatical error" in read_spec["instructions_override"]
    assert "error_spotting" in read_spec["widget_requirements"]
    assert "passive_helper_missing" in read_spec["widget_requirements"]

    speak_spec = file_source.task_spec_for(day, 3)
    assert "Read past simple passage aloud" in speak_spec["topic_override"]
    assert "connected simple past narrative passage" in speak_spec["instructions_override"]
    assert "50-60 words" in speak_spec["instructions_override"]
    assert "text_to_read_aloud" in speak_spec["widget_requirements"]
    assert "single connected past tense passage" in speak_spec["widget_requirements"]


def test_get_day_blank_entry_raises() -> None:
    # Week 2 is still blank in source_24w.py at time of writing.
    with pytest.raises(DayNotFound):
        file_source.get_day(2, 0)


def test_get_day_out_of_range_raises() -> None:
    with pytest.raises(DayNotFound):
        file_source.get_day(1, 99)
    with pytest.raises(DayNotFound):
        file_source.get_day(99, 0)


def test_resolve_archetypes_matches_registry() -> None:
    day = file_source.get_day(1, 0)
    specs = file_source.resolve_archetypes(day)

    assert len(specs) == len(day.task_archetypes_used)
    for name, spec in zip(day.task_archetypes_used, specs):
        assert spec.archetype_id == name


def test_w1d1_activity_order_includes_writing_third() -> None:
    day = file_source.get_day(1, 0)

    assert list(day.task_archetypes_used) == [
        "READ_CLOZE",
        "LISTEN_MCQ",
        "WRITE_OPEN_SENT",
        "SPEAK_TIMED",
    ]
    writing_spec = file_source.task_spec_for(day, 2)
    assert writing_spec["topic_override"] == (
        "Write simple present routine sentences"
    )
    assert "I/he/she" in writing_spec["instructions_override"]


def test_build_teacher_instructions_returns_minimal_lesson_context() -> None:
    day = file_source.get_day(1, 0)
    instr = file_source.build_teacher_instructions(day)

    assert instr == {"lesson_description": day.explanation_brief}
    assert "subject-verb" in instr["lesson_description"]


def test_task_spec_for_returns_authored_specs() -> None:
    day = file_source.get_day(1, 0)
    spec = file_source.task_spec_for(day, 0)

    assert spec["topic_override"].startswith("Simple present routines")
    assert "third-person -s" in spec["instructions_override"]
    assert file_source.task_spec_for(day, 99) == {}


def test_get_day_rejects_task_spec_count_mismatch(monkeypatch) -> None:
    week = WeekSource(
        week_number=99,
        theme_type="grammar",
        cefr_level="A1",
        sub_level_min=1,
        sub_level_max=1,
        days=(
            DaySource(
                title="Mismatch day",
                description="Mismatch brief",
                task_archetypes_used=("READ_CLOZE", "WRITE_OPEN_SENT"),
                task_specs=({"topic_override": "Only one spec"},),
            ),
        ),
    )
    monkeypatch.setattr(file_source, "WEEKS_24", (week,))
    with pytest.raises(DayNotFound, match="task_specs must have one entry"):
        file_source.get_day(99, 0)
