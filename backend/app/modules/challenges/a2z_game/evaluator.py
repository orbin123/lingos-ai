"""Deterministic word extraction and grading for the A2Z Challenge.

Pure functions — no LLM, no DB, no I/O. Safe to call from anywhere.
"""

from __future__ import annotations

import string


# Characters that STT output may attach to words.
_STRIP_CHARS = string.punctuation  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~


def normalize_token(token: str) -> str:
    """Strip leading/trailing punctuation and lowercase.

    >>> normalize_token("Apple,")
    'apple'
    >>> normalize_token("'hello'")
    'hello'
    """
    return token.strip(_STRIP_CHARS).lower()


def starts_with_letter(word: str, letter: str) -> bool:
    """Case-insensitive check that *word* begins with *letter*.

    Both values are expected to be non-empty strings. *letter* is a
    single A-Z character.
    """
    return bool(word) and word[0].upper() == letter.upper()


def extract_valid_words(
    transcript: str,
    letter: str,
    *,
    min_length: int = 2,
) -> list[str]:
    """Return de-duped words from *transcript* that start with *letter*.

    Processing pipeline:
    1. Split on whitespace.
    2. Normalize each token (strip punctuation, lowercase).
    3. Drop empty / pure-punctuation results.
    4. Drop tokens shorter than *min_length* (avoids "a" false-positives).
    5. Keep only tokens that start with *letter*.
    6. Deduplicate by normalized form, preserving first-seen order.

    Returns the list of normalized, valid words.
    """
    if not transcript or not transcript.strip():
        return []

    seen: set[str] = set()
    result: list[str] = []

    for raw_token in transcript.split():
        normalized = normalize_token(raw_token)
        if not normalized or len(normalized) < min_length:
            continue
        if not starts_with_letter(normalized, letter):
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)

    return result


def grade(
    transcript: str,
    letter: str,
    target_words: int,
) -> dict:
    """Grade a transcript for the A2Z Challenge.

    Returns a dict matching the ``A2ZEvaluationReport`` schema shape::

        {
            "valid_words": ["apple", "anchor", ...],
            "valid_word_count": 3,
            "target_words": 10,
            "passed": False,
        }
    """
    words = extract_valid_words(transcript, letter)
    return {
        "valid_words": words,
        "valid_word_count": len(words),
        "target_words": target_words,
        "passed": len(words) >= target_words,
    }
