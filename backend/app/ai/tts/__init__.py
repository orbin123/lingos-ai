"""Text-to-Speech package — STUB for Phase 2.

Only the abstract interface lives here today. Concrete provider
(ElevenLabs / OpenAI TTS) will be added in Phase 2.
"""

from app.ai.tts.interface import (
    DialogueTurn,
    ITTSClient,
    SynthesisResult,
)

__all__ = ["ITTSClient", "DialogueTurn", "SynthesisResult"]
