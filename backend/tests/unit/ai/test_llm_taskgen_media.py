"""LLMTaskGenerator — media archetypes (SPEAK_*/LISTEN_*) with TTS/image.

Split out of the former monolithic test_llm_session_agents.py.
"""

from __future__ import annotations


import pytest

from app.ai.sessions.llm_evaluator import LLMEvaluator
from app.ai.sessions.exceptions import TaskGenerationFailed
from app.ai.sessions.llm_task_generator import (
    LLMTaskGenerator,
    TaskGenOutput,
)
from app.scoring import get_archetype

# Canonical fakes (Phase 3 — moved out of this file into tests/mocks/).
from tests.mocks.imagegen import FakeImageGenService
from tests.mocks.llm import FakeLLMClient
from tests.mocks.tts import FakeTTSService
from tests.unit.ai._llm_agent_support import _dictation_canned


class TestLLMTaskGenerator:
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
            speaking_duration_seconds=1,
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
        assert len(fake.calls) == 3

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
    async def test_listen_dictation_normalizes_and_synthesizes_audio(self, monkeypatch):
        from app.ai import tts as tts_module

        spec = get_archetype("LISTEN_DICTATION")
        fake_tts = FakeTTSService()
        monkeypatch.setattr(tts_module, "get_default_tts_service", lambda: fake_tts)
        canned = _dictation_canned()
        fake = FakeLLMClient([canned])
        agent = LLMTaskGenerator(fake)

        generated = await agent.generate(
            archetype=spec,
            day_topic="Daily routines",
            explanation_brief="Present simple dictation.",
            cefr_level="A1",
            sub_level=1,
        )

        content = generated.content
        assert content["phase"] == "live"
        assert content["widget"] == "listen_and_respond"
        assert content["inner_widget"] == "open_text"
        assert len(content["items"]) == 3
        assert content["items"][0]["correct_answer"] == "Maria wakes up at seven."
        assert content["audio_url"] == "/audio/fake-listening.mp3"

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
        assert len(fake.calls) == 3

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


