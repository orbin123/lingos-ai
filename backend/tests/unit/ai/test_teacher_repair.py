"""Teacher agent — LLM repair/retry + streaming single-turn behavior.

Split out of the former monolithic test_teacher_agent_prompt.py."""

from __future__ import annotations

import pytest

from app.ai.agents import teacher
from app.ai.agents.teacher import (
    generate_teaching_turn,
    stream_teaching_turn,
)

# Canonical fake (Phase 3 — moved out of this file into tests/mocks/).
from tests.mocks.llm import FakeTextLLM


@pytest.mark.asyncio
async def test_repair_collapses_extra_questions(monkeypatch) -> None:
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
    assert "say it with he" in msg
    assert "Also what about she" not in msg


@pytest.mark.asyncio
async def test_repair_depth_day_opener_pattern(monkeypatch) -> None:
    """Regression for day_48_01_02-style multi-question openers."""

    bad = (
        "Hello! Yesterday, you practiced simple present routines. Today, we "
        "will add questions like Do you...? Can you ask one yes/no question "
        "about a daily routine?"
    )
    fake = FakeTextLLM(text=bad)
    monkeypatch.setattr(teacher, "get_default_llm_client", lambda: fake)

    result = await generate_teaching_turn(
        topic="Simple Present — Questions, Negatives & Short Answers",
        sub_skill="grammar",
        task_type="read",
        user_level=1,
        learner_profile={},
        conversation=[],
        lesson_description=(
            "Learners build on yesterday's routines: yes/no and wh-questions."
        ),
        scripted_plan=[
            "Greet the learner and note they practised simple present routines "
            "yesterday. Ask for one yes/no question about a daily routine.",
        ],
    )

    msg = result.messages[0]
    assert msg.count("?") == 1
    assert "yes/no question" in msg
    assert msg.endswith("about a daily routine?")


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
    assert msg == "Info three?"


@pytest.mark.asyncio
async def test_streaming_repairs_multi_question_turn(monkeypatch) -> None:
    # Streaming chunks bundle two questions; final yield must be one question.
    fake = FakeTextLLM(
        text="You used 'analyze'. Can you say it with he?",
        chunks=[
            "Great! ",
            "Can you say it with he? ",
            "And what about she?",
        ],
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
