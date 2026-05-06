"""Text-to-Speech package.

Public surface (what callers should import):

    from app.ai.tts import (
        # High-level service (recommended for almost all callers)
        get_default_tts_service,
        CachedTTSService,
        # Types
        ITTSClient, SynthesisResult, DialogueTurn,
        # Errors
        TTSError, TTSValidationError, TTSAuthError, TTSRateLimited,
    )

    service = get_default_tts_service()
    result = await service.synthesize(text="Hello!", voice="alloy")
    audio_url = result["audio_url"]   # plug into <audio src=...>
"""

from app.ai.tts.cache import (
    CachedTTSService,
    _reset_default_tts_service,
    get_default_tts_service,
)
from app.ai.tts.exceptions import (
    TTSAuthError,
    TTSError,
    TTSProviderError,
    TTSRateLimited,
    TTSTimeout,
    TTSValidationError,
)
from app.ai.tts.interface import (
    DialogueTurn,
    ITTSClient,
    SynthesisResult,
)
from app.ai.tts.openai_client import OpenAITTSClient, get_default_tts_client

__all__ = [
    # High-level service
    "CachedTTSService",
    "get_default_tts_service",
    "_reset_default_tts_service",
    # Low-level provider (rarely needed directly)
    "OpenAITTSClient",
    "get_default_tts_client",
    # Types
    "ITTSClient",
    "SynthesisResult",
    "DialogueTurn",
    # Errors
    "TTSError",
    "TTSTimeout",
    "TTSRateLimited",
    "TTSAuthError",
    "TTSProviderError",
    "TTSValidationError",
]
