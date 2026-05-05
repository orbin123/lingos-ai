"""LLM client exceptions.

These wrap the underlying provider errors (OpenAI, LangChain, network)
so business code can catch ONE family instead of N provider-specific
exception types. Caller decides whether to retry, log, or surface a
clean 502 to the user.
"""


class LLMError(Exception):
    """Base class for any LLM call failure."""


class LLMTimeout(LLMError):
    """Provider took too long. Usually safe to retry."""


class LLMRateLimited(LLMError):
    """Provider rate-limited us. Back off + retry."""


class LLMAuthError(LLMError):
    """Bad / missing API key. NOT retryable — fix config."""


class LLMValidationError(LLMError):
    """LLM returned content that failed Pydantic schema validation.

    Different from a network failure — the provider answered, but the
    answer doesn't match our contract. Usually means the prompt needs
    work. Retry once, then escalate.
    """


class LLMProviderError(LLMError):
    """Catch-all for any other provider-side failure (5xx, malformed
    response, etc). Treated as transient by the retry policy."""
