"""Structured logging configuration (structlog) and request-trace middleware.

Every log line becomes a JSON object with named fields in production and a
pretty, colourised line in development. Both ``structlog.get_logger()`` calls
*and* legacy stdlib ``logging.getLogger(__name__)`` calls flow through the same
processor pipeline (via :class:`structlog.stdlib.ProcessorFormatter`), so the
~36 modules that still use stdlib logging render identically without any
rewrite.

The ``trace_id`` that correlates a single learner action across logs, cost
(``AIRequestLog``) and quality (``AIEvaluation``) already lives in
``app.ai.llm.eval_context``. We bridge it into the log pipeline with the
``_add_eval_context`` processor so that ``eval_context`` stays the single source
of truth — there is no second context store to keep in sync.
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import MutableMapping
from typing import Any

import structlog
from starlette.types import ASGIApp, Receive, Scope, Send

from app.ai.llm.eval_context import (
    get_eval_context,
    reset_eval_context,
    set_eval_context,
)
from app.core.config import settings


def _add_eval_context(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Inject the request-scoped ``trace_id``/``user_id`` into every log event.

    Reads from :mod:`app.ai.llm.eval_context` so logs join the same correlation
    id used by ``AIRequestLog`` and ``AIEvaluation``. ``setdefault`` keeps any
    value an individual call passed explicitly.
    """

    ctx = get_eval_context()
    if ctx.trace_id:
        event_dict.setdefault("trace_id", ctx.trace_id)
    if ctx.user_id is not None:
        event_dict.setdefault("user_id", ctx.user_id)
    return event_dict


def configure_logging(level: str | None = None, json_logs: bool | None = None) -> None:
    """Configure structlog + stdlib logging once at application startup.

    ``level`` defaults to ``settings.log_level``; ``json_logs`` defaults to JSON
    everywhere except the ``development`` environment (where a human-readable
    ``ConsoleRenderer`` is used instead).
    """

    resolved_level = (level or settings.log_level).upper()
    if json_logs is None:
        json_logs = settings.environment != "development"

    # Processors shared by structlog-native loggers and foreign (stdlib) records
    # so both carry trace_id, level, and an ISO timestamp.
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        _add_eval_context,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(resolved_level)
        ),
        cache_logger_on_first_use=True,
    )

    renderer: Any = (
        structlog.processors.JSONRenderer()
        if json_logs
        else structlog.dev.ConsoleRenderer()
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(resolved_level)


class TraceIDMiddleware:
    """Stamp a fresh ``trace_id`` on every inbound HTTP request.

    Binds the id into both the structlog contextvars (so ad-hoc structlog logs
    carry it) and the existing ``eval_context`` (so ``AIRequestLog`` rows and
    structured logs share one id) before auth resolves the user. WebSocket turns
    bind their own trace id inside ``process_message_stream``.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        trace_id = uuid.uuid4().hex
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(trace_id=trace_id)
        token = set_eval_context(trace_id=trace_id, user_id=None)
        try:
            await self.app(scope, receive, send)
        finally:
            reset_eval_context(token)
            structlog.contextvars.clear_contextvars()


class AccessLogMiddleware:
    """Emit one structured log line per HTTP request.

    Fields: method, path, status, latency_ms, user_id (from the JWT ``sub``,
    no DB hit), plus trace_id injected by the processor pipeline — so it must
    run *inside* :class:`TraceIDMiddleware`. Privacy by construction: never
    reads bodies and never logs the query string (WebSocket auth tokens ride
    in query strings; non-http scopes pass through untouched anyway).
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self._logger = structlog.get_logger("access")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = str(scope.get("path") or "")
        if self._skip(path):
            await self.app(scope, receive, send)
            return

        status_holder: dict[str, int | None] = {"status": None}

        async def send_wrapper(message: MutableMapping[str, Any]) -> None:
            if message["type"] == "http.response.start":
                status_holder["status"] = message["status"]
            await send(message)

        start = time.perf_counter()
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            status_holder["status"] = 500
            raise
        finally:
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            self._logger.info(
                "http_request",
                method=str(scope.get("method") or ""),
                path=path,
                status=status_holder["status"],
                latency_ms=latency_ms,
                user_id=self._user_id_from_headers(scope),
            )

    @staticmethod
    def _skip(path: str) -> bool:
        # Static blob mounts produce high-volume, low-value lines.
        static_prefixes = (
            settings.TTS_PUBLIC_URL_PREFIX,
            settings.IMAGEGEN_PUBLIC_URL_PREFIX,
        )
        if any(path.startswith(prefix) for prefix in static_prefixes):
            return True
        return path == "/favicon.ico"

    @staticmethod
    def _user_id_from_headers(scope: Scope) -> int | None:
        """Best-effort user id from the bearer token's ``sub`` — no DB hit.

        eval_context's user_id is bound and reset deep inside service calls,
        so it is already empty by the time the response finishes; decoding
        the JWT here is the only context-free way to attribute the request.
        """
        from app.core.security import decode_token

        auth_header = b""
        for key, value in scope.get("headers", []):
            if key.lower() == b"authorization":
                auth_header = value
                break
        prefix = b"bearer "
        if not auth_header[:7].lower() == prefix:
            return None
        payload = decode_token(auth_header[7:].decode("latin1"))
        if payload is None:
            return None
        try:
            return int(payload["sub"])
        except (KeyError, TypeError, ValueError):
            return None
