"""Abstract LLM client contract.

Why an interface?
- Today: OpenAI via langchain_openai.
- Tomorrow: maybe Anthropic, Llama via Ollama, or a fine-tuned model.

Agents (feedback, task_generator, diagnosis_feedback) depend on this
Protocol — NOT on `langchain_openai.ChatOpenAI` directly. That's the
SOLID Dependency Inversion principle in practice: high-level code
depends on an abstraction, not on the concrete provider.

Two methods cover everything our agents need today:
  1. generate_text()       → free-form text (rare, used for debug/ping)
  2. generate_structured() → Pydantic-validated JSON (the workhorse)

Streaming + function-calling will be added later as new methods on the
same protocol — additive, never breaking.
"""

from __future__ import annotations

from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

# T must be a Pydantic model class so the LLM output can be validated
# against a schema. Bound to BaseModel so callers get full type-checking
# in IDEs + mypy.
T = TypeVar("T", bound=BaseModel)


class ILLMClient(Protocol):
    """Minimal contract every LLM provider implementation must satisfy."""

    async def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> str:
        """Run one round-trip and return raw text.

        Used for: debug pings, simple completions where we don't need a
        schema. NOT used for any agent that produces structured data.
        """
        ...

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_model: type[T],
        temperature: float | None = None,
    ) -> T:
        """Run one round-trip and return a Pydantic-validated instance.

        The implementation MUST guarantee that the returned object is an
        instance of `output_model` — either by using the provider's
        native structured-output mode (preferred) or by parsing JSON +
        calling `output_model.model_validate(...)`.

        Raises:
            LLMValidationError: provider returned content that didn't
                match the schema after the implementation's retries.
            LLMError: any other provider-side failure (timeout, 5xx,
                auth, rate-limit). Caller decides recovery.
        """
        ...

    # --------------------------------------------------------------
    # Escape hatch — for code that already uses LangChain's
    # `.with_structured_output(...)` pattern (feedback.py,
    # diagnosis_feedback.py). Lets us migrate incrementally without
    # rewriting prompts. Not part of the long-term contract.
    # --------------------------------------------------------------
    def raw_chat_model(self) -> Any:
        """Return the underlying chat-model object.

        Today: a `ChatOpenAI` instance. Tomorrow: whatever the provider
        exposes. Existing agents use this to call
        `.with_structured_output(SchemaCls).ainvoke(messages)`.

        New code should prefer `generate_structured(...)` instead.
        """
        ...
