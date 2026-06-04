"""Smoke tests for `app.modules.curriculum.file_source`.

Confirms the in-process accessor over `source_24w.py` returns populated
Week 1 source days and refuses to serve blank days.
"""

from __future__ import annotations

import pytest

from app.modules.curriculum import file_source
from app.modules.curriculum.data.source_24w import (
    ActivityBlueprint,
    DaySource,
    EvaluationBlueprint,
    FeedbackBlueprint,
    TaskBlueprint,
    TeacherBlueprint,
    TeacherStep,
    WeekSource,
)
from app.modules.sessions.exceptions import DayNotFound


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
    # All 24 weeks are file-authored; out-of-range week raises DayNotFound.
    with pytest.raises(DayNotFound):
        file_source.get_day(25, 0)


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
    assert "I, he, she" in writing_spec["instructions_override"]
    assert day.activity_contracts[2]["task_widget"] == "open_text"
    assert day.activity_contracts[2]["evaluation_widget"] == "write_speak_evaluation"
    assert day.activity_contracts[2]["feedback_widget"] == "write_speak_feedback"


def test_build_teacher_instructions_returns_minimal_lesson_context() -> None:
    day = file_source.get_day(1, 0)
    instr = file_source.build_teacher_instructions(day)

    assert instr["lesson_description"] == day.explanation_brief
    assert instr["lesson_goal"] == "Teach simple present for facts, routines, and habits."
    assert instr["readiness_prompt"] == "Ready to try the practice task?"
    assert "subject-verb" in instr["lesson_description"]


def test_task_spec_for_returns_authored_specs() -> None:
    day = file_source.get_day(1, 0)
    spec = file_source.task_spec_for(day, 0)

    assert spec["topic_override"].startswith("Simple present routines")
    assert "third-person -s" in spec["instructions_override"]
    assert file_source.task_spec_for(day, 99) == {}


def test_get_day_rejects_non_contiguous_activity_sequences(monkeypatch) -> None:
    week = WeekSource(
        week_number=99,
        theme_type="grammar",
        cefr_level="A1",
        sub_level_min=1,
        sub_level_max=1,
        days=(
            DaySource(
                title="Sequence mismatch day",
                description="Sequence mismatch brief",
                teacher=TeacherBlueprint(
                    steps=(
                        TeacherStep(
                            id="open",
                            goal="Introduce",
                            instruction="Introduce the lesson.",
                        ),
                    ),
                ),
                activities=(
                    ActivityBlueprint(
                        id="read",
                        sequence=1,
                        task=TaskBlueprint(
                            archetype_id="READ_CLOZE",
                            activity="read",
                            task_widget="fill_blanks",
                        ),
                        evaluation=EvaluationBlueprint(),
                        feedback=FeedbackBlueprint(),
                    ),
                    ActivityBlueprint(
                        id="write",
                        sequence=3,
                        task=TaskBlueprint(
                            archetype_id="WRITE_OPEN_SENT",
                            activity="write",
                            task_widget="open_text",
                        ),
                        evaluation=EvaluationBlueprint(),
                        feedback=FeedbackBlueprint(),
                    ),
                ),
            ),
        ),
    )
    monkeypatch.setattr(file_source, "WEEKS_24", (week,))

    def _resolve_stub(course_length, calendar_week, day_index):
        del course_length
        return type(
            "R",
            (),
            {
                "day": week.days[0],
                "cefr_level": "A1",
                "sub_level_min": 1,
                "sub_level_max": 1,
                "band": "A1A2",
                "source_week": 1,
                "calendar_week": calendar_week,
            },
        )()

    monkeypatch.setattr(file_source, "resolve_day", _resolve_stub)
    monkeypatch.setattr(
        file_source,
        "week_source_from_resolved",
        lambda resolved: week,
    )
    with pytest.raises(DayNotFound, match="contiguous"):
        file_source.get_day(99, 0)


def test_get_day_48w_w1_d2_is_depth_pass_with_a2() -> None:
    day = file_source.get_day_by_id("day_48_01_02")
    assert day.cefr_level == "A2"
    assert day.day_id == "day_48_01_02"
    assert day.topic == "Simple Present — Questions, Negatives & Short Answers"


def test_get_day_48w_w1_d1_is_base_pass_with_a1() -> None:
    day = file_source.get_day_by_id("day_48_01_01")
    assert day.cefr_level == "A1"
    assert day.topic.startswith("Simple Present Tense")
