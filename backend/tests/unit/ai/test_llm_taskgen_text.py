"""LLMTaskGenerator — text archetypes (WRITE_*/READ_*) + retry handling.

Split out of the former monolithic test_llm_session_agents.py.
"""

from __future__ import annotations


import pytest

from app.ai.llm.exceptions import LLMError
from app.ai.sessions.exceptions import TaskGenerationFailed
from app.ai.sessions.llm_task_generator import (
    ErrorSpottingTask,
    ErrorSpottingTaskLLM,
    ErrorCorrectionTask,
    LLMTaskGenerator,
    TaskGenOutput,
)
from app.modules.sessions.task_generator import (
    is_valid_error_spotting_payload,
    normalize_error_spotting_payload,
)
from app.scoring import get_archetype
from app.tasks.schemas import FillInBlanksTask
from app.tasks.schemas.llm_output_schemas import FillInBlanksTaskLLM

# Canonical fakes (Phase 3 — moved out of this file into tests/mocks/).
from tests.mocks.llm import FakeLLMClient
from tests.unit.ai._llm_agent_support import _error_spotting_content


def _error_spotting_three_categories() -> dict:
    """Valid structure but only 3 distinct error categories (below the
    pedagogical target of 4) — must NOT fail generation/validation."""
    payload = _error_spotting_content()
    # Collapse s4 + s5 onto already-used categories → {irregular_past,
    # missing_past_auxiliary, passive_helper_missing} = 3 distinct.
    payload["passage_sentences"][3]["error"]["error_type"] = "irregular_past"
    payload["passage_sentences"][4]["error"]["error_type"] = "irregular_past"
    return payload


class TestLLMTaskGenerator:
    @pytest.mark.asyncio
    async def test_passes_through_valid_output(self):
        spec = get_archetype("WRITE_EMAIL")
        canned = TaskGenOutput(
            topic="Apology email to your team lead",
            instructions="Write a 4–5 sentence email apologising for missing standup.",
            primary_text="Scenario: You missed today's daily standup. Email your team lead.",
            target_words=["apologise", "standup", "async"],
            items=[
                {
                    "item_id": "email_1",
                    "prompt": "Write the apology email to your team lead.",
                    "sample_answer": (
                        "Hi Alex, I'm sorry I missed standup today. "
                        "I will share my update async."
                    ),
                    "answer_hints": ["Use a polite greeting and apology."],
                }
            ],
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
        assert len(c["items"]) == 1
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
        assert len(fake.calls) == 3  # initial attempt + two retries

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
        assert len(fake.calls) == 3

    def test_error_spotting_strict_schema_accepts_three_categories(self):
        """Regression for the Day 2/Week 1 24w crash: <4 distinct error
        categories is a quality miss, not a hard failure — it must validate."""
        payload = _error_spotting_three_categories()
        distinct = {s["error"]["error_type"] for s in payload["passage_sentences"]}
        assert len(distinct) == 3

        # Previously raised "use at least four distinct past-tense error
        # categories"; now it validates and coerces the derived total.
        model = ErrorSpottingTask.model_validate(payload)
        assert model.total_errors == len(model.passage_sentences)

        # The contract-level "is renderable" check must agree (or the failure
        # just relocates to the heal/regenerate path).
        assert is_valid_error_spotting_payload(
            normalize_error_spotting_payload(payload)
        )

    def test_error_spotting_coerces_total_errors(self):
        payload = _error_spotting_content()
        payload["total_errors"] = 99
        model = ErrorSpottingTask.model_validate(payload)
        assert model.total_errors == 5

    @pytest.mark.asyncio
    async def test_error_spotting_generates_with_three_categories(self):
        """End-to-end generate() must succeed for a 3-category payload."""
        spec = get_archetype("READ_ERROR_SPOT")
        canned = ErrorSpottingTaskLLM.model_validate(_error_spotting_three_categories())
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Spot past tense errors",
            explanation_brief="Past tense error spotting.",
            cefr_level="A1",
            sub_level=1,
        )

        assert generated.content["phase"] == "live"
        assert generated.content["widget"] == "error_spotting"
        assert len(fake.calls) == 1  # no wasted retries on a quality miss

    def test_fill_in_blanks_coerces_total_blanks(self):
        task = FillInBlanksTask(
            topic="Routines",
            instructions="Fill each blank.",
            total_blanks=99,
            items=[
                {
                    "item_id": "b1",
                    "sentence_with_blank": "She ___ early.",
                    "correct_answer": "wakes",
                    "explanation": "third-person -s",
                }
            ],
        )
        assert task.total_blanks == len(task.items) == 1

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
        assert len(fake.calls) == 3

    @pytest.mark.asyncio
    async def test_write_open_sent_preserves_valid_open_text_items(self):
        spec = get_archetype("WRITE_OPEN_SENT")
        canned = TaskGenOutput(
            topic="Write simple present routine sentences",
            instructions=("Write affirmative routine sentences with I, he, and she."),
            grammar_rule_explained=("Use base verbs with I and add -s with he or she."),
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
        assert len(fake.calls) == 3

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
                },
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
        assert len(fake.calls) == 3

    @pytest.mark.asyncio
    async def test_read_comp_mcq_malformed_output_retries_then_raises(self):
        spec = get_archetype("READ_COMP_MCQ")
        invalid = TaskGenOutput(
            topic="Read about daily routines",
            instructions="Answer the questions about the passage.",
            passage="Maria wakes up at seven every morning.",
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
        assert exc_info.value.archetype_id == "READ_COMP_MCQ"
        assert len(fake.calls) == 3
