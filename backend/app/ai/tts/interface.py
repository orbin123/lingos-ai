"""Text-to-Speech client contract — STUB for Phase 2.

This file defines the abstract interface so callers can write code
against `ITTSClient` today, even though no provider is implemented yet.
The first concrete provider (ElevenLabs or OpenAI TTS) lands in Phase 2.

Used by listening tasks: cloze_listening, audio_mcq, dictation,
inference_listening, shadowing_exercise, retell_what_you_heard,
phoneme_awareness, identify_mispronounced, detect_stress_pattern,
detect_speaker_tone, register_mismatch_dialogue, write_answers_from_audio.
"""

from __future__ import annotations

from typing import Protocol, TypedDict


class DialogueTurn(TypedDict):
    """One turn in a multi-speaker dialogue.

    Used for tasks that need 2+ voices, e.g. register_mismatch_dialogue
    where speaker A and speaker B alternate.
    """
    speaker: str       # logical speaker id, e.g. "A", "B"
    text: str
    emotion: str | None  # "neutral", "angry", "polite", ... provider-mapped


class SynthesisResult(TypedDict):
    """What every TTS call returns."""
    audio_url: str        # public URL or local path served by our app
    duration_seconds: float
    cache_hit: bool       # True if served from our hash-cache


class ITTSClient(Protocol):
    """Minimal TTS contract.

    Implementations MUST cache by content hash so the same text never
    re-synthesizes (TTS is one of our biggest cost levers).
    """

    async def synthesize(
        self,
        *,
        text: str,
        voice_id: str | None = None,
        speed: float = 1.0,
    ) -> SynthesisResult:
        """Generate audio for plain text. Returns a hosted audio URL."""
        ...

    async def synthesize_dialogue(
        self,
        *,
        turns: list[DialogueTurn],
    ) -> SynthesisResult:
        """Generate a multi-voice dialogue audio file.

        Each turn gets the provider-appropriate voice + emotion mapping.
        Returns ONE concatenated audio file.
        """
        ...
