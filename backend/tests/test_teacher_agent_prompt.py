from __future__ import annotations

from app.ai.agents.teacher import _build_user_prompt


def test_scripted_teacher_prompt_uses_title_description_and_behavior_only() -> None:
    prompt = _build_user_prompt(
        topic="Simple Present Tense",
        sub_skill="grammar",
        task_type="read",
        user_level=1,
        learner_profile={},
        conversation=[],
        teacher_instructions={
            "lesson_description": "Teach routines and subject-verb agreement.",
            "learning_goal": "Old planner goal should not steer authored days.",
            "sub_skill_context": "Old planner context should not appear.",
        },
        scripted_plan=[
            "Teach tense.",
            "Ask for one daily routine.",
        ],
    )

    assert "Lesson title: Simple Present Tense" in prompt
    assert "Lesson description: Teach routines and subject-verb agreement." in prompt
    assert "AUTHORED TEACHER BEHAVIOR" in prompt
    assert "Teach tense." in prompt
    assert "Ask for one daily routine." in prompt
    assert "Old planner goal" not in prompt
    assert "Old planner context" not in prompt
