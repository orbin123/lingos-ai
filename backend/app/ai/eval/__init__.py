"""LLM-as-judge evaluation (Part B Phase 2).

A separate, stronger model scores the *quality* of our production LLM outputs
(feedback today; mentor notes / task generation later) on 0–10 axes. The judge
reuses the same ``ILLMClient`` contract as the agents so it stays
provider-swappable, runs deterministically (temperature 0.0), and never blocks
the learner — callers fire it post-commit, best-effort.
"""

from app.ai.eval.judge import (
    FeedbackJudge,
    JudgeScores,
    MentorNoteJudge,
    MentorNoteScores,
)

__all__ = [
    "FeedbackJudge",
    "JudgeScores",
    "MentorNoteJudge",
    "MentorNoteScores",
]
