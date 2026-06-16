"""Part D 8.3 — HTTP access logging (AccessLogMiddleware).

One structured ``http_request`` line per request with method, path, status,
latency_ms, user_id (from the JWT sub, no DB hit) and trace_id (bound by
TraceIDMiddleware outside). Bodies and query strings are never logged.
"""

from __future__ import annotations

import io
import json
import logging

import pytest
import structlog
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.logging import (
    AccessLogMiddleware,
    TraceIDMiddleware,
    configure_logging,
)
from app.core.security import create_access_token


@pytest.fixture()
def captured_logs():
    """Configure JSON logging and capture root-handler output in a buffer."""
    configure_logging(level="INFO", json_logs=True)
    # TestClient's httpx logs its own "HTTP Request: <full url>" line at INFO;
    # that's the test transport talking, not the app — silence it so the
    # buffer holds only server-side log lines.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    buffer = io.StringIO()
    root = logging.getLogger()
    root.handlers[0].setStream(buffer)
    try:
        yield buffer
    finally:
        structlog.contextvars.clear_contextvars()


def _lines(buffer: io.StringIO) -> list[dict]:
    return [json.loads(line) for line in buffer.getvalue().splitlines() if line]


def _access_lines(buffer: io.StringIO) -> list[dict]:
    return [r for r in _lines(buffer) if r.get("event") == "http_request"]


@pytest.fixture()
def client():
    app = FastAPI()

    @app.get("/ping")
    def ping() -> dict[str, bool]:
        return {"ok": True}

    @app.get("/audio/clip.mp3")
    def audio() -> dict[str, bool]:
        return {"ok": True}

    @app.get("/explode")
    def explode() -> None:
        raise RuntimeError("boom")

    # Same nesting as app/main.py: TraceID outermost, AccessLog inside.
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(TraceIDMiddleware)
    return TestClient(app, raise_server_exceptions=False)


def test_logs_one_line_with_user_id_and_trace_id(captured_logs, client):
    token = create_access_token({"sub": "42"})
    resp = client.get("/ping", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    rows = _access_lines(captured_logs)
    assert len(rows) == 1
    row = rows[0]
    assert row["method"] == "GET"
    assert row["path"] == "/ping"
    assert row["status"] == 200
    assert isinstance(row["latency_ms"], (int, float))
    assert row["user_id"] == 42
    assert row["trace_id"]


def test_missing_or_invalid_auth_logs_null_user(captured_logs, client):
    client.get("/ping")
    client.get("/ping", headers={"Authorization": "Bearer not-a-jwt"})

    rows = _access_lines(captured_logs)
    assert len(rows) == 2
    assert all(r["user_id"] is None for r in rows)
    assert all(r["status"] == 200 for r in rows)


def test_query_string_is_never_logged(captured_logs, client):
    client.get("/ping?token=supersecret-ws-token")

    raw = captured_logs.getvalue()
    assert "supersecret-ws-token" not in raw
    (row,) = _access_lines(captured_logs)
    assert row["path"] == "/ping"


def test_static_mount_paths_are_skipped(captured_logs, client):
    assert client.get("/audio/clip.mp3").status_code == 200
    assert _access_lines(captured_logs) == []


def test_unhandled_exception_logs_500_line(captured_logs, client):
    resp = client.get("/explode")
    assert resp.status_code == 500

    (row,) = _access_lines(captured_logs)
    assert row["status"] == 500
    assert row["path"] == "/explode"


@pytest.mark.asyncio
async def test_passes_through_non_http_scopes():
    called = {"hit": False}

    async def app(scope, receive, send):
        called["hit"] = True

    await AccessLogMiddleware(app)({"type": "websocket"}, None, None)
    assert called["hit"] is True
