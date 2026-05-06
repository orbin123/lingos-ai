"""LLM client package — single entry point for all LLM access in the app.

Public surface (everything else is an implementation detail):

    from app.ai.llm import get_default_llm_client, ILLMClient
    from app.ai.llm import LLMError, LLMValidationError

    client = get_default_llm_client()
    text = await client.generate_text(
        system_prompt="...", user_prompt="..."
    )

For structured (Pydantic-validated) output:

    result = await client.generate_structured(
        system_prompt="...",
        user_prompt="...",
        output_model=MyPydanticModel,
    )
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
]
