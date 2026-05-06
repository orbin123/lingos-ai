"""Image-generation client exceptions.

Same pattern as the LLM, TTS, STT, and pronunciation exception
families: callers catch ONE base class (`ImageGenError`) instead of
provider-specific SDK errors.
"""


class ImageGenError(Exception):
    """Base class for any image-generation failure."""


class ImageGenTimeout(ImageGenError):
    """Provider took too long. Usually safe to retry."""


class ImageGenRateLimited(ImageGenError):
    """Provider rate-limited us. Back off + retry."""


class ImageGenAuthError(ImageGenError):
    """Bad / missing API key or missing org-level permission."""


class ImageGenProviderError(ImageGenError):
    """Catch-all for provider-side failures (5xx, connection, SDK errors)."""


class ImageGenValidationError(ImageGenError):
    """Caller passed invalid input (empty prompt, bad aspect ratio, etc.)."""
