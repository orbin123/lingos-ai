"""Pronunciation client exceptions.

Same pattern as the LLM, TTS, and STT exception families: callers catch
ONE base class (`PronunciationError`) instead of provider-specific SDK
errors, cancellation codes, and local dependency issues.
"""


class PronunciationError(Exception):
    """Base class for any pronunciation-scoring failure."""


class PronunciationTimeout(PronunciationError):
    """Provider took too long. Usually safe to retry."""


class PronunciationRateLimited(PronunciationError):
    """Provider rate-limited us. Back off + retry."""


class PronunciationAuthError(PronunciationError):
    """Bad / missing Azure Speech credentials. NOT retryable."""


class PronunciationProviderError(PronunciationError):
    """Catch-all for provider-side failures (5xx, connection, SDK errors)."""


class PronunciationDependencyError(PronunciationProviderError):
    """Required local dependency (Azure SDK, decoder support) is missing."""


class PronunciationValidationError(PronunciationError):
    """Caller passed invalid input (empty audio, bad filename, silence)."""


class PronunciationUnsupportedFormat(PronunciationValidationError):
    """The uploaded audio format is unsupported by this integration."""
