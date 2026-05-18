"""Tests for the LLM-driven sessions agents.

A `FakeLLMClient` returns canned Pydantic instances so we exercise the
agent wiring (prompt assembly, fallback handling, output validation)
without ever hitting OpenAI. Phase 4 wires these agents into production
routes; these tests lock the contracts the routes depend on.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest
from pydantic import BaseModel

from app.ai.llm.exceptions import LLMError, LLMProviderError
from app.ai.sessions.llm_evaluator import EvaluationOutput, LLMEvaluator
from app.ai.sessions.llm_feedback import FeedbackOutput, LLMFeedbackGenerator, MistakeOutSchema
from app.ai.sessions.llm_task_generator import LLMTaskGenerator, TaskGenOutput
from app.scoring import ARCHETYPE_REGISTRY, get_archetype


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
                MistakeOutSchema(issue=f"issue {i}")
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
    async def test_llm_failure_falls_back_to_stub_content(self):
        spec = get_archetype("WRITE_EMAIL")
        fake = FakeLLMClient([LLMError("provider down")])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Email writing",
            explanation_brief="brief",
            cefr_level="A2",
            sub_level=3,
        )
        # Fallback uses StubTaskGenerator → phase becomes "stub".
        assert generated.content["phase"] == "stub"
        assert generated.content["archetype_id"] == "WRITE_EMAIL"


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
