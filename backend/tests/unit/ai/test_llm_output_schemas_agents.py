"""FillInBlanks + ErrorSpotting LLM-output schema validation.

Split out of the former monolithic test_llm_session_agents.py.
"""

from __future__ import annotations


import pytest
from pydantic import ValidationError

from app.ai.sessions.llm_task_generator import (
    ErrorSpottingTask,
)
from app.modules.sessions.task_generator import normalize_error_spotting_payload
from app.tasks.schemas import FillInBlanksTask

# Canonical fakes (Phase 3 — moved out of this file into tests/mocks/).
from tests.unit.ai._llm_agent_support import _error_spotting_content


class TestFillInBlanksSchema:
    def test_accepts_w1d1_style_payload(self):
        task = FillInBlanksTask(
            topic="Simple present routines",
            instructions="Fill each blank with the correct simple present verb.",
            items=[
                {
                    "item_id": "routine_1",
                    "sentence_with_blank": "She usually ___ breakfast.",
                    "base_verb": "eat",
                    "correct_answer": "eats",
                    "explanation": "With she, add -s.",
                }
            ],
        )

        assert task.total_blanks == 1

    def test_rejects_missing_blank_marker_and_answer(self):
        with pytest.raises(ValidationError):
            FillInBlanksTask(
                topic="Simple present routines",
                instructions="Fill the blank.",
                items=[
                    {
                        "item_id": "routine_1",
                        "sentence_with_blank": "She usually eats breakfast.",
                        "correct_answer": "",
                        "explanation": "With she, add -s.",
                    }
                ],
            )


class TestErrorSpottingSchema:
    def test_accepts_word_level_error_spotting_payload(self):
        task = ErrorSpottingTask.model_validate(_error_spotting_content())

        assert task.total_errors == 5
        assert len(task.passage_sentences) == 5

    def test_accepts_fewer_than_five_sentences(self):
        # Exact-count is a quality target, not a render requirement — fewer
        # sentences validate and the derived total is coerced to the real count.
        payload = _error_spotting_content()
        payload["passage_sentences"] = payload["passage_sentences"][:4]

        task = ErrorSpottingTask.model_validate(payload)
        assert task.total_errors == 4

    def test_accepts_low_diversity_error_types(self):
        # <4 distinct categories is logged as a quality miss, not raised — a
        # stochastic LLM output must never fail the learner's session.
        payload = _error_spotting_content()
        for sentence in payload["passage_sentences"]:
            sentence["error"]["error_type"] = "regular_past_ending"

        task = ErrorSpottingTask.model_validate(payload)
        assert task.total_errors == 5

    def test_rejects_sentence_without_a_marked_error_token(self):
        # Structural integrity stays a hard gate: the widget can't render a
        # sentence that has no clickable error token.
        payload = _error_spotting_content()
        for token in payload["passage_sentences"][0]["tokens"]:
            token["is_error"] = False

        with pytest.raises(ValidationError):
            ErrorSpottingTask.model_validate(payload)

    def test_normalize_syncs_is_error_flags_before_strict_validation(self):
        payload = _error_spotting_content()
        sentence = payload["passage_sentences"][2]
        for token in sentence["tokens"]:
            token["is_error"] = False
        sentence["tokens"][0]["is_error"] = True
        sentence["tokens"][1]["is_error"] = True

        normalized = normalize_error_spotting_payload(payload)
        strict_payload = {
            key: value for key, value in normalized.items() if key != "widget"
        }
        task = ErrorSpottingTask.model_validate(strict_payload)

        error_tokens = [
            token.token_id
            for token in task.passage_sentences[2].tokens
            if token.is_error
        ]
        assert error_tokens == ["s3_t4"]
