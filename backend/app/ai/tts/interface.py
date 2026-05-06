"""Text-to-Speech contracts.

Phase 2 ended up with TWO layers, and this file documents both:

1. `ITTSClient`
   The raw provider contract. It returns synthesized audio bytes plus
   metadata like estimated duration. It does NOT know about storage,
   public URLs, or cache-hit flags.

2. `SynthesisResult`
   The high-level service result returned by `CachedTTSService`, after
   the provider output has been persisted and turned into a public URL.

Used by listening tasks: cloze_listening, audio_mcq, dictation,
inference_listening, shadowing_exercise, retell_what_you_heard,
phoneme_awareness, identify_mispronounced, detect_stress_pattern,
detect_speaker_tone, register_mismatch_dialogue, write_answers_from_audio.
"""

from __future__ import annotations

from typing import Protocol

from typing_extensions import TypedDict


class DialogueTurn(TypedDict):
    """One turn in a multi-speaker dialogue.

    Used for tasks that need 2+ voices, e.g. register_mismatch_dialogue
    where speaker A and speaker B alternate.
    """
    speaker: str       # logical speaker id, e.g. "A", "B"
    text: str
    emotion: str | None  # "neutral", "angry", "polite", ... provider-mapped


class SynthesisResult(TypedDict):
    """High-level TTS service result returned to routes/callers."""
    audio_url: str        # public URL or local path served by our app
    duration_seconds: float
    cache_hit: bool       # True if served from our hash-cache


class SynthesizedAudio(TypedDict):
    """Raw provider output before storage/caching concerns are applied."""
    audio_bytes: bytes
    duration_seconds: float


class ITTSClient(Protocol):
    """Minimal provider-side TTS contract.

    Caching is intentionally NOT part of this interface. The cache
    lives one layer up in `CachedTTSService`, which wraps the provider
    plus blob storage.
    """

    @property
    def model_name(self) -> str:
        """Provider model used for synthesis, e.g. `gpt-4o-mini-tts`."""
        ...

    @property
    def default_voice_id(self) -> str:
        """Default voice used when the caller does not override it."""
        ...

    @property
    def response_format(self) -> str:
        """Audio format returned by the provider, e.g. `mp3`."""
        ...

    def estimate_duration_seconds(self, *, audio_bytes: bytes) -> float:
        """Estimate duration for already-synthesized provider audio.

        Used by the cache layer to backfill metadata for older cache
        entries that predate duration sidecars.
        """
        ...

    async def synthesize(
        self,
        *,
        text: str,
        voice_id: str | None = None,
        speed: float = 1.0,
        style_instructions: str | None = None,
    ) -> SynthesizedAudio:
        """Generate raw audio bytes for plain text."""
        ...

    async def synthesize_dialogue(
        self,
        *,
        turns: list[DialogueTurn],
    ) -> SynthesizedAudio:
        """Generate raw bytes for a multi-voice dialogue audio file.

        Each turn gets the provider-appropriate voice + emotion mapping.
        Returns ONE concatenated audio file as raw bytes.
        """
        ...
