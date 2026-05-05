"""LLM client package — single entry point for all LLM access in the app.

Public surface (everything else is an implementation detail):

    from app.ai.llm import get_default_llm_client, ILLMClient
    from app.ai.llm import LLMError, LLMValidationError

    client = get_default_llm_client()
    text = await client.generate_text(
        system_prompt="...", user_prompt="..."
    )

For agents that already use LangChain's `.with_structured_output(...)`
pattern, a backwards-compatible helper exists:

    from app.ai.llm import get_llm   # returns the underlying ChatOpenAI
"""

from app.ai.llm.exceptions import (
    LLMAuthError,
    LLMError,
    LLMProviderError,
    LLMRateLimited,
    LLMTimeout,
    LLMValidationError,
)
from app.ai.llm.interface import ILLMClient
from app.ai.llm.openai_client import (
    OpenAILLMClient,
    get_default_llm_client,
)


# ---------------------------------------------------------------------------
# Backwards-compatibility shim for agents that still call `get_llm()`.
# Returns the underlying ChatOpenAI so `.with_structured_output(...)` and
# `.ainvoke(...)` keep working without touching legacy agent code.
#
# New code should NOT use this — call `get_default_llm_client()` instead.
# ---------------------------------------------------------------------------
def get_llm():
    """DEPRECATED — kept so feedback.py / diagnosis_feedback.py keep working.

    Returns the underlying ChatOpenAI instance from the default client.
    New code should use `get_default_llm_client()` and call
    `.generate_structured(...)` instead.
    """
    return get_default_llm_client().raw_chat_model()


__all__ = [
    # Public client surface
    "ILLMClient",
    "OpenAILLMClient",
    "get_default_llm_client",
    # Errors
    "LLMError",
    "LLMTimeout",
    "LLMRateLimited",
    "LLMAuthError",
    "LLMValidationError",
    "LLMProviderError",
    # Legacy shim
    "get_llm",
]
