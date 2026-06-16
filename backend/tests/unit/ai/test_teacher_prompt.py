"""Teacher agent — user/system prompt assembly + teaching-turn generation.

Split out of the former monolithic test_teacher_agent_prompt.py."""

from __future__ import annotations

import pytest

from app.ai.agents import teacher
from app.ai.agents.teacher import (
    _build_user_prompt,
    _format_profile,
    _system_prompt,
    generate_teaching_turn,
    stream_teaching_turn,
    validate_teaching_message,
)

# Canonical fake (Phase 3 — moved out of this file into tests/mocks/).
from tests.mocks.llm import FakeTextLLM


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


def test_user_prompt_includes_current_step_and_turn_budget() -> None:
    prompt = _build_user_prompt(
        topic="Simple Present",
        sub_skill="grammar",
        task_type="read",
        user_level=1,
        learner_profile={},
        conversation=[{"role": "ai", "content": "Hi!", "type": "chat"}],
        scripted_plan=[
            "Greet and ask for a routine.",
            "Teach he/she -s.",
            "Ask only: Ready to try the practice task?",
        ],
        current_step_index=2,
    )
    assert "CURRENT STEP" in prompt
    assert "2. Teach he/she -s." in prompt
    assert "TURN BUDGET" in prompt
    assert "60--80 words" in prompt
    assert "reference only" in prompt


@pytest.mark.asyncio
async def test_readiness_turn_bypasses_llm(monkeypatch) -> None:
    fake = FakeTextLLM(text="LLM should not run.")
    monkeypatch.setattr(teacher, "get_default_llm_client", lambda: fake)

    plan = [
        "Greet and ask for one routine.",
        "Teach frequency adverbs.",
        "Ask only: Ready to try the practice task?",
    ]
    conversation = [
        {"role": "ai", "content": "Step 1.", "type": "chat"},
        {"role": "user", "content": "I walk every day."},
        {"role": "ai", "content": "Step 2.", "type": "chat"},
        {"role": "user", "content": "I usually walk."},
    ]

    result = await generate_teaching_turn(
        topic="Simple Present",
        sub_skill="grammar",
        task_type="read",
        user_level=1,
        learner_profile={},
        conversation=conversation,
        scripted_plan=plan,
        teacher_instructions={"readiness_prompt": "Ready to try the practice task?"},
        current_step_index=3,
    )

    assert result.messages == ["Ready to try the practice task?"]
    assert len(fake.calls) == 0


def test_teacher_prompt_includes_learner_profile() -> None:
    prompt = _build_user_prompt(
        topic="Simple Present Tense",
        sub_skill="grammar",
        task_type="read",
        user_level=1,
        learner_profile={
            "interests": "software engineering",
            "primary_goals": "speak in standups",
            "personalisation_context": "needs clear workplace examples",
            "self_assessed_level": "beginner",
            "structured_personalisation": {
                "domain": "technology",
                "communication_contexts": ["daily standup"],
                "pain_points": ["verb endings"],
                "tone_preference": "direct",
            },
        },
        conversation=[{"role": "user", "content": "I work every day."}],
        lesson_description="Teach routines.",
        scripted_plan=["Ask one routine question."],
    )

    assert "software engineering" in prompt
    assert "speak in standups" in prompt
    assert "daily standup" in prompt
    assert "I work every day." in prompt


def test_system_prompt_includes_formatting_rules() -> None:
    prompt = _system_prompt()
    assert "FORMATTING" in prompt
    assert "double asterisks" in prompt
    assert "No headings" in prompt or "No headings, bullet lists" in prompt


def test_validate_teaching_message_accepts_markdown_bold() -> None:
    msg = (
        "You used **smoke** in your question — we use **do** for I/you/we/they. "
        "Can you make one negative sentence?"
    )
    assert validate_teaching_message(msg) == []


def test_format_profile_includes_native_language() -> None:
    profile = _format_profile({"native_language": "Italian", "interests": "travel"})
    assert "Native language: Italian" in profile


def test_teacher_prompt_includes_native_language_from_profile() -> None:
    prompt = _build_user_prompt(
        topic="Simple Present",
        sub_skill="grammar",
        task_type="read",
        user_level=1,
        learner_profile={"native_language": "Italian"},
        conversation=[],
    )
    assert "Native language: Italian" in prompt


def test_system_prompt_advances_after_correct_frequency_adverb_sentence() -> None:
    prompt = _system_prompt()
    one_line_prompt = " ".join(prompt.split())

    assert "frequency-adverb steps" in prompt
    assert (
        "always, usually, often, sometimes, and never all count as successful"
        in one_line_prompt
    )
    assert "do not ask the learner to try another adverb" in prompt
    assert 'Ask only "Ready to try the practice task?"' in one_line_prompt


def test_system_prompt_keeps_positive_feedback_specific() -> None:
    prompt = _system_prompt()

    assert "quote the useful learner phrase" in prompt
    assert "do not add celebration filler" in prompt.lower()


@pytest.mark.asyncio
async def test_generate_teaching_turn_returns_llm_text(monkeypatch) -> None:
    fake = FakeTextLLM(text="Use simple present for routines.")
    monkeypatch.setattr(teacher, "get_default_llm_client", lambda: fake)

    result = await generate_teaching_turn(
        topic="Simple Present",
        sub_skill="grammar",
        task_type="read",
        user_level=1,
        learner_profile={},
        conversation=[],
        lesson_description="Teach routines.",
        scripted_plan=["Greet the learner."],
    )

    assert result.messages == ["Use simple present for routines."]
    assert fake.calls
    assert fake.calls[0]["temperature"] == 0.4


@pytest.mark.asyncio
async def test_stream_teaching_turn_streams_llm_chunks(monkeypatch) -> None:
    fake = FakeTextLLM(chunks=["Hello. ", "Tell me one routine."])
    monkeypatch.setattr(teacher, "get_default_llm_client", lambda: fake)

    chunks = [
        chunk
        async for chunk in stream_teaching_turn(
            topic="Simple Present",
            sub_skill="grammar",
            task_type="read",
            user_level=1,
            learner_profile={},
            conversation=[],
            lesson_description="Teach routines.",
            scripted_plan=["Greet the learner."],
        )
    ]

    # Streaming buffers and yields the validated turn in one shot to
    # guarantee the single-turn contract.
    assert chunks == ["Hello. Tell me one routine."]
    assert fake.calls


@pytest.mark.asyncio
async def test_teaching_turn_falls_back_when_llm_fails(monkeypatch) -> None:
    fake = FakeTextLLM(fail=True)
    monkeypatch.setattr(teacher, "get_default_llm_client", lambda: fake)

    result = await generate_teaching_turn(
        topic="Simple Present Tense",
        sub_skill="grammar",
        task_type="read",
        user_level=1,
        learner_profile={},
        conversation=[],
        lesson_description="Teach routines.",
    )

    assert "Today our lesson is about tense" in result.messages[0]
    assert "Tell me one real daily routine" in result.messages[0]


@pytest.mark.asyncio
async def test_scripted_teaching_turn_fallback_uses_current_lesson(
    monkeypatch,
) -> None:
    fake = FakeTextLLM(fail=True)
    monkeypatch.setattr(teacher, "get_default_llm_client", lambda: fake)

    result = await generate_teaching_turn(
        topic="Simple Past Tense — Regular and Irregular Verbs",
        sub_skill="grammar",
        task_type="read",
        user_level=1,
        learner_profile={},
        conversation=[],
        lesson_description="Teach completed actions.",
        scripted_plan=["Open: ask for one thing the learner did yesterday."],
    )

    message = result.messages[0]
    assert "Simple Past Tense" in message
    assert "simple present" not in message.lower()
    assert "routine" not in message.lower()
