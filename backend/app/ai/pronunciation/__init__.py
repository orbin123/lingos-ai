"""Pronunciation scoring package.

Public surface (what callers should import):

    from app.ai.pronunciation import (
        get_default_pronunciation_service,
        CachedPronunciationService,
        IPronunciationClient,
        PronunciationResult,
        PronunciationError,
        PronunciationValidationError,
    )
"""

from app.ai.pronunciation.cache import (
    CachedPronunciationService,
    _reset_default_pronunciation_service,
    get_default_pronunciation_service,
)
from app.ai.pronunciation.azure_client import (
    AzurePronunciationClient,
    _reset_default_pronunciation_client,
    get_default_pronunciation_client,
)
from app.ai.pronunciation.exceptions import (
    PronunciationAuthError,
    PronunciationDependencyError,
    PronunciationError,
    PronunciationProviderError,
    PronunciationRateLimited,
    PronunciationTimeout,
    PronunciationUnsupportedFormat,
    PronunciationValidationError,
)
from app.ai.pronunciation.interface import (
    IPronunciationClient,
    PhonemeScore,
    PronunciationResult,
    WordScore,
)

__all__ = [
    "CachedPronunciationService",
    "get_default_pronunciation_service",
    "_reset_default_pronunciation_service",
    "AzurePronunciationClient",
    "get_default_pronunciation_client",
    "_reset_default_pronunciation_client",
    "IPronunciationClient",
    "PronunciationResult",
    "WordScore",
    "PhonemeScore",
    "PronunciationError",
    "PronunciationTimeout",
    "PronunciationRateLimited",
    "PronunciationAuthError",
    "PronunciationDependencyError",
    "PronunciationProviderError",
    "PronunciationValidationError",
    "PronunciationUnsupportedFormat",
]
