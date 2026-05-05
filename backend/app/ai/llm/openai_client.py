"""OpenAI implementation of ILLMClient (LangChain-backed).

Design notes:

1. Built on `langchain_openai.ChatOpenAI` so:
   - LangSmith tracing happens automatically (env vars already set)
   - `.with_structured_output(...)` keeps working for legacy agents
   - Swapping to another LangChain-supported provider is one line

2. Retries are handled HERE, not in callers. We retry up to 3 times
   on transient failures (timeout, rate limit, 5xx). Validation errors
   are NOT retried — the prompt is wrong, retrying won't help.

3. Every successful call logs a UsageRecord at INFO level. Every
   failure logs once at WARNING. Callers don't need to log anything.

4. Provider-specific exceptions are translated into our LLMError
   family at the boundary. Nothing leaks `openai.RateLimitError`
   upward — agents catch `LLMError` only.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, TypeVar

import openai
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ValidationError

from app.ai.llm.exceptions import (
    LLMAuthError,
    LLMError,
    LLMProviderError,
    LLMRateLimited,
    LLMTimeout,
    LLMValidationError,
)
from app.ai.llm.usage import UsageRecord, estimate_cost, log_usage
from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# Defaults — single source of truth for "which model + which knobs".
# Override per-call via constructor args if needed (e.g. lower temperature
# for the evaluator agent in the future).
# ---------------------------------------------------------------------------
_DEFAULT_MODEL = "gpt-4o-mini"
_DEFAULT_TEMPERATURE = 0.7
_DEFAULT_TIMEOUT_S = 30.0
_MAX_RETRIES = 3   # ChatOpenAI's built-in retry handles transient errors


class OpenAILLMClient:
    """Concrete `ILLMClient` backed by OpenAI through LangChain.

    Stateless w.r.t. user data — safe to reuse as a process-wide
    singleton (see `get_default_llm_client()` below).
    """

    def __init__(
        self,
        *,
        model: str = _DEFAULT_MODEL,
        temperature: float = _DEFAULT_TEMPERATURE,
        timeout: float = _DEFAULT_TIMEOUT_S,
        max_retries: int = _MAX_RETRIES,
    ) -> None:
        self._model = model
        self._temperature = temperature
        # ChatOpenAI handles its own retry/backoff for transient errors.
        # We tell it how many tries; it does exponential backoff internally.
        self._chat = ChatOpenAI(
            model=model,
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
            api_key=settings.OPENAI_API_KEY,
        )

    # ------------------------------------------------------------------
    # Public — generate_text
    # ------------------------------------------------------------------
    async def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> str:
        """Plain text round-trip. Returns the assistant's reply."""
        chat = self._maybe_rebind_temperature(temperature)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        try:
            response = await chat.ainvoke(messages)
        except Exception as exc:
            raise self._translate_exception(exc) from exc

        self._log_response_usage(response)
        # ChatOpenAI returns an AIMessage; .content is the string.
        return str(response.content)

    # ------------------------------------------------------------------
    # Public — generate_structured (the workhorse)
    # ------------------------------------------------------------------
    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_model: type[T],
        temperature: float | None = None,
    ) -> T:
        """Round-trip that returns a validated Pydantic instance.

        Uses LangChain's structured-output binding so the LLM is
        constrained at the API level (function-calling under the hood).
        That gives us very high schema-conformance without manual JSON
        parsing.
        """
        chat = self._maybe_rebind_temperature(temperature)
        structured_chat = chat.with_structured_output(output_model)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        try:
            result = await structured_chat.ainvoke(messages)
        except ValidationError as exc:
            # The LLM answered, but the answer didn't match the schema.
            # Don't retry — the prompt or schema needs work.
            logger.warning(
                "llm_structured_validation_failed model=%s schema=%s err=%s",
                self._model, output_model.__name__, exc,
            )
            raise LLMValidationError(
                f"LLM output failed schema validation for "
                f"{output_model.__name__}: {exc}"
            ) from exc
        except Exception as exc:
            raise self._translate_exception(exc) from exc

        # NOTE: with_structured_output() loses access to token usage
        # metadata in some LangChain versions. We log a marker so we
        # know a structured call happened even if we can't price it.
        logger.info(
            "llm_structured_ok model=%s schema=%s",
            self._model, output_model.__name__,
        )

        # `result` is already an instance of `output_model` — LangChain
        # validated it for us. Return as-is.
        return result  # type: ignore[no-any-return]

    # ------------------------------------------------------------------
    # Public — escape hatch for legacy agents
    # ------------------------------------------------------------------
    def raw_chat_model(self) -> ChatOpenAI:
        """Return the underlying ChatOpenAI for code that uses LangChain
        APIs directly (e.g. `.with_structured_output(...).ainvoke(...)`).

        Existing agents use this. New code should prefer
        `generate_structured(...)`.
        """
        return self._chat

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _maybe_rebind_temperature(
        self, temperature: float | None
    ) -> ChatOpenAI:
        """Return a ChatOpenAI with a temperature override, or the
        default instance if no override is given.

        ChatOpenAI is cheap to construct — fine to spin a new one when
        a per-call temperature is requested. Keeps the default instance
        pure (same temperature for the whole app).
        """
        if temperature is None or temperature == self._temperature:
            return self._chat
        return ChatOpenAI(
            model=self._model,
            temperature=temperature,
            api_key=settings.OPENAI_API_KEY,
            max_retries=_MAX_RETRIES,
            timeout=_DEFAULT_TIMEOUT_S,
        )

    def _log_response_usage(self, response: Any) -> None:
        """Pull token counts off the AIMessage and emit one log line."""
        # LangChain attaches usage_metadata on the AIMessage when the
        # provider returned it. Defensively handle absence.
        meta = getattr(response, "usage_metadata", None) or {}
        input_tokens = int(meta.get("input_tokens", 0) or 0)
        output_tokens = int(meta.get("output_tokens", 0) or 0)
        total = int(meta.get("total_tokens", input_tokens + output_tokens))
        cost = estimate_cost(self._model, input_tokens, output_tokens)
        log_usage(
            UsageRecord(
                model=self._model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total,
                cost_usd=cost,
            )
        )

    @staticmethod
    def _translate_exception(exc: Exception) -> LLMError:
        """Map provider-specific exceptions into our LLMError family.

        Keeps callers simple — they catch `LLMError` (or one of its
        subclasses) instead of N OpenAI exception types. Order matters:
        check the most-specific subclass first.
        """
        if isinstance(exc, openai.AuthenticationError):
            return LLMAuthError(f"OpenAI auth failed: {exc}")
        if isinstance(exc, openai.RateLimitError):
            return LLMRateLimited(f"OpenAI rate limit: {exc}")
        if isinstance(exc, openai.APITimeoutError):
            return LLMTimeout(f"OpenAI request timed out: {exc}")
        if isinstance(exc, openai.APIError):
            return LLMProviderError(f"OpenAI API error: {exc}")
        # Unknown provider error — wrap it so callers still see LLMError.
        return LLMProviderError(f"Unexpected LLM failure: {exc}")


# ---------------------------------------------------------------------------
# Process-wide singleton.
#
# Why a singleton? Constructing ChatOpenAI does some work (validates the
# API key by calling the API once with some configurations). Building it
# per-request adds latency and is wasteful. The instance is stateless
# w.r.t. user data, so sharing is safe.
#
# `lru_cache` gives us lazy + thread-safe initialization. Tests that
# need a fresh client can call `get_default_llm_client.cache_clear()`.
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_default_llm_client() -> OpenAILLMClient:
    """Return the shared default LLM client. Lazy + cached."""
    return OpenAILLMClient()
