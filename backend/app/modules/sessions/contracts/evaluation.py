"""Evaluation-agent output contract.

One strict shape for every archetype's evaluation result, mirroring the
frontend reference ``ActivityEvaluationOutput`` (``evaluation/source.ts``).
Pronunciation archetypes additionally populate ``pronunciation_assessment``.

The ``tier`` reuses the canonical scoring ``Tier`` enum so this contract stays
in lock-step with the scoring engine rather than inventing a parallel scale.
"""

from __future__ import annotations

from pydantic import Field

from app.modules.sessions.contracts.base import StrictModel
from app.scoring.constants import Tier


class PronunciationPhonemeScore(StrictModel):
    phoneme: str
    accuracy_score: float = Field(ge=0, le=100)


class PronunciationWordScore(StrictModel):
    word: str
    accuracy_score: float = Field(ge=0, le=100)
    error_type: str = "none"  # none | mispronunciation | omission | insertion
    phonemes: tuple[PronunciationPhonemeScore, ...] = ()


class PronunciationAssessment(StrictModel):
    overall_score: float = Field(ge=0, le=100)
    accuracy_score: float = Field(ge=0, le=100)
    fluency_score: float = Field(ge=0, le=100)
    completeness_score: float = Field(ge=0, le=100)
    prosody_score: float | None = Field(default=None, ge=0, le=100)
    words: tuple[PronunciationWordScore, ...] = ()


class ActivityEvaluationOutput(StrictModel):
    """Objective scores for one activity. Wording lives in feedback, not here."""

    activity_id: str
    archetype_id: str
    raw_score: float = Field(ge=0, le=10)
    percentage: float = Field(ge=0, le=100)
    tier: Tier
    attended_label: str = ""
    rubric_scores: dict[str, float] = Field(default_factory=dict)
    sub_skill_breakdown: dict[str, float] = Field(default_factory=dict)
    pronunciation_assessment: PronunciationAssessment | None = None
    evaluator_notes: str = ""


class ScorecardActivity(StrictModel):
    activity_id: str
    sequence: int = Field(ge=1)
    archetype_id: str
    label: str
    raw_score: float = Field(ge=0, le=10)
    tier: Tier
    base_reward: int = Field(ge=0)


class OverallScorecard(StrictModel):
    """Final-review aggregate emitted as the ``final_scorecard`` event."""

    day_id: str
    points_applied: bool = False
    activities: tuple[ScorecardActivity, ...] = ()
    points_earned: dict[str, int] = Field(default_factory=dict)
    skill_labels: dict[str, str] = Field(default_factory=dict)


__all__ = [
    "PronunciationPhonemeScore",
    "PronunciationWordScore",
    "PronunciationAssessment",
    "ActivityEvaluationOutput",
    "ScorecardActivity",
    "OverallScorecard",
]
