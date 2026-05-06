"""Pronunciation scoring package — STUB for Phase 4.

Only the abstract interface lives here today. Concrete provider
(Azure Speech for phoneme-level scoring) will be added in Phase 4.
"""

from app.ai.pronunciation.interface import (
    IPronunciationClient,
    PhonemeScore,
    PronunciationResult,
    WordScore,
)

__all__ = [
    "IPronunciationClient",
    "PronunciationResult",
    "WordScore",
    "PhonemeScore",
]
