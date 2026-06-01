"""Deterministic evaluators + reference data for the diagnosis mini-tasks.

What lives here now:
  - ``RuleBasedEvaluator``  — grades the fill-in-the-blank task against a
    canonical answer key (no LLM, no I/O).
  - ``PASSAGES``            — canonical read-aloud reference texts, keyed by
    passage_id. Used as the Azure pronunciation ``reference_text`` and shown
    to the learner on the frontend.

Writing is now scored by an LLM (``diagnosis_agents.writing_evaluator``) and
read-aloud by Azure Speech Pronunciation Assessment (the frontend posts audio
to ``POST /diagnosis/pronunciation-score`` and submits the result), so the old
``TextEvaluator``/``SpeechEvaluator`` stubs were removed.
"""


# ── Rule-based evaluator (fill-blank) ─────────────────────────────────────

FILL_BLANK_ANSWERS_V1: list[str] = [
    "goes",
    "ate",
    "rains",
    "lived",
    "was written",
]


class RuleBasedEvaluator:
    """Compares user fill-blank answers against the canonical answer key."""

    def evaluate_fill_blank(
        self, *, question_set_id: str, user_answers: list[str]
    ) -> int:
        """Return the count of correct answers (0..5)."""
        if question_set_id != "diag_fillblank_v1":
            raise ValueError(f"Unknown question_set_id: {question_set_id}")

        if len(user_answers) != len(FILL_BLANK_ANSWERS_V1):
            raise ValueError(
                f"Expected {len(FILL_BLANK_ANSWERS_V1)} answers, "
                f"got {len(user_answers)}"
            )

        correct = 0
        for given, expected in zip(user_answers, FILL_BLANK_ANSWERS_V1):
            if given.strip().lower() == expected.strip().lower():
                correct += 1
        return correct


# ── Read-aloud reference passages ─────────────────────────────────────────

# The canonical passages, keyed by passage_id. Must match what the frontend
# shows the user, and is used as the Azure pronunciation reference text.
PASSAGES: dict[str, str] = {
    "diag_passage_v1": (
        "Every morning I wake up early and walk in the park. "
        "The fresh air helps me think clearly. "
        "I greet a few neighbours, finish a short jog, "
        "and return home feeling ready for the day."
    ),
}
