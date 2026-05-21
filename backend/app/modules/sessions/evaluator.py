"""Evaluator interface + Phase 3 deterministic stub.

The interface (Protocol) is what `SessionService` depends on. Phase 4 swaps
in a real LLM-driven implementation; tests inject a deterministic stub.

Stay narrow: the evaluator produces objective scores. Feedback wording is a
separate concern (`FeedbackGenerator`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from app.scoring import ArchetypeSpec


@dataclass(frozen=True)
class EvaluationResult:
    """Output of one evaluation. Service layer wraps this into the ORM row."""

    raw_score: float
    rubric_scores: dict[str, float] = field(default_factory=dict)
    evaluator_notes: str | None = None


class Evaluator(Protocol):
    """Score a user's response against an archetype's rubric.

    Async because production implementations call out to an LLM (Phase 4+).
    """

    async def evaluate(
        self,
        *,
        archetype: ArchetypeSpec,
        task_content: dict,
        user_response: dict | None,
        evaluator_overrides: dict | None = None,
    ) -> EvaluationResult: ...


class StubEvaluator:
    """Deterministic evaluator. Used in tests and as offline fallback.

    Returns the configured `default_score` when a response is present; 0.0
    when the response is missing. The production default in
    `SessionService` is the LLM-driven evaluator from `app.ai.sessions`.

    Tests inject a different `default_score` to exercise tier boundaries.
    """

    def __init__(self, default_score: float = 7.0) -> None:
        if not (0.0 <= default_score <= 10.0):
            raise ValueError(f"default_score must be 0..10, got {default_score}")
        self.default_score = float(default_score)

    async def evaluate(
        self,
        *,
        archetype: ArchetypeSpec,
        task_content: dict,
        user_response: dict | None,
        evaluator_overrides: dict | None = None,
    ) -> EvaluationResult:
        if user_response is None:
            return EvaluationResult(
                raw_score=0.0,
                rubric_scores={r: 0.0 for r in archetype.rubric},
                evaluator_notes="No response submitted.",
            )
        return EvaluationResult(
            raw_score=self.default_score,
            rubric_scores={r: self.default_score for r in archetype.rubric},
            evaluator_notes=(
                "Stub evaluator — returns a constant score. "
                "Production uses the LLM-driven evaluator in app.ai.sessions."
            ),
        )
