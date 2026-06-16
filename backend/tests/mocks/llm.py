"""Canonical fake LLM clients.

Two shapes, because the app's LLM client surface has two halves and different
agents lean on different ones:

- `FakeLLMClient` — structured-output queue. `generate_structured(...)` pops the
  next queued response (a Pydantic instance to return, or an Exception to
  raise). Used by the session agents (evaluator / feedback / task-generator).
- `FakeTextLLM` — free-text + streaming. `generate_text(...)` / `stream_text(...)`.
  Used by the teacher agent.

Both record every call on `.calls` so tests can assert on prompt assembly.
Moved here verbatim from the per-file copies (Phase 3 of the testing refactor).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from pydantic import BaseModel

from app.ai.llm.exceptions import LLMProviderError


class FakeLLMClient:
    """Returns a queued sequence of responses; raises if the queue is empty.

    `responses` is a list of either:
      - BaseModel instances (returned to the caller as-is)
      - Exception instances (raised when generate_structured is invoked)
    """

    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.calls: list[dict] = []

    async def generate_text(self, **_kwargs) -> str:  # pragma: no cover
        raise NotImplementedError

    def stream_text(self, **_kwargs) -> AsyncIterator[str]:  # pragma: no cover
        raise NotImplementedError

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_model: type[BaseModel],
        temperature: float | None = None,
    ) -> BaseModel:
        self.calls.append({
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "output_model": output_model,
            "temperature": temperature,
        })
        if not self._responses:
            raise LLMProviderError("FakeLLMClient: no more queued responses")
        resp = self._responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp


class FakeTextLLM:
    """Free-text + streaming fake for the teacher agent."""

    def __init__(
        self,
        *,
        text: str | list[str] = "LLM teacher message.",
        chunks: list[str] | None = None,
        fail: bool = False,
    ) -> None:
        # `text` may be a single string (returned every call) or a list
        # (consumed in order, allowing distinct first/retry responses).
        if isinstance(text, str):
            self._texts: list[str] = [text]
        else:
            self._texts = list(text)
        self.chunks = chunks or ["LLM ", "stream."]
        self.fail = fail
        self.calls: list[dict] = []

    @property
    def text(self) -> str:
        return self._texts[-1] if self._texts else ""

    async def generate_text(self, **kwargs) -> str:
        self.calls.append(kwargs)
        if self.fail:
            raise RuntimeError("provider down")
        if len(self._texts) > 1:
            return self._texts.pop(0)
        return self._texts[0]

    async def stream_text(self, **kwargs) -> AsyncIterator[str]:
        self.calls.append(kwargs)
        if self.fail:
            raise RuntimeError("provider down")
        for chunk in self.chunks:
            yield chunk
