"""Tests for the G6 observability self-test route.

``POST /admin/observability/test-error`` deliberately returns a 500 so the
founder can prove error capture end-to-end. It is super-admin only and returns
the request ``trace_id`` (stamped by ``TraceIDMiddleware``) so the same id can be
matched in Sentry and CloudWatch.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import models  # noqa: F401 — populate the ORM registry
from app.core.logging import TraceIDMiddleware
from app.modules.admin.routes import router as admin_router
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import ROLE_ADMIN, ROLE_SUPER_ADMIN, Role, User, UserRole


def _user_with_roles(*role_names: str) -> User:
    """Build a transient (non-persisted) user holding the given roles."""
    user = User(email="obs@example.com", password_hash="x", name="O")
    for name in role_names:
        user.role_links.append(UserRole(role=Role(name=name)))
    return user


def _client_for(user: User) -> TestClient:
    app = FastAPI()
    app.add_middleware(TraceIDMiddleware)  # stamps the trace_id the route returns
    app.include_router(admin_router)
    app.dependency_overrides[get_current_user] = lambda: user
    # The route returns a JSONResponse(500); don't let TestClient re-raise.
    return TestClient(app, raise_server_exceptions=False)


def test_super_admin_gets_500_with_trace_id(monkeypatch):
    # Stub the Sentry forward so the test is hermetic (never hits a live DSN)
    # and we can assert the exception is forwarded.
    captured: list = []
    monkeypatch.setattr(
        "app.modules.admin.routes.capture_to_sentry",
        lambda exc=None: captured.append(exc),
    )

    user = _user_with_roles(ROLE_SUPER_ADMIN)
    with _client_for(user) as client:
        resp = client.post("/admin/observability/test-error")

    assert resp.status_code == 500
    body = resp.json()
    assert body["status"] == "error"
    # TraceIDMiddleware stamps a 32-char hex id; the route echoes it back.
    assert isinstance(body["trace_id"], str) and len(body["trace_id"]) == 32
    # The intentional error was forwarded to Sentry exactly once.
    assert len(captured) == 1 and isinstance(captured[0], RuntimeError)


def test_admin_only_user_forbidden():
    user = _user_with_roles(ROLE_ADMIN)
    with _client_for(user) as client:
        resp = client.post("/admin/observability/test-error")

    assert resp.status_code == 403
