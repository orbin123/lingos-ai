"""Smoke tests for the offline golden-set harness (Part B Phase 3).

Exercises the importable core (``run_cases`` + reporting) with injected fake
collaborators so it stays hermetic — no LLM, no network, no DB.
"""

from __future__ import annotations

import pytest

from app.ai.eval.judge import JudgeScores
from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.feedback_generator import StubFeedbackGenerator
from scripts.run_evals import (
    FLAG_THRESHOLD,
    axis_means,
    load_golden_set,
    run_cases,
)
from scripts.run_evals import GOLDEN_SET_PATH


class _ScriptedJudge:
    """Returns a low score for the case marked 'bad', a pass otherwise."""

    async def score(self, *, task, user_answer, feedback):
        bad = "BAD" in (task.get("prompt") or "")
        val = 3.0 if bad else 8.0
        return JudgeScores(
            rationale="invented a mistake" if bad else "grounded",
            accuracy=val,
            relevance=val,
            helpfulness=val,
            correctness=val,
        )


@pytest.mark.asyncio
async def test_run_cases_flags_bad_and_passes_good():
    cases = [
        {
            "id": "good_case",
            "archetype_id": "WRITE_PARA",
            "task": "Write about your weekend.",
            "sample_answer": "I went hiking and it was lovely.",
            "ideal_feedback_notes": "praise it",
        },
        {
            "id": "bad_case",
            "archetype_id": "WRITE_PARA",
            "task": "BAD: deliberately bad fixture.",
            "sample_answer": "whatever",
            "ideal_feedback_notes": "should flag",
        },
    ]

    results = await run_cases(
        cases,
        evaluator=StubEvaluator(),
        feedback_gen=StubFeedbackGenerator(),
        judge=_ScriptedJudge(),
    )

    by_id = {r.case_id: r for r in results}
    assert by_id["good_case"].flagged is False
    assert by_id["bad_case"].flagged is True
    # The bad case trips the < 6 flag on every axis.
    assert all(v < FLAG_THRESHOLD for v in by_id["bad_case"].axes.values())

    means = axis_means(results)
    # mean accuracy = (8 + 3) / 2 = 5.5
    assert means["accuracy"] == 5.5


def test_golden_set_loads_and_uses_known_archetypes():
    from app.scoring import get_archetype

    cases = load_golden_set(GOLDEN_SET_PATH)
    assert 15 <= len(cases) <= 25
    for case in cases:
        # Every archetype id must resolve (fails loudly on a typo).
        get_archetype(case["archetype_id"])
        assert case["id"] and case["task"] and case["sample_answer"]
