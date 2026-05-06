"""Pronunciation scoring contract — STUB for Phase 4.

Implementation lands in Phase 4 — likely Azure Speech Pronunciation
Assessment (phoneme-level scoring is its specialty; OpenAI / Whisper
do not expose this).

Used by speak_* task types where we grade HOW the user said something,
not just what they said:
  - read_aloud
  - shadow_audio
  - record_and_compare
  - phoneme_drills
  - intonation_practice

Why a separate interface (vs. piggy-backing on STT)?
- STT answers "what words were spoken?"
- Pronunciation answers "how accurately were those phonemes produced?"
Different services, different cost profiles, different failure modes.
Keeping them separate means a future swap (e.g. Azure → an open-source
phoneme scorer) doesn't ripple through STT code.
"""

from __future__ import annotations

from typing import Protocol

from typing_extensions import TypedDict


class PhonemeScore(TypedDict):
    """One phoneme produced by the user, with its accuracy score.

    Phoneme = the smallest unit of sound in a language. Scoring at this
    level lets us tell the user 'your /θ/ in "think" sounds like /s/'
    instead of just 'word was wrong.'
    """
    phoneme: str          # IPA symbol, e.g. "θ", "iː"
    accuracy_score: float  # 0.0–100.0 (provider-normalised)


class WordScore(TypedDict):
    """One word, its overall accuracy, and per-phoneme breakdown."""
    word: str
    accuracy_score: float          # 0.0–100.0
    error_type: str | None         # "mispronunciation" | "omission" | "insertion" | None
    phonemes: list[PhonemeScore]


class PronunciationResult(TypedDict):
    """Full output of one pronunciation-assessment call."""
    overall_score: float           # 0.0–100.0 — single headline number
    accuracy_score: float          # how close to native phonemes
    fluency_score: float           # pacing, pauses, run-on
    completeness_score: float      # did they say all expected words?
    words: list[WordScore]


class IPronunciationClient(Protocol):
    """Minimal pronunciation-scoring contract."""

    async def score(
        self,
        *,
        audio_bytes: bytes,
        filename: str,
        reference_text: str,
        language: str = "en-US",
    ) -> PronunciationResult:
        """Score user audio against the expected reference text.

        Args:
            audio_bytes: User's recording bytes.
            filename: A name like "recording.wav". The extension matters
                because providers / local decoders use it to determine
                the container or codec.
            reference_text: What the user was supposed to say.
            language: Provider locale (e.g. 'en-US', 'en-GB').

        Returns:
            PronunciationResult with overall + per-word + per-phoneme scores.
        """
        ...
