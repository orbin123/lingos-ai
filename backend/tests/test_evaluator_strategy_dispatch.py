"""Tests for EvaluationService.score() strategy dispatcher."""

import pytest

from app.ai.agents.evaluator import EvaluationService
from app.tasks.schemas.base import ScoringMethod


SENTINEL = {
    "task_type": "curriculum_grammar_open_text",
    "total": 3,
    "correct_count": 2,
    "percentage": 70.0,
    "subskill_score": 7,
    "main_mistakes": ["test mistake"],
    "questions": {},
}


@pytest.mark.asyncio
async def test_score_dispatches_llm_open_writing(monkeypatch):
    """score() with LLM_OPEN_WRITING calls evaluate_open_text_writing."""
    called_with: dict = {}

    async def fake_evaluate_open_text_writing(
        self, *, task_content, user_answers, user_level, learner_profile, evaluation_focus
    ):
        called_with["task_content"] = task_content
        called_with["user_answers"] = user_answers
        called_with["user_level"] = user_level
        return dict(SENTINEL)

    monkeypatch.setattr(
        EvaluationService,
        "evaluate_open_text_writing",
        fake_evaluate_open_text_writing,
    )

    evaluator = EvaluationService()
    result = await evaluator.score(
        scoring_method=ScoringMethod.LLM_OPEN_WRITING,
        task_content={"items": [{"item_id": "i1", "prompt": "Write"}]},
        user_answers={"i1": "I wrote something."},
        user_level=5,
        learner_profile={"self_assessed_level": "intermediate"},
        evaluation_focus=None,
    )

    assert result == SENTINEL
    assert called_with["task_content"]["items"][0]["item_id"] == "i1"
    assert called_with["user_level"] == 5


@pytest.mark.asyncio
async def test_score_falls_back_to_legacy_evaluate(monkeypatch):
    """score() with an unmigrated scoring_method falls back to evaluate()."""
    legacy_sentinel = {
        "task_type": "fill_in_blanks",
        "total": 2,
        "correct_count": 1,
        "percentage": 50.0,
        "questions": {},
    }

    def fake_evaluate(self, *, activity_type, task_content, user_answers):
        return dict(legacy_sentinel)

    monkeypatch.setattr(EvaluationService, "evaluate", fake_evaluate)

    evaluator = EvaluationService()
    result = await evaluator.score(
        scoring_method=ScoringMethod.RULE_EXACT_MATCH,
        task_content={"blanks": [{"blank_id": "b1", "correct_answer": "went"}]},
        user_answers={"b1": "went"},
        activity_type="fill_in_blanks",
    )

    assert result == legacy_sentinel


@pytest.mark.asyncio
async def test_score_raises_without_activity_type_for_legacy():
    """score() with an unmigrated method and no activity_type raises ValueError."""
    evaluator = EvaluationService()
    with pytest.raises(ValueError, match="score\\(\\) needs activity_type"):
        await evaluator.score(
            scoring_method=ScoringMethod.RULE_EXACT_MATCH,
            task_content={},
            user_answers={},
        )
