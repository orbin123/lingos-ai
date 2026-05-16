"""Persona-differentiation test for the Planner Agent.

Two learners with identical curriculum entries but different
structured_personalisation must produce planner prompts that reference
their respective domains. The evaluator contract (4 evaluation_focuses)
must remain intact regardless of personalisation.
"""

from __future__ import annotations

import asyncio

from app.ai.agents import planner as planner_module
from app.ai.agents.planner import (
    EvaluationFocus,
    PlannerLLMOutput,
    TeacherInstructions,
    _build_planner_prompt,
    generate_daily_plan,
)
from app.modules.curriculum.topics import CourseTopic


def _focuses() -> list[EvaluationFocus]:
    return [
        EvaluationFocus(
            focus_areas=["grammar"],
            level_note="Beginner-friendly.",
            scoring_instruction="Award credit for clear attempts.",
        )
        for _ in range(4)
    ]


def _llm_output() -> PlannerLLMOutput:
    return PlannerLLMOutput(
        teacher_instructions=TeacherInstructions(
            sub_skill_context="Beginner grammar context.",
            learning_goal="Introduce yourself in one sentence.",
            words_to_cover=["I", "am", "work", "study"],
            teaching_approach="Demonstrate one pattern at a time.",
            concept_check_focus="Ask for a one-sentence self-introduction.",
            do_not_reveal="Do not reveal the practice items.",
            lesson_context="placeholder context — stubbed by test",
            vocabulary_domain="placeholder domain — stubbed by test",
            conversation_style="placeholder style — stubbed by test",
        ),
        evaluation_focuses=_focuses(),
    )


_TOPIC = CourseTopic(
    week=1, day=1, topic_id="1:1",
    sub_skill="grammar", sub_level=1,
    communication_goal="introduce yourself in everyday situations",
    language_focus="present simple — affirmative",
)


_ENGINEER_PROFILE = {
    "interests": "software, agile",
    "primary_goals": "workplace fluency",
    "structured_personalisation": {
        "domain": "tech / software engineering",
        "communication_contexts": ["standup meeting", "PR review"],
        "priority_skills": ["explaining technical decisions"],
        "pain_points": ["filler words"],
        "tone_preference": "professional",
        "extraction_source": "llm",
        "extracted_at": "2026-05-15T00:00:00+00:00",
    },
}

_STUDENT_PROFILE = {
    "interests": "study abroad",
    "primary_goals": "study abroad",
    "structured_personalisation": {
        "domain": "university student",
        "communication_contexts": ["first day on campus", "study group"],
        "priority_skills": ["academic writing", "asking questions in class"],
        "pain_points": ["confidence in group discussion"],
        "tone_preference": "neutral",
        "extraction_source": "llm",
        "extracted_at": "2026-05-15T00:00:00+00:00",
    },
}


def test_planner_prompt_embeds_each_users_domain() -> None:
    """The prompt body must reference each user's domain + contexts."""
    engineer_prompt = _build_planner_prompt(
        topic_entry=_TOPIC, learner_profile=_ENGINEER_PROFILE
    )
    student_prompt = _build_planner_prompt(
        topic_entry=_TOPIC, learner_profile=_STUDENT_PROFILE
    )

    assert "tech / software engineering" in engineer_prompt
    assert "standup meeting" in engineer_prompt
    assert "university student" in student_prompt
    assert "first day on campus" in student_prompt

    # Both prompts must always carry the curriculum's non-negotiable
    # language focus regardless of personalisation.
    assert "present simple — affirmative" in engineer_prompt
    assert "present simple — affirmative" in student_prompt


def test_planner_prompt_handles_empty_personalisation_gracefully() -> None:
    """`extraction_source: empty` should trigger the neutral-fallback note."""
    profile = {
        "structured_personalisation": {
            "domain": "general",
            "communication_contexts": [],
            "priority_skills": [],
            "pain_points": [],
            "tone_preference": "neutral",
            "extraction_source": "empty",
            "extracted_at": "2026-05-15T00:00:00+00:00",
        }
    }
    prompt = _build_planner_prompt(topic_entry=_TOPIC, learner_profile=profile)
    assert "EMPTY" in prompt
    assert "neutral" in prompt


def test_planner_e2e_preserves_evaluator_contract(monkeypatch) -> None:
    """End-to-end: the evaluator-facing contract (4 focuses) is preserved."""

    class StubLLM:
        async def generate_structured(self, **kwargs):
            return _llm_output()

    monkeypatch.setattr(
        planner_module, "get_default_llm_client", lambda: StubLLM(),
    )

    plan = asyncio.run(
        generate_daily_plan(
            user_id=1,
            course_slug="beginner-24w",
            topic_entry=_TOPIC,
            learner_profile=_ENGINEER_PROFILE,
        )
    )

    assert len(plan["activities"]) == 4
    for activity in plan["activities"]:
        focus = activity["evaluation_focus"]
        assert focus["focus_areas"]
        assert focus["level_note"]
        assert focus["scoring_instruction"]
    # New personalization fields surface on the plan dict.
    assert plan["communication_goal"] == _TOPIC.communication_goal
    assert plan["language_focus"] == _TOPIC.language_focus
    # And on teacher_instructions so the teacher agent can read them.
    instr = plan["teacher_instructions"]
    assert instr["lesson_context"]
    assert instr["vocabulary_domain"]
    assert instr["conversation_style"]
