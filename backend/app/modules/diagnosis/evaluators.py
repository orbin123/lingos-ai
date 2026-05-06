"""Evaluators for the diagnosis mini-tasks.

Each evaluator has ONE responsibility: turn a raw user submission
into normalized scores. They know nothing about the database, the
formula, or each other.

TextEvaluator is still a stub — real LLM integration is a future ticket.
SpeechEvaluator is now REAL — it scores against a Whisper transcript.
"""

from difflib import SequenceMatcher
import re

from app.modules.diagnosis.schemas import (
    ReadAloudAnalysisOut,
    ReadAloudMismatchOut,
    ReadAloudWordTiming,
)


# ── 1. Rule-based evaluator (fill-blank) ──────────────────────────────────

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


# ── 2. Text evaluator (STUB — replaced by LLM later) ──────────────────────

class TextEvaluator:
    """Evaluates the writing response across 3 dimensions.

    STUB: Returns scores based on word count only.
    Real implementation will call an LLM with a structured rubric prompt.
    """

    def evaluate_writing(
        self, *, prompt_id: str, response_text: str
    ) -> dict[str, float]:
        """Return expression_score, vocabulary_score, tone_score."""
        word_count = len(response_text.split())
        length_factor = min(word_count / 60, 1.0)

        return {
            "expression_score": round(0.3 + 0.4 * length_factor, 2),
            "vocabulary_score": round(0.15 + 0.2 * length_factor, 2),
            "tone_score": round(0.15 + 0.2 * length_factor, 2),
        }


# ── 3. Speech evaluator (REAL — Whisper transcript scoring) ───────────────

# The canonical passages, keyed by passage_id.
# Must match what the frontend shows the user.
PASSAGES: dict[str, str] = {
    "diag_passage_v1": (
        "Every morning I wake up early and walk in the park. "
        "The fresh air helps me think clearly. "
        "I greet a few neighbours, finish a short jog, "
        "and return home feeling ready for the day."
    ),
}

# Ideal reading speed range for a clear, measured read (words per minute)
WPM_MIN = 100
WPM_MAX = 160
_MEANINGFUL_PAUSE_S = 0.25
_LONG_PAUSE_S = 0.80
_MAX_MISMATCHES = 24


def _tokenize(text: str) -> list[str]:
    """Lowercase and split into word tokens, stripping punctuation.

    Example: "I'm fine." → ["i'm", "fine"]
    We keep contractions intact because Whisper preserves them.
    """
    return re.findall(r"[a-z']+", text.lower())


def _accuracy_pct(reference_words: list[str], transcript_words: list[str]) -> float:
    """Word-level accuracy: fraction of reference words present in transcript.

    Uses a sliding-window match so small insertions/deletions don't kill
    the entire score. Returns 0.0 – 1.0.

    Algorithm:
      For each reference word, check if it appears in the transcript within
      a window of ±5 positions around the expected position. This tolerates
      skipped words and minor disfluencies without being too generous.
    """
    if not reference_words:
        return 0.0

    n_ref = len(reference_words)
    n_tra = len(transcript_words)
    matched = 0

    for i, ref_word in enumerate(reference_words):
        # Expected position in transcript scaled by length ratio
        expected_pos = int(i * (n_tra / n_ref)) if n_tra else 0
        window_start = max(0, expected_pos - 5)
        window_end = min(n_tra, expected_pos + 6)
        window = transcript_words[window_start:window_end]
        if ref_word in window:
            matched += 1

    return matched / n_ref


def _similarity_ratio(reference_words: list[str], transcript_words: list[str]) -> float:
    """Token-sequence similarity on 0.0–1.0."""
    if not reference_words and not transcript_words:
        return 0.0
    return SequenceMatcher(a=reference_words, b=transcript_words).ratio()


def _score_wpm(word_count: int, duration_seconds: float) -> tuple[float, float]:
    """Return (wpm, score) for a read-aloud clip."""
    safe_duration = max(duration_seconds, 1.0)
    wpm = (word_count / safe_duration) * 60

    if WPM_MIN <= wpm <= WPM_MAX:
        score = 1.0
    elif wpm < WPM_MIN:
        # Too slow — linear scale from 0.3 (at 0 WPM) to 1.0 (at WPM_MIN)
        score = round(0.3 + 0.7 * (wpm / WPM_MIN), 2)
    else:
        # Too fast — linear penalty above WPM_MAX, floor at 0.5
        over = wpm - WPM_MAX
        score = round(max(0.5, 1.0 - (over / WPM_MAX) * 0.5), 2)

    return round(wpm, 2), min(score, 1.0)


def _pause_stats(
    words: list[ReadAloudWordTiming],
) -> tuple[int, int, float, float, float]:
    """Return pause metrics + a smoothness score on 0.0–1.0."""
    if len(words) < 2:
        return 0, 0, 0.0, 0.0, 1.0

    pauses: list[float] = []
    for previous, current in zip(words, words[1:]):
        gap = max(0.0, current.start_seconds - previous.end_seconds)
        if gap >= _MEANINGFUL_PAUSE_S:
            pauses.append(gap)

    if not pauses:
        return 0, 0, 0.0, 0.0, 1.0

    pause_count = len(pauses)
    long_pause_count = sum(gap >= _LONG_PAUSE_S for gap in pauses)
    longest_pause = max(pauses)
    average_pause = sum(pauses) / pause_count

    penalty = 0.0
    penalty += min(long_pause_count * 0.12, 0.36)
    penalty += min(max(0.0, average_pause - 0.35) * 0.45, 0.18)
    penalty += min(max(0.0, longest_pause - 1.2) * 0.18, 0.16)
    smoothness_score = max(0.3, 1.0 - penalty)

    return (
        pause_count,
        long_pause_count,
        round(longest_pause, 2),
        round(average_pause, 2),
        round(smoothness_score, 2),
    )


def _word_mismatches(
    reference_words: list[str],
    transcript_words: list[str],
) -> tuple[list[ReadAloudMismatchOut], int]:
    """Return per-word-ish mismatches derived from token alignment."""
    mismatches: list[ReadAloudMismatchOut] = []
    mismatch_count = 0
    matcher = SequenceMatcher(a=reference_words, b=transcript_words)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        span = max(i2 - i1, j2 - j1)
        for offset in range(span):
            ref_index = i1 + offset if i1 + offset < i2 else None
            transcript_index = j1 + offset if j1 + offset < j2 else None

            reference_word = (
                reference_words[ref_index] if ref_index is not None else None
            )
            transcript_word = (
                transcript_words[transcript_index]
                if transcript_index is not None
                else None
            )

            if reference_word is not None and transcript_word is not None:
                issue = "substitution"
            elif reference_word is not None:
                issue = "omission"
            else:
                issue = "insertion"

            mismatch_count += 1

            if len(mismatches) < _MAX_MISMATCHES:
                mismatches.append(
                    ReadAloudMismatchOut(
                        issue=issue,
                        reference_word=reference_word,
                        transcript_word=transcript_word,
                        reference_index=ref_index,
                        transcript_index=transcript_index,
                    )
                )

    return mismatches, mismatch_count


class SpeechEvaluator:
    """Scores a read-aloud submission using a Whisper transcript.

    Inputs  : passage_id, transcript (from Whisper), duration_seconds,
              optional word timestamps
    Outputs : Whisper-only MVP analysis including:
              - fluency_score (0.0–1.0)
              - clarity_score (0.0–1.0)
              - transcript_similarity (0.0–1.0)
              - pause stats + word-level mismatches

    fluency_score  — based on reading speed (WPM) and, when available,
                     pause smoothness from Whisper word timestamps.
    clarity_score  — based on token accuracy + sequence similarity vs
                     the reference passage.

    If the passage_id is unknown or the transcript is empty, both scores
    fall back to 0.4 (below average but not zero — avoids punishing
    technical failures too harshly).
    """

    FALLBACK_SCORE = 0.4

    def evaluate_read_aloud(
        self,
        *,
        passage_id: str,
        transcript: str,
        duration_seconds: float,
        words: list[ReadAloudWordTiming] | None = None,
    ) -> ReadAloudAnalysisOut:
        """Return Whisper-based fluency, clarity, and mismatch details."""

        reference_text = PASSAGES.get(passage_id)
        if not reference_text or not transcript.strip():
            return ReadAloudAnalysisOut(
                fluency_score=self.FALLBACK_SCORE,
                clarity_score=self.FALLBACK_SCORE,
                transcript_similarity=0.0,
                word_accuracy=0.0,
                words_per_minute=0.0,
                pause_count=0,
                long_pause_count=0,
                longest_pause_seconds=0.0,
                average_pause_seconds=0.0,
                mismatch_count=0,
                mismatches=[],
            )

        reference_words = _tokenize(reference_text)
        transcript_words = _tokenize(transcript)
        timing_words = words or []

        # ── Clarity: lexical alignment + sequence similarity ──────────────
        accuracy = _accuracy_pct(reference_words, transcript_words)
        similarity = _similarity_ratio(reference_words, transcript_words)
        mismatches, mismatch_count = _word_mismatches(
            reference_words, transcript_words
        )
        clarity_score = round((accuracy * 0.65) + (similarity * 0.35), 2)

        # ── Fluency: reading speed + pause smoothness ─────────────────────
        spoken_word_count = len(timing_words) or len(transcript_words)
        wpm, wpm_score = _score_wpm(spoken_word_count, duration_seconds)
        (
            pause_count,
            long_pause_count,
            longest_pause,
            average_pause,
            pause_score,
        ) = _pause_stats(timing_words)

        if timing_words:
            fluency_score = round((wpm_score * 0.7) + (pause_score * 0.3), 2)
        else:
            fluency_score = round(wpm_score, 2)

        return ReadAloudAnalysisOut(
            fluency_score=min(fluency_score, 1.0),
            clarity_score=min(clarity_score, 1.0),
            transcript_similarity=round(similarity, 2),
            word_accuracy=round(accuracy, 2),
            words_per_minute=wpm,
            pause_count=pause_count,
            long_pause_count=long_pause_count,
            longest_pause_seconds=longest_pause,
            average_pause_seconds=average_pause,
            mismatch_count=mismatch_count,
            mismatches=mismatches,
        )
