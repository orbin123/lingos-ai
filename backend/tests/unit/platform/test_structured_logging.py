"""Part C.5 — structured logging (structlog).

Covers the three new pieces:
  * ``configure_logging`` — emits JSON lines carrying ``trace_id``/``user_id``
    pulled from the eval context, plus ``event`` and ``level``.
  * the foreign (stdlib ``logging``) bridge — a plain ``logging.getLogger``
    call renders as JSON too, with the same bound ``trace_id``.
  * ``TraceIDMiddleware`` — stamps a non-empty ``trace_id`` into the eval
    context during an HTTP scope and clears it afterwards.
"""

from __future__ import annotations

import io
import json
import logging

import pytest
import structlog

from app.ai.llm.eval_context import (
    get_eval_context,
    reset_eval_context,
    set_eval_context,
)
from app.core.logging import TraceIDMiddleware, configure_logging


@pytest.fixture()
def captured_logs():
    """Configure JSON logging and capture root-handler output in a buffer."""
    configure_logging(level="INFO", json_logs=True)
    buffer = io.StringIO()
    root = logging.getLogger()
    # configure_logging installs exactly one StreamHandler; redirect its stream.
    root.handlers[0].setStream(buffer)
    try:
        yield buffer
    finally:
        structlog.contextvars.clear_contextvars()


def _lines(buffer: io.StringIO) -> list[dict]:
    return [json.loads(line) for line in buffer.getvalue().splitlines() if line]


def test_structlog_event_carries_eval_context(captured_logs):
    token = set_eval_context(trace_id="t-123", user_id=42)
    try:
        structlog.get_logger("test").warning("teaching_turn_failed", latency_ms=1200)
    finally:
        reset_eval_context(token)

    rows = _lines(captured_logs)
    row = next(r for r in rows if r.get("event") == "teaching_turn_failed")
    assert row["trace_id"] == "t-123"
    assert row["user_id"] == 42
    assert row["latency_ms"] == 1200
    assert row["level"] == "warning"


def test_foreign_stdlib_log_renders_json_with_trace_id(captured_logs):
    """A legacy ``logging.getLogger`` call flows through the same pipeline."""
    structlog.contextvars.bind_contextvars(trace_id="t-foreign")
    try:
        logging.getLogger("some.legacy.module").warning("legacy message")
    finally:
        structlog.contextvars.unbind_contextvars("trace_id")

    rows = _lines(captured_logs)
    row = next(r for r in rows if r.get("event") == "legacy message")
    assert row["trace_id"] == "t-foreign"
    assert row["level"] == "warning"


@pytest.mark.asyncio
async def test_trace_middleware_stamps_and_clears_trace_id():
    seen: dict[str, str | None] = {}

    async def app(scope, receive, send):
        seen["trace_id"] = get_eval_context().trace_id

    middleware = TraceIDMiddleware(app)

    async def receive():  # pragma: no cover - unused by the dummy app
        return {"type": "http.request"}

    async def send(message):  # pragma: no cover - unused by the dummy app
        return None

    await middleware({"type": "http"}, receive, send)

    assert seen["trace_id"]  # non-empty id was bound during the request
    # Context is reset after the request returns.
    assert get_eval_context().trace_id is None


@pytest.mark.asyncio
async def test_trace_middleware_passes_through_non_http():
    called = {"hit": False}

    async def app(scope, receive, send):
        called["hit"] = True

    await TraceIDMiddleware(app)({"type": "lifespan"}, None, None)
    assert called["hit"] is True
