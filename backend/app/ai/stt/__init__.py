"""Speech-to-Text package.

Public surface (what callers should import):

    from app.ai.stt import (
        # High-level service (recommended for almost all callers)
        get_default_stt_service,
        CachedSTTService,
        # Types
        ISTTClient, TranscriptionResult, WordTimestamp,
        # Errors
        STTError, STTValidationError, STTPayloadTooLarge,
        STTAuthError, STTRateLimited,
    )

    service = get_default_stt_service()
    result = await service.transcribe(
        audio_bytes=raw_bytes,
        filename="recording.webm",
        with_timestamps=False,
    )
    text = result["text"]
"""

from app.ai.stt.cache import (
    CachedSTTService,
    _reset_default_stt_service,
    get_default_stt_service,
)
from app.ai.stt.exceptions import (
    STTAuthError,
    STTError,
    STTPayloadTooLarge,
    STTProviderError,
    STTRateLimited,
    STTTimeout,
    STTValidationError,
)
from app.ai.stt.interface import (
    ISTTClient,
    TranscriptionResult,
    WordTimestamp,
)
from app.ai.stt.openai_client import (
    OpenAISTTClient,
    _reset_default_stt_client,
    get_default_stt_client,
)

__all__ = [
    # High-level service
    "CachedSTTService",
    "get_default_stt_service",
    "_reset_default_stt_service",
    # Low-level provider (rarely needed directly)
    "OpenAISTTClient",
    "get_default_stt_client",
    "_reset_default_stt_client",
    # Types
    "ISTTClient",
    "TranscriptionResult",
    "WordTimestamp",
    # Errors
    "STTError",
    "STTTimeout",
    "STTRateLimited",
    "STTAuthError",
    "STTProviderError",
    "STTValidationError",
    "STTPayloadTooLarge",
]
