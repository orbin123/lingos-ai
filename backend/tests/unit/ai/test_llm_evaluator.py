"""LLMEvaluator: output parsing, rubric fallback, deterministic rule-based scoring.

Split out of the former monolithic test_llm_session_agents.py.
"""

from __future__ import annotations

import json

import pytest

from app.ai.llm.exceptions import LLMError
from app.ai.sessions.llm_evaluator import EvaluationOutput, LLMEvaluator
from app.ai.sessions.prompts import compute_mcq_wrong_items
from app.scoring import get_archetype

# Canonical fakes (Phase 3 — moved out of this file into tests/mocks/).
from tests.mocks.llm import FakeLLMClient
from tests.unit.ai._llm_agent_support import _error_spotting_content


class TestLLMEvaluator:
    @pytest.mark.asyncio
    async def test_passes_through_valid_output(self):
        spec = get_archetype("WRITE_EMAIL")
        canned = EvaluationOutput(
            raw_score=7.5,
            rubric_scores={r: 7.5 for r in spec.rubric},
            evaluator_notes="Decent overall; tone slipped near the end.",
        )
        fake = FakeLLMClient([canned])
        agent = LLMEvaluator(fake)

        result = await agent.evaluate(
            archetype=spec,
            task_content={"topic": "Apology email"},
            user_response={"text": "I'm sorry I missed standup."},
        )

        assert result.raw_score == 7.5
        assert set(result.rubric_scores) == set(spec.rubric)
        assert result.evaluator_notes == "Decent overall; tone slipped near the end."
        # Prompt assembly invoked exactly once with the right schema.
        assert len(fake.calls) == 1
        assert fake.calls[0]["output_model"] is EvaluationOutput

    @pytest.mark.asyncio
    async def test_missing_rubric_keys_fall_back_to_raw_score(self):
        spec = get_archetype("WRITE_EMAIL")
        fake = FakeLLMClient(
            [
                EvaluationOutput(raw_score=6.0, rubric_scores={}, evaluator_notes=""),
            ]
        )
        agent = LLMEvaluator(fake)
        result = await agent.evaluate(
            archetype=spec,
            task_content={},
            user_response={"x": "y"},
        )
        assert set(result.rubric_scores) == set(spec.rubric)
        assert all(v == 6.0 for v in result.rubric_scores.values())

    @pytest.mark.asyncio
    async def test_no_response_short_circuits_without_llm_call(self):
        spec = get_archetype("READ_COMP_MCQ")
        fake = FakeLLMClient([])  # empty — would raise if called
        agent = LLMEvaluator(fake)

        result = await agent.evaluate(
            archetype=spec,
            task_content={},
            user_response=None,
        )
        assert result.raw_score == 0.0
        assert all(v == 0.0 for v in result.rubric_scores.values())
        assert "No response" in (result.evaluator_notes or "")
        assert fake.calls == []

    @pytest.mark.asyncio
    async def test_llm_failure_falls_back_to_mid_range(self):
        spec = get_archetype("WRITE_EMAIL")
        fake = FakeLLMClient([LLMError("simulated provider outage")])
        agent = LLMEvaluator(fake)

        result = await agent.evaluate(
            archetype=spec,
            task_content={},
            user_response={"x": "y"},
        )
        assert result.raw_score == 5.0
        assert all(v == 5.0 for v in result.rubric_scores.values())
        assert "unavailable" in (result.evaluator_notes or "").lower()

    @pytest.mark.asyncio
    async def test_listen_mcq_scores_deterministically_without_llm_call(self):
        spec = get_archetype("LISTEN_MCQ")
        fake = FakeLLMClient([])
        agent = LLMEvaluator(fake)

        result = await agent.evaluate(
            archetype=spec,
            task_content={
                "items": [
                    {
                        "item_id": "q1",
                        "options": ["A", "B", "C", "D"],
                        "correct_index": 1,
                    },
                    {
                        "item_id": "q2",
                        "options": ["A", "B", "C", "D"],
                        "correct_index": 2,
                    },
                    {
                        "item_id": "q3",
                        "options": ["A", "B", "C", "D"],
                        "correct_index": 0,
                    },
                ]
            },
            user_response={
                "inner_response": {
                    "widget": "mcq",
                    "answers": [
                        {"item_id": "q1", "selected_index": 1},
                        {"item_id": "q2", "selected_index": 0},
                    ],
                }
            },
        )

        assert result.raw_score == 3.3
        assert all(value == 3.3 for value in result.rubric_scores.values())
        assert "1/3 correct" in (result.evaluator_notes or "")
        assert "1 missing" in (result.evaluator_notes or "")

    @pytest.mark.asyncio
    async def test_listen_mcq_scores_flat_live_answer_map_without_llm_call(self):
        spec = get_archetype("LISTEN_MCQ")
        fake = FakeLLMClient([])
        agent = LLMEvaluator(fake)

        result = await agent.evaluate(
            archetype=spec,
            task_content={
                "items": [
                    {"item_id": "q1", "options": ["A", "B"], "correct_index": 1},
                    {"item_id": "q2", "options": ["A", "B"], "correct_index": 0},
                ]
            },
            user_response={"q1": 1, "q2": 0},
        )

        assert result.raw_score == 10.0
        assert all(value == 10.0 for value in result.rubric_scores.values())
        assert fake.calls == []

    @pytest.mark.asyncio
    async def test_read_cloze_scores_deterministically_without_llm_call(self):
        spec = get_archetype("READ_CLOZE")
        fake = FakeLLMClient([])
        agent = LLMEvaluator(fake)

        result = await agent.evaluate(
            archetype=spec,
            task_content={
                "items": [
                    {"item_id": "b1", "correct_answer": "brush"},
                    {"item_id": "b2", "correct_answer": "eats"},
                    {"item_id": "b3", "correct_answer": "walks"},
                    {"item_id": "b4", "correct_answer": "drink"},
                ]
            },
            user_response={
                "b1": "brush",
                "b2": "eats",
                "b3": "walk",
                "b4": "drink",
            },
        )

        assert result.raw_score == 7.5
        assert all(value == 7.5 for value in result.rubric_scores.values())
        notes = json.loads(result.evaluator_notes or "{}")
        assert notes["correct_count"] == 3
        assert notes["total_blanks"] == 4
        assert fake.calls == []

    def test_listen_mcq_feedback_accepts_flat_live_answer_map(self):
        wrong = compute_mcq_wrong_items(
            {
                "items": [
                    {
                        "item_id": "q1",
                        "options": ["Morning", "Evening"],
                        "correct_index": 1,
                        "explanation": "The speaker says evening.",
                    }
                ]
            },
            {"q1": 0},
        )

        assert wrong == [
            {
                "item_id": "q1",
                "prompt": "",
                "user_selected": "Morning",
                "correct_answer": "Evening",
                "user_wrote": "Morning",
                "correction": "Evening",
                "explanation": "The speaker says evening.",
            }
        ]

    @pytest.mark.asyncio
    async def test_error_spotting_scores_selected_error_tokens(self):
        spec = get_archetype("READ_ERROR_SPOT")
        fake = FakeLLMClient([])
        agent = LLMEvaluator(fake)

        result = await agent.evaluate(
            archetype=spec,
            task_content=_error_spotting_content(),
            user_response={
                "selected_token_ids": [
                    "s1_t3",
                    "s2_t3",
                    "s3_t4",
                    "s4_t4",
                    "s5_t4",
                ],
            },
        )

        assert result.raw_score == 10.0
        assert all(value == 10.0 for value in result.rubric_scores.values())
        assert '"correct_count": 5' in (result.evaluator_notes or "")
        assert fake.calls == []

    @pytest.mark.asyncio
    async def test_error_spotting_tracks_missed_and_false_positive_tokens(self):
        spec = get_archetype("READ_ERROR_SPOT")
        fake = FakeLLMClient([])
        agent = LLMEvaluator(fake)

        result = await agent.evaluate(
            archetype=spec,
            task_content=_error_spotting_content(),
            user_response={"selected_token_ids": ["s1_t3", "s2_t1"]},
        )

        assert result.raw_score == 2.0
        notes = result.evaluator_notes or ""
        assert '"found_token_ids": ["s1_t3"]' in notes
        assert '"false_positive_token_ids": ["s2_t1"]' in notes
        assert '"total_errors": 5' in notes
        assert fake.calls == []
        assert fake.calls == []

    @pytest.mark.asyncio
    async def test_speak_timed_empty_transcripts_short_circuits_without_llm(self):
        spec = get_archetype("SPEAK_TIMED")
        fake = FakeLLMClient([])
        agent = LLMEvaluator(fake)

        result = await agent.evaluate(
            archetype=spec,
            task_content={
                "speaking_prompts": [
                    "Say a routine sentence with I and a frequency adverb.",
                    "Say a routine sentence with he and a frequency adverb.",
                    "Say a routine sentence with she and a frequency adverb.",
                ],
            },
            user_response={"recordings": []},
        )

        assert result.raw_score == 0.0
        assert all(v == 0.0 for v in result.rubric_scores.values())
        assert result.evaluator_notes == "No speech transcript was submitted."
        assert fake.calls == []

    @pytest.mark.asyncio
    async def test_speak_timed_passes_aligned_transcripts_to_llm(self):
        spec = get_archetype("SPEAK_TIMED")
        canned = EvaluationOutput(
            raw_score=8.0,
            evaluator_notes="Good verb forms and frequency adverbs.",
        )
        fake = FakeLLMClient([canned])
        agent = LLMEvaluator(fake)

        user_response = {
            "recordings": [
                {
                    "item_id": "prompt_1",
                    "transcript": "I usually drink water in the morning.",
                    "audio_blob_url": "/audio/a.webm",
                    "duration_seconds": 8,
                    "attempt_number": 1,
                },
                {
                    "item_id": "prompt_2",
                    "transcript": "He often walks to school.",
                    "audio_blob_url": "/audio/b.webm",
                    "duration_seconds": 7,
                    "attempt_number": 1,
                },
                {
                    "item_id": "prompt_3",
                    "transcript": "She always eats breakfast at seven.",
                    "audio_blob_url": "/audio/c.webm",
                    "duration_seconds": 9,
                    "attempt_number": 1,
                },
            ],
            "time_spent_seconds": 45,
        }
        task_content = {
            "speaking_prompts": [
                "Say a routine sentence with I and a frequency adverb.",
                "Say a routine sentence with he and a frequency adverb.",
                "Say a routine sentence with she and a frequency adverb.",
            ],
            "sample_responses": [
                "I usually drink water in the morning.",
                "He often walks to school.",
                "She always eats breakfast at seven.",
            ],
            "grammar_rule_to_practice": "Use base verb with I; add -s for he/she.",
        }

        result = await agent.evaluate(
            archetype=spec,
            task_content=task_content,
            user_response=user_response,
        )

        assert result.raw_score == 8.0
        assert len(fake.calls) == 1
        prompt = fake.calls[0]["user_prompt"]
        assert "I usually drink water in the morning." in prompt
        assert "He often walks to school." in prompt
        assert "She always eats breakfast at seven." in prompt
        assert "learner_transcript" in prompt


# ── LLMFeedbackGenerator ───────────────────────────────────────────
