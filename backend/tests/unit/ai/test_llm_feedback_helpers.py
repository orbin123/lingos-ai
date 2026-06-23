"""Feedback helpers: MCQ/cloze wrong-item computation + confirmed-mistake injection.

Split out of the former monolithic test_llm_session_agents.py.
"""

from __future__ import annotations


import pytest

from app.ai.sessions.llm_feedback import (
    FeedbackOutput,
    LLMFeedbackGenerator,
    MistakeOutSchema,
)
from app.scoring import get_archetype

# Canonical fakes (Phase 3 — moved out of this file into tests/mocks/).
from tests.mocks.llm import FakeLLMClient


class TestComputeWrongItems:
    """Unit tests for the deterministic blank-checking helper."""

    def _task(self):
        return {
            "items": [
                {
                    "item_id": "b1",
                    "correct_answer": "brush",
                    "explanation": "base verb for I",
                },
                {
                    "item_id": "b2",
                    "correct_answer": "eats",
                    "explanation": "she adds -s",
                },
                {
                    "item_id": "b3",
                    "correct_answer": "walks",
                    "explanation": "he adds -s",
                },
                {
                    "item_id": "b4",
                    "correct_answer": "drink",
                    "explanation": "they takes base verb",
                },
            ]
        }

    def test_only_wrong_answer_is_flagged(self):
        from app.ai.sessions.prompts import compute_wrong_items

        user_response = {"b1": "brush", "b2": "eat", "b3": "walks", "b4": "drink"}
        wrong = compute_wrong_items(self._task(), user_response)

        assert len(wrong) == 1
        assert wrong[0]["item_id"] == "b2"
        assert wrong[0]["user_wrote"] == "eat"
        assert wrong[0]["correct_answer"] == "eats"

    def test_all_correct_returns_empty(self):
        from app.ai.sessions.prompts import compute_wrong_items

        user_response = {"b1": "brush", "b2": "eats", "b3": "walks", "b4": "drink"}
        assert compute_wrong_items(self._task(), user_response) == []

    def test_case_and_whitespace_insensitive(self):
        from app.ai.sessions.prompts import compute_wrong_items

        user_response = {"b1": "  Brush  ", "b2": "EATS", "b3": "walks", "b4": "drink"}
        assert compute_wrong_items(self._task(), user_response) == []

    def test_blank_answer_not_flagged_as_mistake(self):
        from app.ai.sessions.prompts import compute_wrong_items

        user_response = {"b1": "brush", "b2": "", "b3": "walks", "b4": "drink"}
        wrong = compute_wrong_items(self._task(), user_response)
        assert not any(w["item_id"] == "b2" for w in wrong)

    def test_listen_cloze_wrong_answers_use_inner_response(self):
        from app.ai.sessions.prompts import compute_listen_cloze_wrong_items

        task_content = {
            "items": [
                {"item_id": "b1", "correct_answer": "got", "explanation": "get -> got"},
                {
                    "item_id": "b2",
                    "correct_answer": "had",
                    "explanation": "have -> had",
                },
            ]
        }
        user_response = {
            "inner_response": {
                "widget": "fill_in_blanks",
                "answers": [
                    {"item_id": "b1", "user_answer": "got"},
                    {"item_id": "b2", "user_answer": "haved"},
                ],
            }
        }

        wrong = compute_listen_cloze_wrong_items(task_content, user_response)
        assert len(wrong) == 1
        assert wrong[0]["item_id"] == "b2"
        assert wrong[0]["correct_answer"] == "had"


class TestComputeErrorCorrectionWrongItems:
    """Deterministic answer-key checking for error-correction items.

    The learner submits a flat ``{item_id: corrected_text}`` map; each item's
    ``sample_answer`` is the key. Comparison ignores case and trailing
    punctuation (sentence normalization), mirroring the grading intent.
    """

    def _task(self):
        return {
            "widget": "error_correction",
            "items": [
                {
                    "item_id": "e1",
                    "incorrect_sentence": "She walk to work.",
                    "sample_answer": "She walked to work.",
                    "watch_hints": ["tense"],
                },
                {
                    "item_id": "e2",
                    "incorrect_sentence": "They was happy.",
                    "sample_answer": "They were happy.",
                    "watch_hints": ["agreement"],
                },
                {
                    "item_id": "e3",
                    "incorrect_sentence": "He go home yesterday.",
                    "sample_answer": "He went home yesterday.",
                    "watch_hints": ["irregular past"],
                },
            ],
        }

    def test_only_unfixed_items_are_flagged(self):
        from app.ai.sessions.prompts import compute_error_correction_wrong_items

        user_response = {
            "e1": "She walk to work.",  # unchanged → wrong
            "e2": "They were happy.",  # fixed → correct
            "e3": "He went home yesterday.",  # fixed → correct
        }
        wrong = compute_error_correction_wrong_items(self._task(), user_response)
        assert [w["item_id"] for w in wrong] == ["e1"]
        assert wrong[0]["user_wrote"] == "She walk to work."
        assert wrong[0]["correct_answer"] == "She walked to work."
        # watch_hints become the rule hint.
        assert wrong[0]["explanation"] == "tense"

    def test_case_and_trailing_punctuation_insensitive(self):
        from app.ai.sessions.prompts import compute_error_correction_wrong_items

        user_response = {
            "e1": "she walked to work",  # no capital, no period → still correct
            "e2": "  They Were Happy!  ",  # spacing + casing + ! → still correct
            "e3": "He went home yesterday.",
        }
        assert compute_error_correction_wrong_items(self._task(), user_response) == []

    def test_blank_answer_not_flagged(self):
        from app.ai.sessions.prompts import compute_error_correction_wrong_items

        user_response = {
            "e1": "",
            "e2": "They were happy.",
            "e3": "He went home yesterday.",
        }
        wrong = compute_error_correction_wrong_items(self._task(), user_response)
        assert not any(w["item_id"] == "e1" for w in wrong)


class TestFeedbackConfirmedMistakes:
    """Tests that the feedback generator threads confirmed_mistakes into the prompt
    for fill_in_blanks and that open-text widgets are unaffected."""

    def _fill_blanks_archetype(self):
        return get_archetype("READ_CLOZE")

    def _open_text_archetype(self):
        return get_archetype("WRITE_EMAIL")

    def _eval(self):
        from app.modules.sessions.evaluator import EvaluationResult

        return EvaluationResult(raw_score=7.5, rubric_scores={}, evaluator_notes=None)

    def _canned_feedback(self, spec):
        return FeedbackOutput(
            score=8,
            summary="Good work.",
            mistakes=[],
            sub_skill_breakdown={skill: 8 for skill in spec.weight_map},
        )

    @pytest.mark.asyncio
    async def test_fill_blanks_injects_confirmed_wrong_answers_in_prompt(self):
        """When the task is fill_in_blanks, the prompt must contain the
        pre-computed confirmed_wrong_answers section listing only real mistakes."""
        spec = self._fill_blanks_archetype()
        fake = FakeLLMClient([self._canned_feedback(spec)])
        agent = LLMFeedbackGenerator(fake)

        task_content = {
            "items": [
                {
                    "item_id": "b1",
                    "correct_answer": "brush",
                    "explanation": "base verb for I",
                },
                {
                    "item_id": "b2",
                    "correct_answer": "eats",
                    "explanation": "she adds -s",
                },
                {
                    "item_id": "b3",
                    "correct_answer": "walks",
                    "explanation": "he adds -s",
                },
                {
                    "item_id": "b4",
                    "correct_answer": "drink",
                    "explanation": "they takes base verb",
                },
            ]
        }
        user_response = {"b1": "brush", "b2": "eat", "b3": "walks", "b4": "drink"}

        await agent.generate(
            archetype=spec,
            evaluation=self._eval(),
            user_response=user_response,
            task_content=task_content,
        )

        prompt = fake.calls[0]["user_prompt"]
        # Confirmed section must be present.
        marker = "confirmed wrong answers"
        assert marker in prompt.lower(), (
            "Expected 'Confirmed wrong answers' section in prompt"
        )
        # Extract only the confirmed section (everything after the marker).
        confirmed_section = prompt.lower().split(marker, 1)[1]
        # b2 (the wrong answer) must appear in the confirmed section.
        assert '"b2"' in confirmed_section
        # b4 (correct answer "drink" for "they") must NOT appear in the confirmed section.
        assert '"b4"' not in confirmed_section

    @pytest.mark.asyncio
    async def test_error_correction_injects_confirmed_wrong_answers(self):
        """error_correction is no longer open-ended: the prompt must carry the
        deterministic confirmed set (real misses only), not the open-ended block."""
        spec = get_archetype("WRITE_ERROR_CORR")
        fake = FakeLLMClient([self._canned_feedback(spec)])
        agent = LLMFeedbackGenerator(fake)

        await agent.generate(
            archetype=spec,
            evaluation=self._eval(),
            user_response={
                "e1": "She walk to work.",  # wrong (unchanged)
                "e2": "They were happy.",  # correct
            },
            task_content={
                "widget": "error_correction",
                "items": [
                    {
                        "item_id": "e1",
                        "incorrect_sentence": "She walk to work.",
                        "sample_answer": "She walked to work.",
                        "watch_hints": ["tense"],
                    },
                    {
                        "item_id": "e2",
                        "incorrect_sentence": "They was happy.",
                        "sample_answer": "They were happy.",
                        "watch_hints": ["agreement"],
                    },
                ],
            },
        )

        prompt = fake.calls[0]["user_prompt"]
        assert "open-ended feedback mode" not in prompt.lower()
        confirmed_section = prompt.lower().split("confirmed wrong answers", 1)[1]
        assert '"e1"' in confirmed_section
        assert '"e2"' not in confirmed_section

    @pytest.mark.asyncio
    async def test_open_text_does_not_inject_confirmed_mistakes(self):
        """Non-deterministic widget types must NOT include the confirmed_wrong_answers
        section — the LLM should judge quality freely for open-ended responses."""
        spec = self._open_text_archetype()
        fake = FakeLLMClient([self._canned_feedback(spec)])
        agent = LLMFeedbackGenerator(fake)

        await agent.generate(
            archetype=spec,
            evaluation=self._eval(),
            user_response={"text": "I am write to apologise."},
            task_content={"topic": "Apology email"},
        )

        prompt = fake.calls[0]["user_prompt"]
        assert "confirmed wrong answers" not in prompt.lower()
        assert "Open-ended feedback mode" in prompt
        assert "improved version" in prompt
        assert "preserves the same idea" in prompt

    @pytest.mark.asyncio
    async def test_listen_cloze_injects_confirmed_wrong_answers_in_prompt(self):
        spec = get_archetype("LISTEN_CLOZE")
        fake = FakeLLMClient([self._canned_feedback(spec)])
        agent = LLMFeedbackGenerator(fake)

        await agent.generate(
            archetype=spec,
            evaluation=self._eval(),
            user_response={
                "inner_response": {
                    "widget": "fill_in_blanks",
                    "answers": [
                        {"item_id": "b1", "user_answer": "got"},
                        {"item_id": "b2", "user_answer": "haved"},
                    ],
                }
            },
            task_content={
                "widget": "listen_and_respond",
                "inner_widget": "fill_in_blanks",
                "items": [
                    {
                        "item_id": "b1",
                        "correct_answer": "got",
                        "explanation": "get -> got",
                    },
                    {
                        "item_id": "b2",
                        "correct_answer": "had",
                        "explanation": "have -> had",
                    },
                ],
            },
        )

        confirmed_section = (
            fake.calls[0]["user_prompt"]
            .lower()
            .split(
                "confirmed wrong answers",
                1,
            )[1]
        )
        assert '"b2"' in confirmed_section
        assert '"b1"' not in confirmed_section

    @pytest.mark.asyncio
    async def test_read_word_match_mcq_feedback_uses_option_labels_not_indices(self):
        """Standalone MCQ widgets (e.g. READ_WORD_MATCH) must show option text."""
        spec = get_archetype("READ_WORD_MATCH")
        fake = FakeLLMClient(
            [
                FeedbackOutput(
                    score=8,
                    summary="Good effort on articles.",
                    mistakes=[
                        MistakeOutSchema(
                            issue="Wrong pick for hour",
                            user_wrote="0",
                            correction="1",
                            rule="Use an before vowel sounds.",
                        )
                    ],
                )
            ]
        )
        agent = LLMFeedbackGenerator(fake)

        task_content = {
            "items": [
                {
                    "item_id": "hour",
                    "prompt": "hour",
                    "options": ["a", "an", "the"],
                    "correct_index": 1,
                    "explanation": "Use 'an' before vowel sounds, like 'hour'.",
                }
            ]
        }
        user_response = {
            "hour": 0,
            "inner_response": {
                "widget": "mcq",
                "answers": [{"item_id": "hour", "selected_index": 0}],
            },
        }

        result = await agent.generate(
            archetype=spec,
            evaluation=self._eval(),
            user_response=user_response,
            task_content=task_content,
        )

        assert len(result.mistakes) == 1
        assert result.mistakes[0].user_wrote == "a"
        assert result.mistakes[0].correction == "an"
        assert result.mistakes[0].issue == "'hour'"


# ── Registry sanity (Phase 4: every archetype must be invokable) ───
