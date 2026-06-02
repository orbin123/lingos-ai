"""Tests for the LLM-driven sessions agents.

A `FakeLLMClient` returns canned Pydantic instances so we exercise the
agent wiring (prompt assembly, fallback handling, output validation)
without ever hitting OpenAI. Phase 4 wires these agents into production
routes; these tests lock the contracts the routes depend on.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from app.ai.llm.exceptions import LLMError, LLMProviderError
from app.ai.sessions.llm_evaluator import EvaluationOutput, LLMEvaluator
from app.ai.sessions.llm_feedback import FeedbackOutput, LLMFeedbackGenerator, MistakeOutSchema
from app.ai.sessions.prompts import compute_mcq_wrong_items
from app.ai.sessions.exceptions import TaskGenerationFailed
from app.ai.sessions.llm_task_generator import (
    ErrorSpottingTask,
    ErrorSpottingTaskLLM,
    ErrorCorrectionTask,
    LLMTaskGenerator,
    TaskGenOutput,
)
from app.modules.sessions.task_generator import normalize_error_spotting_payload
from app.scoring import ARCHETYPE_REGISTRY, get_archetype
from app.tasks.schemas import FillInBlanksTask
from app.tasks.schemas.llm_output_schemas import FillInBlanksTaskLLM


# ── Fake LLM client ────────────────────────────────────────────────


class FakeLLMClient:
    """Returns a queued sequence of responses; raises if the queue is empty.

    `responses` is a list of either:
      - BaseModel instances (returned to the caller as-is)
      - Exception instances (raised when generate_structured is invoked)
    """

    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.calls: list[dict] = []

    async def generate_text(self, **_kwargs) -> str:  # pragma: no cover
        raise NotImplementedError

    def stream_text(self, **_kwargs) -> AsyncIterator[str]:  # pragma: no cover
        raise NotImplementedError

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_model: type[BaseModel],
        temperature: float | None = None,
    ) -> BaseModel:
        self.calls.append({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "output_model": output_model,
            "temperature": temperature,
        })
        if not self._responses:
            raise LLMProviderError("FakeLLMClient: no more queued responses")
        resp = self._responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp


class FakeTTSService:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[dict] = []

    async def synthesize(self, *, text: str, **kwargs):
        self.calls.append({"text": text, **kwargs})
        if self.fail:
            raise RuntimeError("tts down")
        return {
            "audio_url": "/audio/fake-listening.mp3",
            "duration_seconds": 12.4,
        }


class FakeImageGenService:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[dict] = []

    async def generate(self, *, prompt: str, **kwargs):
        self.calls.append({"prompt": prompt, **kwargs})
        if self.fail:
            raise RuntimeError("imagegen down")
        return {
            "image_url": "/images/ab/fake-scene.png",
            "width": 1536,
            "height": 1024,
            "cache_hit": False,
        }


def _error_spotting_content() -> dict:
    return {
        "topic": "Spot past tense errors",
        "instructions": "Tap each word in the passage that contains a grammatical error.",
        "task_intro": "Tap each word that has a grammatical error.",
        "passage_sentences": [
            {
                "sentence_id": "s1",
                "tokens": [
                    {"token_id": "s1_t1", "text": "Yesterday", "is_error": False},
                    {"token_id": "s1_t2", "text": "I", "is_error": False},
                    {"token_id": "s1_t3", "text": "goed", "is_error": True},
                ],
                "error": {
                    "token_id": "s1_t3",
                    "incorrect_phrase": "goed",
                    "correction": "went",
                    "error_type": "irregular_past",
                    "rule": "Use went as the past form of go.",
                    "explanation": "Go is irregular in the past.",
                },
            },
            {
                "sentence_id": "s2",
                "tokens": [
                    {"token_id": "s2_t1", "text": "She", "is_error": False},
                    {"token_id": "s2_t2", "text": "did", "is_error": False},
                    {"token_id": "s2_t3", "text": "finished", "is_error": True},
                ],
                "error": {
                    "token_id": "s2_t3",
                    "incorrect_phrase": "finished",
                    "correction": "finish",
                    "error_type": "missing_past_auxiliary",
                    "rule": "After did, use the base verb.",
                    "explanation": "Did already carries the past tense.",
                },
            },
            {
                "sentence_id": "s3",
                "tokens": [
                    {"token_id": "s3_t1", "text": "The", "is_error": False},
                    {"token_id": "s3_t2", "text": "manager", "is_error": False},
                    {"token_id": "s3_t3", "text": "was", "is_error": False},
                    {"token_id": "s3_t4", "text": "hire", "is_error": True},
                ],
                "error": {
                    "token_id": "s3_t4",
                    "incorrect_phrase": "hire",
                    "correction": "hired",
                    "error_type": "passive_helper_missing",
                    "rule": "Use was/were + past participle in passive voice.",
                    "explanation": "The passive form needs the past participle.",
                },
            },
            {
                "sentence_id": "s4",
                "tokens": [
                    {"token_id": "s4_t1", "text": "Last", "is_error": False},
                    {"token_id": "s4_t2", "text": "week", "is_error": False},
                    {"token_id": "s4_t3", "text": "we", "is_error": False},
                    {"token_id": "s4_t4", "text": "visit", "is_error": True},
                ],
                "error": {
                    "token_id": "s4_t4",
                    "incorrect_phrase": "visit",
                    "correction": "visited",
                    "error_type": "time_marker_mismatch",
                    "rule": "Use a past verb with a past time marker.",
                    "explanation": "Last week points to finished time.",
                },
            },
            {
                "sentence_id": "s5",
                "tokens": [
                    {"token_id": "s5_t1", "text": "They", "is_error": False},
                    {"token_id": "s5_t2", "text": "had", "is_error": False},
                    {"token_id": "s5_t3", "text": "good", "is_error": False},
                    {"token_id": "s5_t4", "text": "advices", "is_error": True},
                    {"token_id": "s5_t5", "text": "yesterday.", "is_error": False},
                ],
                "error": {
                    "token_id": "s5_t4",
                    "incorrect_phrase": "advices",
                    "correction": "advice",
                    "error_type": "object_or_complement_mismatch",
                    "rule": "Advice is uncountable.",
                    "explanation": "Use advice, not advices.",
                },
            },
        ],
        "total_errors": 5,
    }


# ── LLMEvaluator ───────────────────────────────────────────────────


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
        fake = FakeLLMClient([
            EvaluationOutput(raw_score=6.0, rubric_scores={}, evaluator_notes=""),
        ])
        agent = LLMEvaluator(fake)
        result = await agent.evaluate(
            archetype=spec, task_content={}, user_response={"x": "y"},
        )
        assert set(result.rubric_scores) == set(spec.rubric)
        assert all(v == 6.0 for v in result.rubric_scores.values())

    @pytest.mark.asyncio
    async def test_no_response_short_circuits_without_llm_call(self):
        spec = get_archetype("READ_COMP_MCQ")
        fake = FakeLLMClient([])  # empty — would raise if called
        agent = LLMEvaluator(fake)

        result = await agent.evaluate(
            archetype=spec, task_content={}, user_response=None,
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
            archetype=spec, task_content={}, user_response={"x": "y"},
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
                    {"item_id": "q1", "options": ["A", "B", "C", "D"], "correct_index": 1},
                    {"item_id": "q2", "options": ["A", "B", "C", "D"], "correct_index": 2},
                    {"item_id": "q3", "options": ["A", "B", "C", "D"], "correct_index": 0},
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


class TestLLMFeedbackGenerator:
    def _eval(self):
        from app.modules.sessions.evaluator import EvaluationResult
        return EvaluationResult(
            raw_score=7.0,
            rubric_scores={"grammatical_accuracy": 7.0},
            evaluator_notes="Solid.",
        )

    @pytest.mark.asyncio
    async def test_passes_through_valid_output(self):
        spec = get_archetype("WRITE_EMAIL")
        canned = FeedbackOutput(
            score=7,
            summary="Polite tone, but two tense slips.",
            did_well=["Greeted appropriately."],
            mistakes=[
                MistakeOutSchema(
                    issue="Past tense form",
                    user_wrote="I was not joined the meeting",
                    correction="I couldn't join the meeting",
                    rule="Use couldn't + base verb for past inability.",
                    sub_skills_affected=["grammar"],
                ),
            ],
            next_tip="Re-read each verb for tense.",
            sub_skill_breakdown={skill: 7 for skill in spec.weight_map},
        )
        fake = FakeLLMClient([canned])
        agent = LLMFeedbackGenerator(fake)

        fb = await agent.generate(
            archetype=spec,
            evaluation=self._eval(),
            user_response={"text": "..."},
        )
        assert fb.score == 7
        assert fb.summary.startswith("Polite tone")
        assert len(fb.did_well) == 1
        assert len(fb.mistakes) == 1
        assert fb.mistakes[0].issue == "Past tense form"
        assert set(fb.sub_skill_breakdown) == set(spec.weight_map)

    @pytest.mark.asyncio
    async def test_caps_mistakes_at_three(self):
        spec = get_archetype("WRITE_EMAIL")
        canned = FeedbackOutput(
            score=4,
            summary="Several issues.",
            mistakes=[
                MistakeOutSchema(
                    issue=f"issue {i}",
                    user_wrote=f"bad wording {i}",
                    correction=f"better wording {i}",
                )
                for i in range(5)
            ],
            sub_skill_breakdown={skill: 4 for skill in spec.weight_map},
        )
        fake = FakeLLMClient([canned])
        agent = LLMFeedbackGenerator(fake)

        fb = await agent.generate(
            archetype=spec, evaluation=self._eval(), user_response={"x": "y"},
        )
        assert len(fb.mistakes) == 3

    @pytest.mark.asyncio
    async def test_filters_false_positive_open_text_mistakes(self):
        spec = get_archetype("WRITE_OPEN_SENT")
        canned = FeedbackOutput(
            score=9,
            summary="Clear routine sentences.",
            did_well=["Used frequency adverbs correctly."],
            mistakes=[
                MistakeOutSchema(
                    issue="Verb form",
                    user_wrote="I always practice machine learning code.",
                    correction="I always practice machine learning codes.",
                    rule="Use the base verb with I.",
                ),
                MistakeOutSchema(
                    issue="Subject-verb agreement",
                    user_wrote="He often reviews technical documentation.",
                    correction="He often review technical documentation.",
                    rule="Missing -s with he or she.",
                ),
                MistakeOutSchema(
                    issue="Subject-verb agreement",
                    user_wrote="She usually documents her project progress.",
                    correction="She usually document her project progress.",
                    rule="Missing -s with he or she.",
                ),
                MistakeOutSchema(
                    issue="Spelling",
                    user_wrote="I alway practice coding.",
                    correction="I always practice coding.",
                    rule="Use the full spelling of always.",
                ),
            ],
            sub_skill_breakdown={skill: 9 for skill in spec.weight_map},
        )
        fake = FakeLLMClient([canned])
        agent = LLMFeedbackGenerator(fake)

        fb = await agent.generate(
            archetype=spec,
            evaluation=self._eval(),
            user_response={
                "routine_i": "I always practice machine learning code.",
                "routine_he": "He often reviews technical documentation.",
                "routine_she": "She usually documents her project progress.",
            },
        )

        assert len(fb.mistakes) == 1
        assert fb.mistakes[0].issue == "Spelling"

    @pytest.mark.asyncio
    async def test_error_spotting_feedback_uses_learner_friendly_mistakes(self):
        spec = get_archetype("READ_ERROR_SPOT")
        canned = FeedbackOutput(
            score=4,
            summary="You found some errors, but missed two key corrections.",
            mistakes=[
                MistakeOutSchema(
                    issue="missing_past_auxiliary",
                    user_wrote="not selected",
                    correction="finish",
                    rule="After did, use the base verb.",
                ),
                MistakeOutSchema(
                    issue="object_or_complement_mismatch",
                    user_wrote="not selected",
                    correction="advice",
                    rule="Advice is uncountable.",
                ),
            ],
            next_tip="Check whether each flagged word is truly wrong.",
            sub_skill_breakdown={skill: 4 for skill in spec.weight_map},
        )
        fake = FakeLLMClient([canned])
        agent = LLMFeedbackGenerator(fake)

        fb = await agent.generate(
            archetype=spec,
            evaluation=self._eval(),
            user_response={
                "selected_token_ids": ["s1_t3", "s2_t1", "s3_t4", "s4_t4"],
            },
            task_content=_error_spotting_content(),
        )

        assert [m.user_wrote for m in fb.mistakes] == ["finished", "advices", "She"]
        assert [m.correction for m in fb.mistakes] == [
            "finish",
            "advice",
            "Do not flag this word",
        ]
        assert fb.mistakes[0].issue == '"finished" should be "finish".'
        assert fb.mistakes[1].issue == '"advices" should be "advice".'
        assert fb.mistakes[2].issue == '"She" was not an error.'
        assert "missing_past_auxiliary" not in {m.issue for m in fb.mistakes}
        assert "object_or_complement_mismatch" not in {m.issue for m in fb.mistakes}

    @pytest.mark.asyncio
    async def test_no_response_short_circuits(self):
        spec = get_archetype("READ_COMP_MCQ")
        fake = FakeLLMClient([])
        agent = LLMFeedbackGenerator(fake)

        fb = await agent.generate(
            archetype=spec, evaluation=self._eval(), user_response=None,
        )
        assert fb.score == 0
        assert "No response submitted" in fb.summary
        assert fake.calls == []

    @pytest.mark.asyncio
    async def test_llm_failure_falls_back_with_score(self):
        spec = get_archetype("WRITE_EMAIL")
        fake = FakeLLMClient([LLMError("provider down")])
        agent = LLMFeedbackGenerator(fake)

        fb = await agent.generate(
            archetype=spec, evaluation=self._eval(), user_response={"x": "y"},
        )
        # The fallback still uses the evaluation's rounded score.
        assert fb.score == 7
        assert "unavailable" in fb.summary.lower()
        assert set(fb.sub_skill_breakdown) == set(spec.weight_map)


# ── LLMTaskGenerator ───────────────────────────────────────────────


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

    def test_rejects_less_than_five_sentences(self):
        payload = _error_spotting_content()
        payload["passage_sentences"] = payload["passage_sentences"][:4]

        with pytest.raises(ValidationError):
            ErrorSpottingTask.model_validate(payload)

    def test_rejects_low_diversity_error_types(self):
        payload = _error_spotting_content()
        for sentence in payload["passage_sentences"]:
            sentence["error"]["error_type"] = "regular_past_ending"

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
        strict_payload = {key: value for key, value in normalized.items() if key != "widget"}
        task = ErrorSpottingTask.model_validate(strict_payload)

        error_tokens = [
            token.token_id
            for token in task.passage_sentences[2].tokens
            if token.is_error
        ]
        assert error_tokens == ["s3_t4"]


class TestLLMTaskGenerator:
    @pytest.mark.asyncio
    async def test_passes_through_valid_output(self):
        spec = get_archetype("WRITE_EMAIL")
        canned = TaskGenOutput(
            topic="Apology email to your team lead",
            instructions="Write a 4–5 sentence email apologising for missing standup.",
            primary_text="Scenario: You missed today's daily standup. Email your team lead.",
            target_words=["apologise", "standup", "async"],
        )
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Email writing",
            explanation_brief="A 4-5 sentence email at A2 level.",
            cefr_level="A2",
            sub_level=3,
            user_interests=["software engineering"],
        )

        c = generated.content
        assert c["phase"] == "live"
        assert c["archetype_id"] == "WRITE_EMAIL"
        assert c["topic"] == "Apology email to your team lead"
        assert "Write a 4–5 sentence email" in c["instructions"]
        assert c["primary_text"].startswith("Scenario:")
        assert c["target_words"] == ["apologise", "standup", "async"]
        assert c["cefr_level"] == "A2"
        assert c["sub_level"] == 3

    @pytest.mark.asyncio
    async def test_llm_failure_retries_once_then_raises(self):
        spec = get_archetype("WRITE_EMAIL")
        fake = FakeLLMClient([LLMError("provider down"), LLMError("still down")])
        agent = LLMTaskGenerator(fake)

        # No silent substitution: the LLM is retried once, then a typed error is
        # raised so the orchestrator can surface a clean error event.
        with pytest.raises(TaskGenerationFailed) as exc_info:
            await agent.generate(
                archetype=spec,
                day_topic="Email writing",
                explanation_brief="brief",
                cefr_level="A2",
                sub_level=3,
            )
        assert exc_info.value.archetype_id == "WRITE_EMAIL"
        assert len(fake.calls) == 2  # initial attempt + one retry

    @pytest.mark.asyncio
    async def test_fill_in_blanks_uses_widget_schema_and_protects_widget_key(self):
        spec = get_archetype("READ_CLOZE")
        canned = FillInBlanksTask(
            topic="Simple present routines",
            instructions="Fill each blank with the correct simple present verb.",
            task_intro="Complete the routine sentences.",
            grammar_rule_explained="Use base verbs with I and add -s with he/she.",
            items=[
                {
                    "item_id": "routine_1",
                    "sentence_with_blank": "He always ___ to school.",
                    "base_verb": "walk",
                    "correct_answer": "walks",
                    "explanation": "With he, add -s.",
                }
            ],
            widget="FillInBlanks",
            ui_widget="NotAWidget",
        )
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Simple present routines",
            explanation_brief="Routines with third-person -s.",
            cefr_level="A1",
            sub_level=1,
        )

        assert fake.calls[0]["output_model"] is FillInBlanksTaskLLM
        assert generated.content["widget"] == "fill_in_blanks"
        assert generated.content["ui_widget"] == "FillInBlanks"
        assert generated.content["items"][0]["correct_answer"] == "walks"

    @pytest.mark.asyncio
    async def test_error_spotting_uses_strict_widget_schema(self):
        spec = get_archetype("READ_ERROR_SPOT")
        canned = ErrorSpottingTask.model_validate(_error_spotting_content())
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Spot past tense errors",
            explanation_brief="Past tense error spotting.",
            cefr_level="A1",
            sub_level=1,
        )

        assert fake.calls[0]["output_model"] is ErrorSpottingTaskLLM
        content = generated.content
        assert content["phase"] == "live"
        assert content["widget"] == "error_spotting"
        assert content["ui_widget"] == "ErrorSpotting"
        assert content["total_errors"] == 5
        assert len(content["passage_sentences"]) == 5

    @pytest.mark.asyncio
    async def test_error_spotting_normalizes_mismatched_is_error_flags(self):
        spec = get_archetype("READ_ERROR_SPOT")
        payload = _error_spotting_content()
        sentence = payload["passage_sentences"][2]
        for token in sentence["tokens"]:
            token["is_error"] = False
        canned = ErrorSpottingTaskLLM.model_validate(payload)
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Spot past tense errors",
            explanation_brief="Past tense error spotting.",
            cefr_level="A1",
            sub_level=1,
        )

        error_tokens = [
            token["token_id"]
            for token in generated.content["passage_sentences"][2]["tokens"]
            if token.get("is_error")
        ]
        assert error_tokens == ["s3_t4"]

    @pytest.mark.asyncio
    async def test_error_spotting_failure_retries_then_raises(self):
        spec = get_archetype("READ_ERROR_SPOT")
        fake = FakeLLMClient([LLMError("provider down"), LLMError("still down")])
        agent = LLMTaskGenerator(fake)

        with pytest.raises(TaskGenerationFailed) as exc_info:
            await agent.generate(
                archetype=spec,
                day_topic="Spot past tense errors",
                explanation_brief="Past tense error spotting.",
                cefr_level="A1",
                sub_level=1,
            )
        assert exc_info.value.archetype_id == "READ_ERROR_SPOT"
        assert len(fake.calls) == 2

    @pytest.mark.asyncio
    async def test_w1d1_simple_present_fill_in_blanks_calls_llm(self):
        """W1D1 topic/instructions overrides no longer short-circuit to a
        hardcoded payload — the LLM is always called so learner interests
        and passage format requirements reach the model."""
        spec = get_archetype("READ_CLOZE")
        canned = FillInBlanksTask(
            topic="Simple present routines",
            instructions="Fill each blank with the correct simple present verb.",
            items=[
                {
                    "item_id": "b1",
                    "sentence_with_blank": "Every morning she ___ up early.",
                    "base_verb": "wake",
                    "correct_answer": "wakes",
                    "explanation": "With she, add -s.",
                }
            ],
        )
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Simple present routines",
            explanation_brief="Routines with third-person -s.",
            cefr_level="A1",
            sub_level=1,
            user_interests=["football"],
            task_spec={
                "topic_override": "Simple present routines",
                "instructions_override": (
                    "Write a 5–7 sentence connected passage about a "
                    "daily routine. Base the topic and characters on "
                    "the learner's interests. Focus on simple present "
                    "and third-person -s. Always include base_verb "
                    "for every blank."
                ),
            },
        )

        content = generated.content
        assert len(fake.calls) == 1, "LLM must be called — no hardcoded bypass"
        assert content["phase"] == "live"
        assert content["widget"] == "fill_in_blanks"
        prompt = fake.calls[0]["user_prompt"]
        assert "football" in prompt
        assert "base_verb" in prompt

    @pytest.mark.asyncio
    async def test_invalid_fill_in_blanks_output_retries_then_raises(self):
        spec = get_archetype("READ_CLOZE")
        invalid = TaskGenOutput(
            topic="Simple present routines",
            instructions="Fill the blanks.",
        )
        fake = FakeLLMClient([invalid, invalid])
        agent = LLMTaskGenerator(fake)

        with pytest.raises(TaskGenerationFailed) as exc_info:
            await agent.generate(
                archetype=spec,
                day_topic="Simple present routines",
                explanation_brief="Routines with third-person -s.",
                cefr_level="A1",
                sub_level=1,
            )
        assert exc_info.value.archetype_id == "READ_CLOZE"
        assert len(fake.calls) == 2

    @pytest.mark.asyncio
    async def test_write_open_sent_preserves_valid_open_text_items(self):
        spec = get_archetype("WRITE_OPEN_SENT")
        canned = TaskGenOutput(
            topic="Write simple present routine sentences",
            instructions=(
                "Write affirmative routine sentences with I, he, and she."
            ),
            grammar_rule_explained=(
                "Use base verbs with I and add -s with he or she."
            ),
            common_mistakes=["He walk -> He walks."],
            target_words=["always", "usually", "often"],
            items=[
                {
                    "item_id": "routine_i",
                    "prompt": "Write one I routine sentence with usually.",
                    "sample_answer": "I usually study English at night.",
                    "answer_hints": ["Start with I.", "Use a base verb."],
                },
                {
                    "item_id": "routine_he",
                    "prompt": "Write one he routine sentence with often.",
                    "sample_answer": "He often walks to work.",
                    "answer_hints": ["Start with He.", "Add -s to the verb."],
                },
                {
                    "item_id": "routine_she",
                    "prompt": "Write one she routine sentence with always.",
                    "sample_answer": "She always eats breakfast.",
                    "answer_hints": ["Start with She.", "Add -s to the verb."],
                },
            ],
        )
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Simple present routines",
            explanation_brief="Routine sentences with frequency adverbs.",
            cefr_level="A1",
            sub_level=1,
            task_spec={
                "topic_override": "Write simple present routine sentences",
                "instructions_override": (
                    "Ask for affirmative routine sentences using I/he/she "
                    "and frequency adverbs."
                ),
            },
        )

        content = generated.content
        assert content["phase"] == "live"
        assert content["widget"] == "open_text"
        assert content["ui_widget"] == "open_text"
        assert [item["item_id"] for item in content["items"]] == [
            "routine_i",
            "routine_he",
            "routine_she",
        ]
        prompt = fake.calls[0]["user_prompt"]
        assert "exactly 3 items" in prompt
        assert "frequency adverb" in prompt

    @pytest.mark.asyncio
    async def test_write_open_sent_malformed_output_retries_then_raises(self):
        spec = get_archetype("WRITE_OPEN_SENT")
        invalid = TaskGenOutput(
            topic="Write simple present routine sentences",
            instructions="Write routine sentences.",
            items=[],
        )
        fake = FakeLLMClient([invalid, invalid])
        agent = LLMTaskGenerator(fake)

        with pytest.raises(TaskGenerationFailed) as exc_info:
            await agent.generate(
                archetype=spec,
                day_topic="Simple present routines",
                explanation_brief="Routine sentences with frequency adverbs.",
                cefr_level="A1",
                sub_level=1,
            )
        assert exc_info.value.archetype_id == "WRITE_OPEN_SENT"
        assert len(fake.calls) == 2

    @pytest.mark.asyncio
    async def test_write_error_correction_preserves_valid_items(self):
        spec = get_archetype("WRITE_ERROR_CORR")
        canned = ErrorCorrectionTask(
            topic="Correct past tense mistakes",
            instructions="Rewrite each incorrect sentence so it is grammatically correct and natural.",
            task_intro="Correct past tense mistakes.",
            items=[
                {
                    "item_id": "ec_1",
                    "incorrect_sentence": "He don't have no time.",
                    "sample_answer": "He didn't have any time.",
                    "watch_hints": ["tense", "double negatives"],
                },
                {
                    "item_id": "ec_2",
                    "incorrect_sentence": "She goed home.",
                    "sample_answer": "She went home.",
                    "watch_hints": ["irregular past"],
                },
                {
                    "item_id": "ec_3",
                    "incorrect_sentence": "We didn't walked.",
                    "sample_answer": "We didn't walk.",
                    "watch_hints": ["did + base verb"],
                }
            ],
        )
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Simple past",
            explanation_brief="Past tense error correction.",
            cefr_level="A1",
            sub_level=1,
        )

        content = generated.content
        assert content["phase"] == "live"
        assert content["widget"] == "error_correction"
        assert content["ui_widget"] == "ErrorCorrection"
        assert len(content["items"]) == 3
        assert content["items"][0]["incorrect_sentence"] == "He don't have no time."
        assert content["items"][0]["watch_hints"] == ["tense", "double negatives"]

    @pytest.mark.asyncio
    async def test_write_error_correction_malformed_output_retries_then_raises(self):
        spec = get_archetype("WRITE_ERROR_CORR")
        invalid = TaskGenOutput(
            topic="Correct past tense mistakes",
            instructions="Rewrite sentences.",
            items=[],
        )
        fake = FakeLLMClient([invalid, invalid])
        agent = LLMTaskGenerator(fake)

        with pytest.raises(TaskGenerationFailed) as exc_info:
            await agent.generate(
                archetype=spec,
                day_topic="Simple past",
                explanation_brief="Past tense error correction.",
                cefr_level="A1",
                sub_level=1,
            )
        assert exc_info.value.archetype_id == "WRITE_ERROR_CORR"
        assert len(fake.calls) == 2


    @pytest.mark.asyncio
    async def test_speak_timed_preserves_valid_speak_payload(self):
        spec = get_archetype("SPEAK_TIMED")
        canned = TaskGenOutput(
            topic="Say simple present routines",
            instructions=(
                "Tap the mic and say one short routine sentence per prompt."
            ),
            task_intro="Record your routine sentences.",
            speaking_duration_seconds=45,
            speaking_prompts=[
                "Say a routine sentence with I and a frequency adverb.",
                "Say a routine sentence with he and a frequency adverb.",
                "Say a routine sentence with she and a frequency adverb.",
            ],
            sample_responses=[
                "I usually drink water in the morning.",
                "He often walks to school.",
                "She always eats breakfast at seven.",
            ],
            target_words=["always", "usually", "often", "sometimes", "never"],
        )
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Say simple present routines",
            explanation_brief="Routine sentences with frequency adverbs.",
            cefr_level="A1",
            sub_level=1,
            task_spec={
                "topic_override": "Say simple present routines",
                "instructions_override": (
                    "Prompt the learner to speak short routine sentences with "
                    "correct verb forms."
                ),
            },
        )

        content = generated.content
        assert content["phase"] == "live"
        assert content["widget"] == "speak_and_record"
        assert content["speaking_prompts"] == canned.speaking_prompts
        assert content["sample_responses"] == canned.sample_responses
        assert content["speaking_duration_seconds"] == 45

    @pytest.mark.asyncio
    async def test_speak_timed_malformed_output_retries_then_raises(self):
        spec = get_archetype("SPEAK_TIMED")
        invalid = TaskGenOutput(
            topic="Say simple present routines",
            instructions="Speak naturally.",
            speaking_prompts=[],
        )
        fake = FakeLLMClient([invalid, invalid])
        agent = LLMTaskGenerator(fake)

        with pytest.raises(TaskGenerationFailed) as exc_info:
            await agent.generate(
                archetype=spec,
                day_topic="Say simple present routines",
                explanation_brief="Routine sentences with frequency adverbs.",
                cefr_level="A1",
                sub_level=1,
            )
        assert exc_info.value.archetype_id == "SPEAK_TIMED"
        assert len(fake.calls) == 2

    @pytest.mark.asyncio
    async def test_speak_pic_desc_generates_required_image(self, monkeypatch):
        from app.ai import imagegen as imagegen_module

        spec = get_archetype("SPEAK_PIC_DESC")
        fake_imagegen = FakeImageGenService()
        monkeypatch.setattr(
            imagegen_module,
            "get_default_imagegen_service",
            lambda: fake_imagegen,
        )
        canned = TaskGenOutput(
            topic="Describe a picture using articles",
            instructions="Describe the picture aloud using a/an and the correctly.",
            task_intro="Record your description of the scene.",
            image_alt="A cat sleeping on a sofa next to an open book.",
            speaking_prompts=["Describe the cat using 'a' or 'the'."],
            sample_responses=[
                "I can see a cat on the sofa. The book is open next to the cat.",
            ],
            grammar_rule_to_practice=(
                "Use 'a' before consonant sounds, 'an' before vowel sounds, "
                "and 'the' for specific nouns."
            ),
            speaking_duration_seconds=45,
        )
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Articles in scene description",
            explanation_brief="Picture description with articles.",
            cefr_level="A1",
            sub_level=1,
            task_spec={
                "task_widget": "speak_pic_desc",
                "widget_requirements": (
                    "Target widget 'speak_pic_desc'. Provide image_alt describing "
                    "a simple scene."
                ),
            },
        )

        content = generated.content
        assert content["phase"] == "live"
        assert content["image_url"] == "/images/ab/fake-scene.png"
        assert content["image_alt"] == canned.image_alt
        assert content["speaking_prompts"] == ["Describe the cat using 'a' or 'the'."]
        assert len(fake_imagegen.calls) == 1
        assert fake_imagegen.calls[0]["prompt"] == canned.image_alt
        assert fake_imagegen.calls[0]["aspect_ratio"] == "landscape"

    @pytest.mark.asyncio
    async def test_speak_pic_desc_image_failure_sets_error(self, monkeypatch):
        from app.ai import imagegen as imagegen_module

        spec = get_archetype("SPEAK_PIC_DESC")
        fake_imagegen = FakeImageGenService(fail=True)
        monkeypatch.setattr(
            imagegen_module,
            "get_default_imagegen_service",
            lambda: fake_imagegen,
        )
        canned = TaskGenOutput(
            topic="Describe a picture using articles",
            instructions="Describe the picture aloud.",
            task_intro="Record your description of the scene.",
            image_alt="A cat on a sofa.",
            speaking_prompts=["Describe what you see."],
            sample_responses=["I see a cat on the sofa."],
            grammar_rule_to_practice="Use articles correctly.",
            speaking_duration_seconds=45,
        )
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Articles",
            explanation_brief="Picture description.",
            cefr_level="A1",
            sub_level=1,
        )

        content = generated.content
        assert content.get("image_url") is None
        assert "image_error" in content
        assert "SPEAK_PIC_DESC" in content["image_error"]

    @pytest.mark.asyncio
    async def test_listen_mcq_synthesizes_required_audio(self, monkeypatch):
        from app.ai import tts as tts_module

        spec = get_archetype("LISTEN_MCQ")
        fake_tts = FakeTTSService()
        monkeypatch.setattr(tts_module, "get_default_tts_service", lambda: fake_tts)
        canned = TaskGenOutput(
            topic="Listening for routines",
            instructions="Listen and answer the questions.",
            audio_script="Mina usually studies English after breakfast.",
            inner_widget="MCQList",
            items=[
                {
                    "item_id": "q1",
                    "prompt": "When does Mina study English?",
                    "options": ["Before bed", "After breakfast", "At lunch", "Never"],
                    "correct_index": 1,
                    "explanation": "The script says after breakfast.",
                }
            ],
        )
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Daily routines",
            explanation_brief="Simple present routines.",
            cefr_level="A1",
            sub_level=1,
        )

        content = generated.content
        assert content["phase"] == "live"
        assert content["widget"] == "listen_and_respond"
        assert content["inner_widget"] == "mcq"
        assert content["audio_url"] == "/audio/fake-listening.mp3"
        assert content["audio_duration_seconds"] == 12
        assert fake_tts.calls[0]["text"] == "Mina usually studies English after breakfast."

    @pytest.mark.asyncio
    async def test_malformed_listen_mcq_retries_then_raises(self):
        spec = get_archetype("LISTEN_MCQ")
        invalid = TaskGenOutput(
            topic="Listening for routines",
            instructions="Listen and answer.",
            audio_script="This has no questions.",
            inner_widget="multiple_choice",
            items=[],
        )
        fake = FakeLLMClient([invalid, invalid])
        agent = LLMTaskGenerator(fake)

        with pytest.raises(TaskGenerationFailed) as exc_info:
            await agent.generate(
                archetype=spec,
                day_topic="Daily routines",
                explanation_brief="Simple present routines.",
                cefr_level="A1",
                sub_level=1,
            )
        assert exc_info.value.archetype_id == "LISTEN_MCQ"
        assert len(fake.calls) == 2

    @pytest.mark.asyncio
    async def test_listen_mcq_tts_failure_uses_browser_fallback(self, monkeypatch):
        from app.ai import tts as tts_module

        spec = get_archetype("LISTEN_MCQ")
        monkeypatch.setattr(
            tts_module,
            "get_default_tts_service",
            lambda: FakeTTSService(fail=True),
        )
        fake = FakeLLMClient([
            TaskGenOutput(
                topic="Listening for routines",
                instructions="Listen and answer.",
                audio_script="Mina usually studies English after breakfast.",
                inner_widget="mcq",
                items=[
                    {
                        "item_id": "q1",
                        "prompt": "When does Mina study English?",
                        "options": ["Before bed", "After breakfast", "At lunch", "Never"],
                        "correct_index": 1,
                        "explanation": "The script says after breakfast.",
                    }
                ],
            )
        ])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Daily routines",
            explanation_brief="Simple present routines.",
            cefr_level="A1",
            sub_level=1,
        )

        content = generated.content
        assert content["audio_url"] is None
        assert content["browser_tts_fallback"] is True
        assert content["tts_error"] == "Could not synthesize listening audio for LISTEN_MCQ"
        assert content["audio_duration_seconds"] > 0

    @pytest.mark.asyncio
    async def test_listen_cloze_synthesizes_audio_and_keeps_blank_items(self, monkeypatch):
        from app.ai import tts as tts_module

        spec = get_archetype("LISTEN_CLOZE")
        fake_tts = FakeTTSService()
        monkeypatch.setattr(tts_module, "get_default_tts_service", lambda: fake_tts)
        fake = FakeLLMClient([
            TaskGenOutput(
                topic="Listen and fill past verb forms",
                instructions="Listen and complete the notes.",
                audio_script="Priya got up early and had an interview.",
                inner_widget="fill_in_blanks",
                passage="Priya ___ up early and ___ an interview.",
                items=[
                    {
                        "item_id": "b1",
                        "sentence_with_blank": "Priya ___ up early.",
                        "base_verb": "get",
                        "correct_answer": "got",
                        "grammar_rule": "Use got as the past form of get.",
                        "explanation": "Get becomes got in the past.",
                    },
                    {
                        "item_id": "b2",
                        "sentence_with_blank": "She ___ an interview.",
                        "base_verb": "have",
                        "correct_answer": "had",
                        "grammar_rule": "Use had as the past form of have.",
                        "explanation": "Have becomes had in the past.",
                    },
                ],
            )
        ])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Simple past",
            explanation_brief="Regular and irregular past verbs.",
            cefr_level="A1",
            sub_level=1,
        )

        content = generated.content
        assert content["widget"] == "listen_and_respond"
        assert content["inner_widget"] == "fill_in_blanks"
        assert content["audio_url"] == "/audio/fake-listening.mp3"
        assert content["items"][0]["correct_answer"] == "got"
        assert fake_tts.calls[0]["text"] == "Priya got up early and had an interview."

    @pytest.mark.asyncio
    async def test_authored_listen_cloze_payload_bypasses_llm_and_synthesizes(self, monkeypatch):
        from app.ai import tts as tts_module

        spec = get_archetype("LISTEN_CLOZE")
        fake_tts = FakeTTSService()
        monkeypatch.setattr(tts_module, "get_default_tts_service", lambda: fake_tts)
        fake = FakeLLMClient([])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Simple past",
            explanation_brief="Regular and irregular past verbs.",
            cefr_level="A1",
            sub_level=1,
            task_spec={
                "listen_and_respond": {
                    "instructions": "Listen and fill the blanks.",
                    "audio_script": "She prepared her answers and felt confident.",
                    "inner_widget": "fill_in_blanks",
                    "passage": "She ___ her answers and ___ confident.",
                    "items": [
                        {
                            "item_id": "b1",
                            "sentence_with_blank": "She ___ her answers.",
                            "correct_answer": "prepared",
                            "explanation": "Prepare becomes prepared.",
                        },
                        {
                            "item_id": "b2",
                            "sentence_with_blank": "She ___ confident.",
                            "correct_answer": "felt",
                            "explanation": "Feel becomes felt.",
                        },
                    ],
                }
            },
        )

        content = generated.content
        assert content["phase"] == "authored"
        assert content["inner_widget"] == "fill_in_blanks"
        assert content["audio_url"] == "/audio/fake-listening.mp3"
        assert fake.calls == []

    @pytest.mark.asyncio
    async def test_listen_cloze_evaluator_scores_inner_blank_answers(self):
        spec = get_archetype("LISTEN_CLOZE")
        agent = LLMEvaluator(FakeLLMClient([]))

        result = await agent.evaluate(
            archetype=spec,
            task_content={
                "widget": "listen_and_respond",
                "inner_widget": "fill_in_blanks",
                "items": [
                    {"item_id": "b1", "correct_answer": "got"},
                    {"item_id": "b2", "correct_answer": "had"},
                    {"item_id": "b3", "correct_answer": "prepared"},
                    {"item_id": "b4", "correct_answer": "felt"},
                ],
            },
            user_response={
                "inner_response": {
                    "widget": "fill_in_blanks",
                    "answers": [
                        {"item_id": "b1", "user_answer": "got"},
                        {"item_id": "b2", "user_answer": "has"},
                        {"item_id": "b3", "user_answer": " prepared "},
                    ],
                }
            },
        )

        assert result.raw_score == 5.0
        assert all(score == 5.0 for score in result.rubric_scores.values())
        assert '"missing": 1' in (result.evaluator_notes or "")


# ── compute_wrong_items + confirmed_mistakes pipeline ─────────────


class TestComputeWrongItems:
    """Unit tests for the deterministic blank-checking helper."""

    def _task(self):
        return {
            "items": [
                {"item_id": "b1", "correct_answer": "brush", "explanation": "base verb for I"},
                {"item_id": "b2", "correct_answer": "eats",  "explanation": "she adds -s"},
                {"item_id": "b3", "correct_answer": "walks", "explanation": "he adds -s"},
                {"item_id": "b4", "correct_answer": "drink", "explanation": "they takes base verb"},
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
                {"item_id": "b2", "correct_answer": "had", "explanation": "have -> had"},
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
                {"item_id": "b1", "correct_answer": "brush", "explanation": "base verb for I"},
                {"item_id": "b2", "correct_answer": "eats",  "explanation": "she adds -s"},
                {"item_id": "b3", "correct_answer": "walks", "explanation": "he adds -s"},
                {"item_id": "b4", "correct_answer": "drink", "explanation": "they takes base verb"},
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
        assert marker in prompt.lower(), "Expected 'Confirmed wrong answers' section in prompt"
        # Extract only the confirmed section (everything after the marker).
        confirmed_section = prompt.lower().split(marker, 1)[1]
        # b2 (the wrong answer) must appear in the confirmed section.
        assert '"b2"' in confirmed_section
        # b4 (correct answer "drink" for "they") must NOT appear in the confirmed section.
        assert '"b4"' not in confirmed_section

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
                    {"item_id": "b1", "correct_answer": "got", "explanation": "get -> got"},
                    {"item_id": "b2", "correct_answer": "had", "explanation": "have -> had"},
                ],
            },
        )

        confirmed_section = fake.calls[0]["user_prompt"].lower().split(
            "confirmed wrong answers",
            1,
        )[1]
        assert '"b2"' in confirmed_section
        assert '"b1"' not in confirmed_section

    @pytest.mark.asyncio
    async def test_read_word_match_mcq_feedback_uses_option_labels_not_indices(self):
        """Standalone MCQ widgets (e.g. READ_WORD_MATCH) must show option text."""
        spec = get_archetype("READ_WORD_MATCH")
        fake = FakeLLMClient([
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
        ])
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
        user_response = {"hour": 0, "inner_response": {"widget": "mcq", "answers": [{"item_id": "hour", "selected_index": 0}]}}

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


class TestEveryArchetypeRoundTrips:
    """Every archetype in the registry must produce a valid eval prompt
    without raising. Catches bad rubric or weight_map data."""

    @pytest.mark.parametrize(
        "spec",
        list(ARCHETYPE_REGISTRY.values()),
        ids=lambda s: s.archetype_id,
    )
    def test_eval_prompt_assembles(self, spec):
        from app.ai.sessions.prompts import build_eval_user_prompt

        prompt = build_eval_user_prompt(
            archetype=spec,
            task_content={"topic": "x"},
            user_response={"answer": "y"},
        )
        assert spec.archetype_id in prompt
        assert "rubric criteria" in prompt.lower()


# ── Generator output → schema-boundary projection (Layer 2, Task 2.3) ──────
#
# The seam that drifts: the LLM-side generation schemas (TaskGenOutput,
# FillInBlanksTask, ErrorSpottingTask, ...) and the normalize helpers are loose;
# the wire contracts in contracts/task_payloads.py are strict. These tests run
# the *real* LLMTaskGenerator.generate() path (LLM mock → normalize) and then
# project_task_payload() the result, proving the generated content satisfies its
# contract end to end across the major task families. (The exhaustive
# per-archetype projection coverage lives in test_contract_projection.py; this is
# the integration seam through the production generator.)


def _fill_in_blanks_canned() -> FillInBlanksTask:
    return FillInBlanksTask(
        topic="Simple present routines",
        instructions="Fill each blank with the correct simple present verb.",
        items=[
            {
                "item_id": "b1",
                "sentence_with_blank": "He always ___ to school.",
                "base_verb": "walk",
                "correct_answer": "walks",
                "explanation": "With he, add -s.",
            }
        ],
    )


def _error_correction_canned() -> ErrorCorrectionTask:
    return ErrorCorrectionTask(
        topic="Fix past tense mistakes",
        instructions="Rewrite each sentence correctly.",
        task_intro="Correct the mistakes.",
        items=[
            {
                "item_id": "e1",
                "incorrect_sentence": "She walk to work.",
                "sample_answer": "She walks to work.",
                "watch_hints": ["third person -s"],
            },
            {
                "item_id": "e2",
                "incorrect_sentence": "He go yesterday.",
                "sample_answer": "He went yesterday.",
                "watch_hints": ["irregular past"],
            },
            {
                "item_id": "e3",
                "incorrect_sentence": "They was happy.",
                "sample_answer": "They were happy.",
                "watch_hints": ["were with they"],
            },
        ],
    )


def _mcq_canned() -> TaskGenOutput:
    return TaskGenOutput(
        topic="Reading comprehension",
        instructions="Choose the best answer.",
        primary_text="Maria wakes at seven and drinks coffee.",
        items=[
            {
                "item_id": "q1",
                "prompt": "When does Maria wake up?",
                "options": ["Six", "Seven", "Eight"],
                "correct_index": 1,
                "explanation": "She wakes at seven.",
            }
        ],
    )


def _tfng_canned() -> TaskGenOutput:
    return TaskGenOutput(
        topic="True, false, or not given",
        instructions="Decide true, false, or not given.",
        primary_text="Cats are mammals.",
        items=[
            {
                "item_id": "t1",
                "prompt": "Cats are mammals.",
                "correct_answer": "true",
                "explanation": "Stated directly.",
            }
        ],
    )


_GENERATOR_PROJECTION_CASES = [
    ("READ_CLOZE", _fill_in_blanks_canned),
    ("READ_ERROR_SPOT", lambda: ErrorSpottingTask.model_validate(_error_spotting_content())),
    ("WRITE_ERROR_CORR", _error_correction_canned),
    ("READ_COMP_MCQ", _mcq_canned),
    ("READ_TFNG", _tfng_canned),
]


class TestGeneratorOutputProjectsThroughContract:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "archetype_id,canned_factory",
        _GENERATOR_PROJECTION_CASES,
        ids=[case[0] for case in _GENERATOR_PROJECTION_CASES],
    )
    async def test_generated_content_projects_onto_contract(
        self, archetype_id, canned_factory
    ):
        from app.modules.sessions.contracts import project_task_payload
        from app.modules.sessions.contracts.registry import get_contract

        spec = get_archetype(archetype_id)
        agent = LLMTaskGenerator(FakeLLMClient([canned_factory()]))

        generated = await agent.generate(
            archetype=spec,
            day_topic=spec.name,
            explanation_brief="Cycle-1 practice task.",
            cefr_level="A1",
            sub_level=1,
        )

        # The mock produces valid output, so we stay on the live LLM path.
        assert generated.content["phase"] == "live"

        # The loose generated content projects onto its strict wire contract.
        payload = project_task_payload(
            archetype_id,
            dict(generated.content),
            activity_id="attempt-1",
            sequence=1,
        )
        # Round-trips through the strict contract (which enforces non-empty
        # items/sentences via min_length), proving the generated shape is valid.
        model = get_contract(archetype_id).task_payload.model_validate(payload)
        assert model.archetype_id == archetype_id
        assert model.task_widget == get_contract(archetype_id).task_widget
