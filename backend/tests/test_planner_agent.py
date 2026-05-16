"""Tests for the Planner Agent — deterministic assembly, end-to-end, fallback."""

from __future__ import annotations

import asyncio

import pytest

from app.ai.agents import planner as planner_module
from app.ai.agents.planner import (
    EvaluationFocus,
    PlannerLLMOutput,
    TeacherInstructions,
    _build_deterministic_activities,
    generate_daily_plan,
)
from app.modules.curriculum.topics import CourseTopic, get_course_topic


def _stub_focuses() -> list[EvaluationFocus]:
    return [
        EvaluationFocus(
            focus_areas=[f"focus {i}"],
            level_note=f"level note {i}",
            scoring_instruction=f"score how {i}",
        )
        for i in range(4)
    ]


def _stub_llm_output() -> PlannerLLMOutput:
    return PlannerLLMOutput(
        teacher_instructions=TeacherInstructions(
            sub_skill_context="Vocabulary intro for beginners.",
            learning_goal="Teach 8-10 everyday words for talking about people.",
            words_to_cover=["mother", "father", "house"],
            teaching_approach="Use one simple example per word; sentences under 10 words.",
            concept_check_focus="Ask learner to use one word in a sentence about home.",
            do_not_reveal="Do not reveal MCQ blanks or exact options.",
            lesson_context="introducing the people closest to you to a new neighbour",
            vocabulary_domain="everyday English: family and home",
            conversation_style="warm and encouraging",
        ),
        evaluation_focuses=_stub_focuses(),
    )


def test_build_deterministic_activities_for_vocabulary() -> None:
    focuses = _stub_focuses()
    activities = _build_deterministic_activities(
        sub_skill="vocabulary",
        evaluation_focuses=focuses,
    )

    assert [a["activity"] for a in activities] == ["read", "write", "listen", "speak"]
    assert [a["order"] for a in activities] == [1, 2, 3, 4]

    read, write, listen, speak = activities

    assert read["template_id"] == "full_vocabulary_read_v1"
    assert read["widget"] == "mcq"
    assert read["evaluation_method"] == "rule_exact_match"

    assert write["template_id"] == "full_vocabulary_write_v1"
    assert write["widget"] == "open_text"
    assert write["evaluation_method"] == "llm_open_writing"

    assert listen["template_id"] == "full_vocabulary_listen_v1"
    assert listen["widget"] == "listen_and_respond"

    assert speak["template_id"] == "full_vocabulary_speak_v1"
    assert speak["widget"] == "speak_and_record"

    for activity, focus in zip(activities, focuses, strict=True):
        assert activity["evaluation_focus"] == focus.model_dump()


def test_build_deterministic_activities_rejects_wrong_focus_count() -> None:
    with pytest.raises(ValueError):
        _build_deterministic_activities(
            sub_skill="vocabulary",
            evaluation_focuses=_stub_focuses()[:2],
        )


def test_generate_daily_plan_end_to_end_with_mocked_llm(monkeypatch) -> None:
    class StubLLM:
        async def generate_structured(
            self, *, system_prompt, user_prompt, output_model, temperature=None,
        ):
            assert output_model is PlannerLLMOutput
            return _stub_llm_output()

    monkeypatch.setattr(
        planner_module, "get_default_llm_client", lambda: StubLLM(),
    )

    topic_entry = get_course_topic(duration_weeks=24, week=1, day=2)
    # If the course data has W1D2 as vocabulary, we expect that flow.
    # Otherwise fall back to a hand-built CourseTopic so this test stays robust.
    if topic_entry is None or topic_entry.sub_skill != "vocabulary":
        topic_entry = CourseTopic(
            week=1, day=2, topic_id="1:2", sub_skill="vocabulary",
            sub_level=1,
            communication_goal="talk about the people around you",
            language_focus="everyday vocabulary: people and places",
        )

    plan = asyncio.run(generate_daily_plan(
        user_id=42,
        course_slug="beginner-24w",
        topic_entry=topic_entry,
        learner_profile={"interests": "cooking", "primary_goals": "travel"},
    ))

    expected_top_keys = {
        "user_id", "course_slug", "week", "day", "topic_id", "topic_name",
        "communication_goal", "language_focus",
        "sub_skill", "sub_level", "generated_at", "teacher_instructions",
        "activities",
    }
    assert expected_top_keys.issubset(plan.keys())
    assert plan["user_id"] == 42
    assert plan["course_slug"] == "beginner-24w"
    assert plan["sub_skill"] == "vocabulary"
    assert len(plan["activities"]) == 4
    assert plan["teacher_instructions"]["words_to_cover"] == ["mother", "father", "house"]
    assert plan["teacher_instructions"]["lesson_context"]
    assert plan["teacher_instructions"]["vocabulary_domain"]
    assert plan["teacher_instructions"]["conversation_style"]
    assert plan["activities"][0]["template_id"] == "full_vocabulary_read_v1"


def test_generate_daily_plan_falls_back_when_llm_raises(monkeypatch) -> None:
    class ExplodingLLM:
        async def generate_structured(self, **kwargs):
            raise RuntimeError("LLM down")

    monkeypatch.setattr(
        planner_module, "get_default_llm_client", lambda: ExplodingLLM(),
    )

    topic_entry = CourseTopic(
        week=1, day=2, topic_id="1:2", sub_skill="vocabulary",
        sub_level=1,
        communication_goal="talk about the people around you",
        language_focus="everyday vocabulary: people and places",
    )

    plan = asyncio.run(generate_daily_plan(
        user_id=99,
        course_slug="beginner-24w",
        topic_entry=topic_entry,
        learner_profile={},
    ))

    assert len(plan["activities"]) == 4
    assert plan["teacher_instructions"]["sub_skill_context"]
    assert plan["teacher_instructions"]["do_not_reveal"]
    # Fallback must still populate the new personalization fields so
    # downstream agents never see a partial teacher_instructions object.
    assert plan["teacher_instructions"]["lesson_context"]
    assert plan["teacher_instructions"]["vocabulary_domain"]
    assert plan["teacher_instructions"]["conversation_style"]
    for activity in plan["activities"]:
        assert activity["evaluation_focus"]["focus_areas"]
