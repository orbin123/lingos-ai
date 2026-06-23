"""LLMFeedbackGenerator: output parsing, mistake capping, false-positive filtering.

Split out of the former monolithic test_llm_session_agents.py.
"""

from __future__ import annotations


import pytest

from app.ai.llm.exceptions import LLMError
from app.ai.sessions.llm_feedback import (
    FeedbackOutput,
    LLMFeedbackGenerator,
    MistakeOutSchema,
)
from app.scoring import get_archetype

# Canonical fakes (Phase 3 — moved out of this file into tests/mocks/).
from tests.mocks.llm import FakeLLMClient
from tests.unit.ai._llm_agent_support import _error_spotting_content


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
            archetype=spec,
            evaluation=self._eval(),
            user_response={"x": "y"},
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
    async def test_error_correction_feedback_lists_only_real_mistakes(self):
        """Regression for the '3 vs 2' bug (tasks_eval_feedback_distorted.png).

        error_correction has a per-item answer key, so feedback must cite EXACTLY
        the deterministically-wrong items even when the LLM invents an extra one.
        """
        spec = get_archetype("WRITE_ERROR_CORR")
        # The LLM hallucinates THREE mistakes (including one about the item the
        # learner actually fixed); only two items were truly wrong.
        canned = FeedbackOutput(
            score=4,
            summary="A couple of tense slips.",
            mistakes=[
                MistakeOutSchema(
                    issue="Invented problem",
                    user_wrote="He went home yesterday.",
                    correction="He goes home yesterday.",
                    rule="hallucinated",
                ),
                MistakeOutSchema(issue="x", user_wrote="aaa", correction="bbb"),
                MistakeOutSchema(issue="y", user_wrote="ccc", correction="ddd"),
            ],
            sub_skill_breakdown={skill: 4 for skill in spec.weight_map},
        )
        fake = FakeLLMClient([canned])
        agent = LLMFeedbackGenerator(fake)

        task_content = {
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
        user_response = {
            "e1": "She walk to work.",  # wrong (unchanged)
            "e2": "They was happy.",  # wrong (unchanged)
            "e3": "He went home yesterday.",  # correct
        }

        fb = await agent.generate(
            archetype=spec,
            evaluation=self._eval(),
            user_response=user_response,
            task_content=task_content,
        )

        # EXACTLY the two real misses — the invented third is gone.
        assert len(fb.mistakes) == 2
        assert [m.user_wrote for m in fb.mistakes] == [
            "She walk to work.",
            "They was happy.",
        ]
        assert (
            fb.mistakes[0].issue
            == '"She walk to work." should be "She walked to work.".'
        )
        assert fb.mistakes[1].correction == "They were happy."
        # The LLM's fabricated mistake about the correctly-fixed item is dropped.
        assert all("goes home" not in (m.correction or "") for m in fb.mistakes)

    @pytest.mark.asyncio
    async def test_error_correction_all_correct_shows_no_mistakes(self):
        """When every item is fixed, feedback shows zero mistakes even if the
        LLM tries to invent some."""
        spec = get_archetype("WRITE_ERROR_CORR")
        canned = FeedbackOutput(
            score=10,
            summary="All corrected.",
            mistakes=[
                MistakeOutSchema(issue="phantom", user_wrote="x", correction="y"),
            ],
            sub_skill_breakdown={skill: 10 for skill in spec.weight_map},
        )
        fake = FakeLLMClient([canned])
        agent = LLMFeedbackGenerator(fake)

        task_content = {
            "widget": "error_correction",
            "items": [
                {
                    "item_id": "e1",
                    "incorrect_sentence": "She walk to work.",
                    "sample_answer": "She walked to work.",
                    "watch_hints": ["tense"],
                },
            ],
        }
        fb = await agent.generate(
            archetype=spec,
            evaluation=self._eval(),
            user_response={"e1": "She walked to work."},
            task_content=task_content,
        )
        assert fb.mistakes == ()

    @pytest.mark.asyncio
    async def test_no_response_short_circuits(self):
        spec = get_archetype("READ_COMP_MCQ")
        fake = FakeLLMClient([])
        agent = LLMFeedbackGenerator(fake)

        fb = await agent.generate(
            archetype=spec,
            evaluation=self._eval(),
            user_response=None,
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
            archetype=spec,
            evaluation=self._eval(),
            user_response={"x": "y"},
        )
        # The fallback still uses the evaluation's rounded score.
        assert fb.score == 7
        assert "unavailable" in fb.summary.lower()
        assert set(fb.sub_skill_breakdown) == set(spec.weight_map)


# ── LLMTaskGenerator ───────────────────────────────────────────────
