"""Reusable DB-backed logging for AI requests."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

from sqlalchemy.orm import Session

from app.modules.admin.models import AIRequestLog


T = TypeVar("T")


class AIRequestLoggingService:
    """Record one operational row per AI provider request.

    The service is intentionally small: callers can either record a row
    directly after an AI call, or wrap an awaitable with ``track_async``.
    It does not store prompts or raw user content.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def record(
        self,
        *,
        agent_name: str,
        model: str,
        status: str,
        user_id: int | None = None,
        trace_id: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        latency_ms: int | None = None,
        error_message: str | None = None,
        prompt_version: str | None = None,
        commit: bool = False,
    ) -> AIRequestLog:
        log = AIRequestLog(
            user_id=user_id,
            trace_id=trace_id,
            agent_name=agent_name,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message,
            prompt_version=prompt_version,
        )
        self.db.add(log)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(log)
        return log

    def record_success(
        self,
        *,
        agent_name: str,
        model: str,
        user_id: int | None = None,
        trace_id: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        latency_ms: int | None = None,
        prompt_version: str | None = None,
        commit: bool = False,
    ) -> AIRequestLog:
        return self.record(
            agent_name=agent_name,
            model=model,
            user_id=user_id,
            trace_id=trace_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            status="success",
            prompt_version=prompt_version,
            commit=commit,
        )

    def record_failure(
        self,
        *,
        agent_name: str,
        model: str,
        error_message: str,
        user_id: int | None = None,
        trace_id: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        latency_ms: int | None = None,
        prompt_version: str | None = None,
        commit: bool = False,
    ) -> AIRequestLog:
        return self.record(
            agent_name=agent_name,
            model=model,
            user_id=user_id,
            trace_id=trace_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            status="error",
            error_message=error_message,
            prompt_version=prompt_version,
            commit=commit,
        )

    async def track_async(
        self,
        call: Callable[[], Awaitable[T]],
        *,
        agent_name: str,
        model: str,
        user_id: int | None = None,
        trace_id: str | None = None,
        prompt_version: str | None = None,
        commit: bool = False,
    ) -> T:
        started = time.perf_counter()
        try:
            result = await call()
        except Exception as exc:
            self.record_failure(
                agent_name=agent_name,
                model=model,
                user_id=user_id,
                trace_id=trace_id,
                latency_ms=round((time.perf_counter() - started) * 1000),
                error_message=str(exc),
                prompt_version=prompt_version,
                commit=commit,
            )
            raise

        self.record_success(
            agent_name=agent_name,
            model=model,
            user_id=user_id,
            trace_id=trace_id,
            latency_ms=round((time.perf_counter() - started) * 1000),
            prompt_version=prompt_version,
            commit=commit,
        )
        return result
