"""Speech-to-Text client contract — STUB for Phase 3.

Implementation lands in Phase 3 (likely OpenAI Whisper API).

Used by all speak_* task types: storyboard_narration,
retell_what_you_heard, and any future free-form speaking task.
"""

from __future__ import annotations

from typing import Protocol

from typing_extensions import TypedDict


class WordTimestamp(TypedDict):
    """One transcribed word with its time bounds.

    Word-level timestamps power fluency analysis (pauses, speed,
    self-corrections) without a separate model.
    """
    word: str
    start_seconds: float
    end_seconds: float
    confidence: float | None


class TranscriptionResult(TypedDict):
    """Full STT output."""
    text: str
    language: str
    duration_seconds: float
    words: list[WordTimestamp] | None  # None when timestamps weren't requested


class ISTTClient(Protocol):
    """Minimal STT contract."""

    async def transcribe(
        self,
        *,
        audio_bytes: bytes,
        language: str = "en",
    ) -> TranscriptionResult:
        """Plain transcription — no timestamps. Cheaper + faster."""
        ...

    async def transcribe_with_timestamps(
        self,
        *,
        audio_bytes: bytes,
        language: str = "en",
    ) -> TranscriptionResult:
        """Word-level timestamps. Used for fluency / pause analysis."""
        ...
