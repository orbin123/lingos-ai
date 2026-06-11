"""Refresh-token sessions: cookie issue, rotation, theft detection, logout."""

from __future__ import annotations

import math

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.email as email_pkg
from app import models  # noqa: F401 — populate the ORM registry
from app.core.config import settings
from app.core.database import Base, get_db
from app.core.security import decode_token, hash_password
from app.modules.auth.models import (
    AuthSession,
    EmailOtp,
    OAuthAccount,
    Permission,
    Role,
    RolePermission,
    User,
    UserProfile,
    UserRole,
)
from app.modules.auth.routes import router as auth_router
from app.modules.auth.session_service import REFRESH_COOKIE_NAME

AUTH_TABLES = [
    User.__table__,
    UserProfile.__table__,
    OAuthAccount.__table__,
    Role.__table__,
    UserRole.__table__,
    Permission.__table__,
    RolePermission.__table__,
    EmailOtp.__table__,
    AuthSession.__table__,
]

EMAIL = "session@example.com"
PASSWORD = "password123"


class NullEmailClient:
    def send(self, **kwargs):
        pass


@pytest.fixture()
def db_session(monkeypatch):
    monkeypatch.setattr(email_pkg, "_default_client", NullEmailClient())
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=AUTH_TABLES)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    user = User(
        email=EMAIL,
        password_hash=hash_password(PASSWORD),
        name="S",
        email_verified=True,
    )
    db.add(user)
    db.commit()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
        email_pkg._reset_default_email_client()


@pytest.fixture()
def client(db_session):
    app = FastAPI()
    app.include_router(auth_router, prefix="/auth")
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client


def _login(client, *, remember: bool = False):
    return client.post(
        "/auth/login",
        json={"email": EMAIL, "password": PASSWORD, "remember_me": remember},
    )


def _sessions(db) -> list[AuthSession]:
    return list(
        db.execute(select(AuthSession).order_by(AuthSession.id)).scalars()
    )


class TestLoginIssuesPair:
    def test_cookie_attributes(self, client):
        res = _login(client)
        assert res.status_code == 200
        set_cookie = res.headers["set-cookie"]
        assert REFRESH_COOKIE_NAME in set_cookie
        assert "HttpOnly" in set_cookie
        assert "SameSite=lax" in set_cookie.replace("samesite", "SameSite")
        assert "Path=/auth" in set_cookie

    def test_access_token_short_with_ver_claim(self, client):
        res = _login(client)
        payload = decode_token(res.json()["access_token"])
        assert payload["ver"] is True
        ttl_minutes = (payload["exp"] - payload["iat"]) / 60 if "iat" in payload else None
        if ttl_minutes is None:
            # No iat claim — bound the exp against the configured TTL.
            import time

            remaining = payload["exp"] - time.time()
            assert remaining <= settings.ACCESS_TOKEN_TTL_MINUTES * 60 + 5
            assert remaining > settings.ACCESS_TOKEN_TTL_MINUTES * 60 - 120
        else:
            assert math.isclose(
                ttl_minutes, settings.ACCESS_TOKEN_TTL_MINUTES, abs_tol=1
            )

    def test_session_row_created(self, client, db_session):
        _login(client)
        rows = _sessions(db_session)
        assert len(rows) == 1
        assert rows[0].family_id == rows[0].id
        assert rows[0].revoked_at is None

    def test_remember_me_extends_window(self, client, db_session):
        _login(client, remember=True)
        row = _sessions(db_session)[0]
        window_days = (row.expires_at - row.created_at).days
        assert window_days >= settings.REFRESH_TOKEN_REMEMBER_DAYS - 1

    def test_default_window(self, client, db_session):
        _login(client)
        row = _sessions(db_session)[0]
        window_days = (row.expires_at - row.created_at).days
        assert window_days >= settings.REFRESH_TOKEN_TTL_DAYS - 1
        assert window_days < settings.REFRESH_TOKEN_REMEMBER_DAYS - 1


class TestRefreshRotation:
    def test_refresh_returns_new_token_and_rotates(self, client, db_session):
        _login(client)
        old_cookie = client.cookies.get(REFRESH_COOKIE_NAME)
        res = client.post("/auth/refresh")
        assert res.status_code == 200
        assert res.json()["access_token"]
        new_cookie = client.cookies.get(REFRESH_COOKIE_NAME)
        assert new_cookie and new_cookie != old_cookie

        rows = _sessions(db_session)
        assert len(rows) == 2
        assert rows[0].revoked_at is not None  # old rotated away
        assert rows[1].revoked_at is None
        assert rows[1].family_id == rows[0].id  # same chain

    def test_reuse_after_rotation_revokes_family(self, client, db_session):
        _login(client)
        stolen = client.cookies.get(REFRESH_COOKIE_NAME)
        assert client.post("/auth/refresh").status_code == 200

        # Replay the pre-rotation token.
        client.cookies.set(REFRESH_COOKIE_NAME, stolen, path="/auth")
        res = client.post("/auth/refresh")
        assert res.status_code == 401

        # The whole family is dead — including the newest token.
        assert all(row.revoked_at is not None for row in _sessions(db_session))

    def test_missing_cookie_401(self, client):
        assert client.post("/auth/refresh").status_code == 401

    def test_garbage_cookie_401(self, client):
        client.cookies.set(REFRESH_COOKIE_NAME, "not-a-real-token", path="/auth")
        assert client.post("/auth/refresh").status_code == 401


class TestLogout:
    def test_logout_revokes_and_clears(self, client, db_session):
        _login(client)
        res = client.post("/auth/logout")
        assert res.status_code == 204
        assert _sessions(db_session)[0].revoked_at is not None
        # Subsequent refresh fails (cookie cleared and/or session revoked).
        assert client.post("/auth/refresh").status_code == 401

    def test_logout_without_cookie_is_noop_204(self, client):
        assert client.post("/auth/logout").status_code == 204


class TestPasswordResetRevokesSessions:
    def test_reset_kills_all_sessions(self, client, db_session):
        _login(client)
        # Issue the reset OTP directly through the service (email is nulled).
        from app.modules.auth.models import OtpPurpose
        from app.modules.auth.otp_service import OtpService

        user = db_session.execute(select(User)).scalar_one()

        class Capture:
            code: str | None = None

            def send(self, *, to, subject, html, text=None):
                import re

                Capture.code = re.search(r"\d{6}", text).group()

        OtpService(db_session, email_client=Capture()).issue(
            user=user, purpose=OtpPurpose.PASSWORD_RESET
        )
        res = client.post(
            "/auth/password-reset/confirm",
            json={"email": EMAIL, "code": Capture.code, "new_password": "brandnew123"},
        )
        assert res.status_code == 200
        assert all(row.revoked_at is not None for row in _sessions(db_session))
