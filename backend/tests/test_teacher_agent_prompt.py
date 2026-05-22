from __future__ import annotations

from collections.abc import AsyncIterator

import pytest

from app.ai.agents import teacher
from app.ai.agents.teacher import (
    TeachingOutput,
    _build_user_prompt,
    generate_teaching_turn,
    stream_teaching_turn,
    validate_teaching_message,
)


class FakeTextLLM:
    def __init__(
        self,
        *,
        text: str | list[str] = "LLM teacher message.",
        chunks: list[str] | None = None,
        fail: bool = False,
    ) -> None:
        # `text` may be a single string (returned every call) or a list
        # (consumed in order, allowing distinct first/retry responses).
        if isinstance(text, str):
            self._texts: list[str] = [text]
        else:
            self._texts = list(text)
        self.chunks = chunks or ["LLM ", "stream."]
        self.fail = fail
        self.calls: list[dict] = []

    @property
    def text(self) -> str:
        return self._texts[-1] if self._texts else ""

    async def generate_text(self, **kwargs) -> str:
        self.calls.append(kwargs)
        if self.fail:
            raise RuntimeError("provider down")
        if len(self._texts) > 1:
            return self._texts.pop(0)
        return self._texts[0]

    async def stream_text(self, **kwargs) -> AsyncIterator[str]:
        self.calls.append(kwargs)
        if self.fail:
            raise RuntimeError("provider down")
        for chunk in self.chunks:
            yield chunk


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
        scripted_plan=["Greet the learner."],
    )

    assert "Today our lesson is about tense" in result.messages[0]
    assert "Tell me one real daily routine" in result.messages[0]


# --- Guardrail tests: single-turn contract -----------------------------------


def test_validate_clean_message_returns_no_violations() -> None:
    assert validate_teaching_message("Nice work. Can you change it to he?") == []


def test_validate_flags_multiple_questions() -> None:
    msg = "Good. Can you say it with he? And what about she?"
    violations = validate_teaching_message(msg)
    assert "multiple_questions" in violations


def test_validate_flags_too_long() -> None:
    msg = " ".join(["word"] * 100) + "?"
    violations = validate_teaching_message(msg)
    assert "too_long" in violations


def test_validate_flags_empty() -> None:
    assert validate_teaching_message("   ") == ["empty"]


def test_validate_flags_readiness_combined_with_teaching() -> None:
    msg = (
        "With he or she we add an s to the verb. Now you understand the rule. "
        "Always use this for routines. Ready to try the practice task?"
    )
    violations = validate_teaching_message(msg)
    assert "readiness_combined_with_teaching" in violations


def test_validate_flags_duplicate_of_previous() -> None:
    prev = "Hello! Today we will learn about the simple present tense."
    # Same words, slight reorder — Jaccard well above threshold.
    msg = "Hello! Today we learn about the simple present tense will."
    violations = validate_teaching_message(msg, previous_assistant_message=prev)
    assert "duplicate_of_previous" in violations


def test_validate_not_duplicate_when_content_differs() -> None:
    prev = "Hello! Today we will learn about the simple present tense."
    msg = "You used 'analyze'. Can you say it with he?"
    violations = validate_teaching_message(msg, previous_assistant_message=prev)
    assert "duplicate_of_previous" not in violations


def test_teaching_output_rejects_multiple_messages() -> None:
    with pytest.raises(ValueError, match="exactly one message"):
        TeachingOutput(messages=["one?", "two?"])


def test_teaching_output_rejects_multiple_questions() -> None:
    with pytest.raises(ValueError, match="multiple_questions"):
        TeachingOutput(messages=["A? B?"])


@pytest.mark.asyncio
async def test_repair_truncates_extra_questions(monkeypatch) -> None:
    # LLM dumps teaching + two questions in one turn — the exact bug the user
    # reported. Repair must keep only up to and including the first question.
    bad = (
        "Great sentence! For 'I' use the base verb 'analyze'. For 'he' add an "
        "s to make 'analyzes'. Now can you say it with he? Also what about she?"
    )
    fake = FakeTextLLM(text=bad)
    monkeypatch.setattr(teacher, "get_default_llm_client", lambda: fake)

    result = await generate_teaching_turn(
        topic="Simple Present",
        sub_skill="grammar",
        task_type="read",
        user_level=1,
        learner_profile={},
        conversation=[{"role": "user", "content": "I analyze data every day."}],
        lesson_description="Teach routines.",
        scripted_plan=["Teach he/she -s rule."],
    )

    msg = result.messages[0]
    assert msg.count("?") == 1
    assert msg.endswith("?")
    assert "Also what about she" not in msg


@pytest.mark.asyncio
async def test_repair_retries_on_duplicate_then_returns_clean(monkeypatch) -> None:
    prev = "Hello! Today we will learn about the simple present tense."
    # First call: near-duplicate of prior turn. Retry call: clean.
    fake = FakeTextLLM(
        text=[
            "Hello! Today we learn about the simple present tense will.",
            "You used 'analyze'. Can you say it with he?",
        ]
    )
    monkeypatch.setattr(teacher, "get_default_llm_client", lambda: fake)

    result = await generate_teaching_turn(
        topic="Simple Present",
        sub_skill="grammar",
        task_type="read",
        user_level=1,
        learner_profile={},
        conversation=[
            {"role": "ai", "content": prev, "type": "chat"},
            {"role": "user", "content": "I analyze data every day."},
        ],
        lesson_description="Teach routines.",
        scripted_plan=["Teach he/she -s rule."],
    )

    assert result.messages == ["You used 'analyze'. Can you say it with he?"]
    # Two calls: the initial + the corrective retry.
    assert len(fake.calls) == 2
    # The retry prompt must include the anti-duplication nudge.
    retry_prompt = fake.calls[1]["user_prompt"]
    assert "Do NOT repeat" in retry_prompt


@pytest.mark.asyncio
async def test_repair_falls_back_when_retry_also_fails(monkeypatch) -> None:
    # Both attempts return multi-question turns; deterministic truncation
    # still leaves a single-question, clean turn.
    bad = "Info one? Info two? Info three?"
    fake = FakeTextLLM(text=bad)
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

    msg = result.messages[0]
    assert msg.count("?") == 1


@pytest.mark.asyncio
async def test_streaming_repairs_multi_question_turn(monkeypatch) -> None:
    # Streaming chunks bundle two questions; final yield must be one question.
    fake = FakeTextLLM(
        chunks=[
            "Great! ",
            "Can you say it with he? ",
            "And what about she?",
        ]
    )
    monkeypatch.setattr(teacher, "get_default_llm_client", lambda: fake)

    chunks = [
        chunk
        async for chunk in stream_teaching_turn(
            topic="Simple Present",
            sub_skill="grammar",
            task_type="read",
            user_level=1,
            learner_profile={},
            conversation=[{"role": "user", "content": "I analyze data."}],
            lesson_description="Teach routines.",
            scripted_plan=["Teach he/she -s rule."],
        )
    ]

    assert len(chunks) == 1
    assert chunks[0].count("?") == 1
    assert chunks[0].endswith("?")
