"""TTS client exceptions.

Same pattern as the LLM exception family: callers catch ONE base class
(`TTSError`) instead of N provider-specific exception types.
"""


class TTSError(Exception):
    """Base class for any TTS call failure."""


class TTSTimeout(TTSError):
    """Provider took too long. Usually safe to retry."""


class TTSRateLimited(TTSError):
    """Provider rate-limited us. Back off + retry."""


class TTSAuthError(TTSError):
    """Bad / missing API key. NOT retryable — fix config."""


class TTSProviderError(TTSError):
    """Catch-all for any other provider-side failure (5xx, malformed
    response, etc). Treated as transient by the retry policy."""


class TTSValidationError(TTSError):
    """Caller passed invalid input (empty text, unsupported voice).

    Not provider-side — caller bug, never retried.
    """
