"""Tests for evaluator consumption of Planner evaluation_focus.

Verifies that scoring_instruction + level_note are injected into the prompt
for AI-based evaluators, and that the lenient Planner guidance for sub-level 1
produces a higher score than the generic level-tier defaults for the same
answer with a basic grammar mistake.
"""

from __future__ import annotations

import asyncio

import pytest

from app.ai.agents import evaluator as evaluator_module
from app.ai.agents.evaluator import (
    EvaluationService,
    _build_open_text_user_message,
    _format_evaluation_focus_block,
    _OpenTextWritingEval,
    _ItemWritingEval,
)


VOCAB_FOCUS_SUB_LEVEL_1 = {
    "focus_areas": ["correct use of target vocabulary words", "basic sentence formation"],
    "level_note": (
        "Sub-level 1 beginner. Ignore advanced grammar mistakes entirely. "
        "Score only on whether the target vocabulary word is used correctly."
    ),
    "scoring_instruction": (
        "Award high scores (7-9/10) if the learner used the target word in a "
        "recognizable sentence, even with basic grammar errors. Award low "
        "scores (1-4/10) only if the target word is missing or used wrong."
    ),
}


def _task_content_vocabulary_write() -> dict:
    return {
        "items": [
            {
                "item_id": "item_1",
                "prompt": "Write one sentence about your family using the word 'mother'.",
                "sample_answer": "My mother cooks dinner every evening.",
            }
        ],
        "grammar_rule_explained": "Vocabulary use — family/home words",
        "common_mistakes": [],
    }


def test_format_evaluation_focus_block_includes_keys() -> None:
    rendered = _format_evaluation_focus_block(VOCAB_FOCUS_SUB_LEVEL_1)
    assert "PLANNER EVALUATION FOCUS" in rendered
    assert "focus_areas: correct use of target vocabulary words" in rendered
    assert "level_note: Sub-level 1 beginner" in rendered
    assert "scoring_instruction: Award high scores" in rendered


def test_format_evaluation_focus_block_empty_when_missing() -> None:
    assert _format_evaluation_focus_block(None) == ""
    assert _format_evaluation_focus_block({}) == ""


def test_open_text_prompt_includes_focus_when_supplied() -> None:
    prompt = _build_open_text_user_message(
        task_content=_task_content_vocabulary_write(),
        user_answers={"item_1": "My mother cook dinner."},
        user_level=1,
        learner_profile={},
        evaluation_focus=VOCAB_FOCUS_SUB_LEVEL_1,
    )
    assert "PLANNER EVALUATION FOCUS" in prompt
    assert "Award high scores" in prompt


def test_open_text_prompt_omits_focus_block_when_missing() -> None:
    prompt = _build_open_text_user_message(
        task_content=_task_content_vocabulary_write(),
        user_answers={"item_1": "My mother cook dinner."},
        user_level=1,
        learner_profile={},
    )
    assert "PLANNER EVALUATION FOCUS" not in prompt


def test_evaluate_open_text_writing_forwards_focus_to_llm(monkeypatch) -> None:
    """The evaluator must inject evaluation_focus into the user_prompt and
    a lenient scoring_instruction must let the LLM return a high score even
    when the answer has a basic grammar mistake — proves the wiring path.
    """
    captured = {"with_focus": None, "without_focus": None}

    async def stub_with_focus(self, **kwargs):
        captured["with_focus"] = kwargs["user_prompt"]
        return _OpenTextWritingEval(
            subskill_score=8,
            items=[_ItemWritingEval(
                item_id="item_1",
                correct=True,
                user_answer="My mother cook dinner.",
                mistakes=["Minor verb agreement: 'cook' → 'cooks' (ignored at sub-level 1)"],
                score=0.8,
            )],
            main_mistakes=[],
            overall_level="good",
        )

    async def stub_without_focus(self, **kwargs):
        captured["without_focus"] = kwargs["user_prompt"]
        return _OpenTextWritingEval(
            subskill_score=4,
            items=[_ItemWritingEval(
                item_id="item_1",
                correct=False,
                user_answer="My mother cook dinner.",
                mistakes=["Missing -s on third-person verb: 'cook' → 'cooks'"],
                score=0.4,
            )],
            main_mistakes=["Missing -s on third-person verb"],
            overall_level="needs_work",
        )

    # Path 1: with planner focus — lenient stub returns 8
    class StubClientLenient:
        async def generate_structured(self, **kwargs):
            return await stub_with_focus(self, **kwargs)

    import app.ai.llm as llm_module
    monkeypatch.setattr(
        llm_module, "get_default_llm_client", lambda: StubClientLenient(),
    )

    result_lenient = asyncio.run(EvaluationService().evaluate_open_text_writing(
        task_content=_task_content_vocabulary_write(),
        user_answers={"item_1": "My mother cook dinner."},
        user_level=1,
        learner_profile={},
        evaluation_focus=VOCAB_FOCUS_SUB_LEVEL_1,
    ))

    # Path 2: no planner focus — generic stub returns 4
    class StubClientStrict:
        async def generate_structured(self, **kwargs):
            return await stub_without_focus(self, **kwargs)

    monkeypatch.setattr(
        llm_module, "get_default_llm_client", lambda: StubClientStrict(),
    )

    result_strict = asyncio.run(EvaluationService().evaluate_open_text_writing(
        task_content=_task_content_vocabulary_write(),
        user_answers={"item_1": "My mother cook dinner."},
        user_level=1,
        learner_profile={},
    ))

    assert captured["with_focus"] is not None
    assert "PLANNER EVALUATION FOCUS" in captured["with_focus"]
    assert "Award high scores" in captured["with_focus"]

    assert captured["without_focus"] is not None
    assert "PLANNER EVALUATION FOCUS" not in captured["without_focus"]

    assert result_lenient["subskill_score"] == 8
    assert result_strict["subskill_score"] == 4
    assert result_lenient["subskill_score"] > result_strict["subskill_score"]


def test_evaluate_grammar_speaking_includes_focus_block(monkeypatch) -> None:
    """Prompt for grammar-speaking must include the planner focus block when supplied."""
    captured = {}

    class StubLLM:
        async def generate_structured(self, **kwargs):
            captured["prompt"] = kwargs["user_prompt"]
            from app.ai.agents.evaluator import _GrammarSpeakingEval, _GrammarSpeakingItemEval
            return _GrammarSpeakingEval(
                subskill_score=7,
                items=[_GrammarSpeakingItemEval(
                    item_id="prompt_1", mistakes=[], score=0.7, grammar_rule_used=True,
                )],
                main_mistakes=[],
                overall_level="good",
            )

    import app.ai.llm as llm_module
    monkeypatch.setattr(llm_module, "get_default_llm_client", lambda: StubLLM())

    task_content = {
        "speaking_prompts": ["Use 'mother' in a sentence."],
        "sample_responses": ["My mother cooks at home."],
        "grammar_rule_to_practice": "vocabulary in speech",
        "instructions": "Speak one sentence per prompt.",
    }
    answers = {
        "recordings": [
            {"item_id": "prompt_1", "transcript": "My mother cook at home.",
             "duration_seconds": 3}
        ]
    }

    asyncio.run(EvaluationService().evaluate_grammar_speaking(
        task_content=task_content,
        user_answers=answers,
        user_level=1,
        learner_profile={},
        evaluation_focus=VOCAB_FOCUS_SUB_LEVEL_1,
    ))

    assert "PLANNER EVALUATION FOCUS" in captured["prompt"]
    assert "Award high scores" in captured["prompt"]
