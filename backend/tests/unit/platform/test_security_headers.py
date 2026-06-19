"""Security-headers middleware (G7).

HSTS + nosniff are emitted only when ENVIRONMENT=production, ride on every
response (incl. errors), and never overwrite a header an endpoint set itself.
"""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.testclient import TestClient

from app.core import security_headers
from app.core.security_headers import SecurityHeadersMiddleware


def _build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/ok")
    def ok() -> PlainTextResponse:
        return PlainTextResponse("ok")

    @app.get("/boom")
    def boom() -> PlainTextResponse:
        # HTTPException is handled by ExceptionMiddleware, which Starlette nests
        # *inside* app-added middleware — so the headers ride on this response.
        # (A truly unhandled error is caught by the outermost ServerErrorMiddleware,
        # outside our middleware; that edge case is intentionally not covered.)
        raise HTTPException(status_code=403, detail="nope")

    @app.get("/preset")
    def preset() -> PlainTextResponse:
        # Endpoint sets its own HSTS — middleware must not clobber it.
        return PlainTextResponse(
            "preset", headers={"Strict-Transport-Security": "max-age=1"}
        )

    return app


@pytest.fixture
def prod_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # The middleware reads settings.environment at construction time.
    monkeypatch.setattr(security_headers.settings, "environment", "production")


def test_headers_present_in_production(prod_env: None) -> None:
    client = TestClient(_build_app())
    resp = client.get("/ok")
    assert resp.status_code == 200
    assert (
        resp.headers["strict-transport-security"]
        == "max-age=86400; includeSubDomains"
    )
    assert resp.headers["x-content-type-options"] == "nosniff"


def test_headers_absent_outside_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(security_headers.settings, "environment", "development")
    client = TestClient(_build_app())
    resp = client.get("/ok")
    assert resp.status_code == 200
    assert "strict-transport-security" not in resp.headers
    assert "x-content-type-options" not in resp.headers


def test_headers_ride_on_error_responses(prod_env: None) -> None:
    client = TestClient(_build_app())
    resp = client.get("/boom")
    assert resp.status_code == 403
    assert (
        resp.headers["strict-transport-security"]
        == "max-age=86400; includeSubDomains"
    )


def test_does_not_overwrite_explicit_header(prod_env: None) -> None:
    client = TestClient(_build_app())
    resp = client.get("/preset")
    assert resp.headers["strict-transport-security"] == "max-age=1"
    # nosniff still appended (it wasn't preset).
    assert resp.headers["x-content-type-options"] == "nosniff"
