"""Tests for the Teacher Agent's consumption of Planner teacher_instructions.

Verifies:
  - When teacher_instructions are supplied, they appear in the prompt the
    Teacher Agent sends to the LLM (i.e. vocabulary context, not a hardcoded
    grammar fallback).
  - When omitted, the Teacher still runs end-to-end using its fallback path.
"""

from __future__ import annotations

import asyncio

import pytest

from app.ai.agents import teacher as teacher_module
from app.ai.agents.teacher import (
    TeachingOutput,
    _build_user_prompt,
    _format_planner_section,
    generate_teaching_turn,
)


VOCAB_INSTRUCTIONS = {
    "sub_skill_context": "Vocabulary session focusing on family and home words at a beginner level.",
    "learning_goal": "Teach 8-10 family/home words and one short sentence per word.",
    "words_to_cover": ["mother", "father", "house", "kitchen"],
    "teaching_approach": "Use very short sentences. One example per word. No derivatives.",
    "concept_check_focus": "Ask learner to use one of the words in a sentence about their home.",
    "do_not_reveal": "Do not reveal the MCQ options or the exact blanks.",
}


def test_format_planner_section_includes_words_and_keys() -> None:
    rendered = _format_planner_section(VOCAB_INSTRUCTIONS)
    assert "sub_skill_context: Vocabulary session" in rendered
    assert "learning_goal: Teach 8-10" in rendered
    assert "words_to_cover: mother, father, house, kitchen" in rendered
    assert "do_not_reveal" in rendered


def test_format_planner_section_returns_neutral_fallback_when_missing() -> None:
    """When no planner data is supplied, the teacher prompt must still get a
    short instruction (a 'none' note) so the LLM never sees a blank slot."""
    for empty_input in (None, {}):
        rendered = _format_planner_section(empty_input)
        assert rendered.startswith("Planner guidance: none")
        # Critical: the prompt block stays single-line and does NOT impersonate
        # a real planner block with structured key/value pairs.
        assert "Planner guidance for this lesson" not in rendered


def test_build_user_prompt_includes_planner_block_when_supplied() -> None:
    prompt = _build_user_prompt(
        topic="Everyday Words — Family & Home",
        sub_skill="vocabulary",
        task_type="mcq",
        user_level=1,
        learner_profile={},
        conversation=[],
        teacher_instructions=VOCAB_INSTRUCTIONS,
    )
    assert "Planner guidance for this lesson" in prompt
    assert "words_to_cover: mother, father, house, kitchen" in prompt


def test_build_user_prompt_signals_no_planner_when_omitted() -> None:
    prompt = _build_user_prompt(
        topic="Present Simple",
        sub_skill="grammar",
        task_type="fill_in_blanks",
        user_level=3,
        learner_profile={},
        conversation=[],
    )
    assert "Planner guidance: none" in prompt
    assert "Planner guidance for this lesson" not in prompt


def test_generate_teaching_turn_with_instructions_passes_them_through(monkeypatch) -> None:
    captured = {}

    class StubLLM:
        async def generate_structured(
            self, *, system_prompt, user_prompt, output_model, temperature=None,
        ):
            captured["user_prompt"] = user_prompt
            return TeachingOutput(messages=["Hello — today's words include mother and father."])

    monkeypatch.setattr(teacher_module, "get_default_llm_client", lambda: StubLLM())

    out = asyncio.run(generate_teaching_turn(
        topic="Everyday Words — Family & Home",
        sub_skill="vocabulary",
        task_type="mcq",
        user_level=1,
        learner_profile={},
        conversation=[],
        teacher_instructions=VOCAB_INSTRUCTIONS,
    ))

    assert "mother" in captured["user_prompt"]
    assert "Vocabulary session" in captured["user_prompt"]
    # The fallback grammar agenda must NOT be the only thing in the prompt;
    # the planner block should be present.
    assert "Planner guidance for this lesson" in captured["user_prompt"]
    assert out.messages[0].startswith("Hello")


def test_generate_teaching_turn_without_instructions_still_works(monkeypatch) -> None:
    class StubLLM:
        async def generate_structured(
            self, *, system_prompt, user_prompt, output_model, temperature=None,
        ):
            assert "Planner guidance: none" in user_prompt
            return TeachingOutput(messages=["Fallback teaching turn."])

    monkeypatch.setattr(teacher_module, "get_default_llm_client", lambda: StubLLM())

    out = asyncio.run(generate_teaching_turn(
        topic="Present Simple",
        sub_skill="grammar",
        task_type="fill_in_blanks",
        user_level=3,
        learner_profile={},
        conversation=[],
    ))
    assert out.messages == ["Fallback teaching turn."]


def test_generate_teaching_turn_uses_fallback_when_llm_raises(monkeypatch) -> None:
    class ExplodingLLM:
        async def generate_structured(self, **kwargs):
            raise RuntimeError("LLM down")

    monkeypatch.setattr(teacher_module, "get_default_llm_client", lambda: ExplodingLLM())

    out = asyncio.run(generate_teaching_turn(
        topic="Present Simple",
        sub_skill="grammar",
        task_type="fill_in_blanks",
        user_level=3,
        learner_profile={},
        conversation=[],
        teacher_instructions=VOCAB_INSTRUCTIONS,
    ))

    assert len(out.messages) >= 1
    assert all(isinstance(msg, str) and msg for msg in out.messages)
