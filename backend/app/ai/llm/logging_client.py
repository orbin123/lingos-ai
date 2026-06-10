"""``ILLMClient`` decorator that records one ``AIRequestLog`` row per call.

This is the instrumentation seam for AI observability. It wraps a real client
(e.g. :class:`OpenAILLMClient`), tags every call with a fixed ``agent_name``,
and on each call writes an operational row capturing latency, status, model,
tokens, and the correlation ``trace_id`` / ``user_id`` from
:mod:`app.ai.llm.eval_context`.

Design constraints (mirrors the existing RAG background workers):

* **Never break a learner call.** Any logging failure is swallowed + logged.
* **Never touch a request-scoped session.** Each write opens its own short
  :func:`SessionLocal`, commits, and closes — the request/WebSocket session is
  not safe for concurrent use.
* **No prompts / content stored** — only counts, timing, model, status.

Token capture: the wrapped client is constructed with ``usage_sink=record_usage``
so the most recent call's :class:`UsageRecord` lands in a context-local slot that
:meth:`_track` reads immediately after the call. ``contextvars`` keeps this
isolated per async task; calls within one task are sequential, so the slot is
unambiguous.
"""

from __future__ import annotations

import contextvars
import logging
import time
from collections.abc import AsyncIterator

from app.ai.llm.eval_context import get_eval_context
from app.ai.llm.interface import ILLMClient
from app.ai.llm.usage import UsageRecord
from app.ai.request_logging import AIRequestLoggingService
from app.core.config import settings
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


_LAST_USAGE: contextvars.ContextVar[UsageRecord | None] = contextvars.ContextVar(
    "ai_last_llm_usage", default=None
)


def record_usage(record: UsageRecord) -> None:
    """Usage sink: stash the latest call's usage for the active task.

    Pass this as ``usage_sink=`` when constructing the client a
    ``LoggingLLMClient`` wraps.
    """
    _LAST_USAGE.set(record)


class LoggingLLMClient:
    """Wrap an ``ILLMClient`` so every call is logged to ``AIRequestLog``."""

    def __init__(
        self,
        inner: ILLMClient,
        *,
        agent_name: str,
        model: str,
    ) -> None:
        self._inner = inner
        self._agent_name = agent_name
        self._model = model

    async def generate_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> str:
        return await self._track(
            lambda: self._inner.generate_text(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            )
        )

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_model: type,
        temperature: float | None = None,
    ):
        return await self._track(
            lambda: self._inner.generate_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                output_model=output_model,
                temperature=temperature,
            )
        )

    def stream_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> AsyncIterator[str]:
        # Streaming usage is not reliably available; delegate without logging.
        return self._inner.stream_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    async def _track(self, call):
        if not settings.AI_REQUEST_LOGGING_ENABLED:
            return await call()

        _LAST_USAGE.set(None)
        started = time.perf_counter()
        try:
            result = await call()
        except Exception as exc:
            self._write(
                status="error",
                latency_ms=round((time.perf_counter() - started) * 1000),
                error_message=str(exc),
                usage=_LAST_USAGE.get(),
            )
            raise

        self._write(
            status="success",
            latency_ms=round((time.perf_counter() - started) * 1000),
            error_message=None,
            usage=_LAST_USAGE.get(),
        )
        return result

    def _write(
        self,
        *,
        status: str,
        latency_ms: int,
        error_message: str | None,
        usage: UsageRecord | None,
    ) -> None:
        ctx = get_eval_context()
        try:
            db = SessionLocal()
            try:
                AIRequestLoggingService(db).record(
                    agent_name=self._agent_name,
                    model=usage.model if usage else self._model,
                    status=status,
                    user_id=ctx.user_id,
                    trace_id=ctx.trace_id,
                    input_tokens=usage.input_tokens if usage else None,
                    output_tokens=usage.output_tokens if usage else None,
                    latency_ms=latency_ms,
                    error_message=error_message,
                    commit=True,
                )
            finally:
                db.close()
        except Exception:  # pragma: no cover - defensive
            # Observability must never break the learner flow.
            logger.warning(
                "AIRequestLog write failed for agent=%s", self._agent_name,
                exc_info=True,
            )
