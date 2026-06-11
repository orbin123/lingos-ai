"""OTP-based password reset: generic request responses, confirm flow."""

from __future__ import annotations

import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.email as email_pkg
from app import models  # noqa: F401 — populate the ORM registry
from app.core.database import Base, get_db
from app.core.security import hash_password
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

EMAIL = "resetme@example.com"
OLD_PASSWORD = "oldpassword1"
NEW_PASSWORD = "newpassword1"


class CaptureEmailClient:
    def __init__(self):
        self.sent: list[dict] = []

    def send(self, *, to, subject, html, text=None):
        self.sent.append({"to": to, "subject": subject, "html": html, "text": text})

    def last_code(self) -> str:
        match = re.search(r"\d{6}", self.sent[-1]["text"])
        assert match
        return match.group()


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=AUTH_TABLES)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture()
def mailbox(monkeypatch):
    fake = CaptureEmailClient()
    monkeypatch.setattr(email_pkg, "_default_client", fake)
    yield fake
    email_pkg._reset_default_email_client()


@pytest.fixture()
def client(db_session, mailbox):
    app = FastAPI()
    app.include_router(auth_router, prefix="/auth")
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def verified_user(db_session) -> User:
    user = User(
        email=EMAIL,
        password_hash=hash_password(OLD_PASSWORD),
        name="Reset Me",
        email_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


class TestRequest:
    def test_existing_user_gets_code_generic_200(self, client, verified_user, mailbox):
        res = client.post("/auth/password-reset/request", json={"email": EMAIL})
        assert res.status_code == 200
        assert "If an account exists" in res.json()["message"]
        assert len(mailbox.sent) == 1
        assert "reset" in mailbox.sent[0]["subject"].lower()

    def test_unknown_email_same_generic_200_no_send(self, client, mailbox):
        res = client.post(
            "/auth/password-reset/request", json={"email": "ghost@example.com"}
        )
        assert res.status_code == 200
        assert "If an account exists" in res.json()["message"]
        assert mailbox.sent == []

    def test_oauth_only_account_generic_200_no_send(self, client, db_session, mailbox):
        db_session.add(
            User(email=EMAIL, password_hash=None, name="OAuth", email_verified=True)
        )
        db_session.commit()
        res = client.post("/auth/password-reset/request", json={"email": EMAIL})
        assert res.status_code == 200
        assert mailbox.sent == []


class TestConfirm:
    def test_confirm_sets_new_password(self, client, verified_user, mailbox):
        client.post("/auth/password-reset/request", json={"email": EMAIL})
        code = mailbox.last_code()
        res = client.post(
            "/auth/password-reset/confirm",
            json={"email": EMAIL, "code": code, "new_password": NEW_PASSWORD},
        )
        assert res.status_code == 200

        old_login = client.post(
            "/auth/login", json={"email": EMAIL, "password": OLD_PASSWORD}
        )
        assert old_login.status_code == 401
        new_login = client.post(
            "/auth/login", json={"email": EMAIL, "password": NEW_PASSWORD}
        )
        assert new_login.status_code == 200

    def test_wrong_code_400(self, client, verified_user, mailbox):
        client.post("/auth/password-reset/request", json={"email": EMAIL})
        real = mailbox.last_code()
        wrong = "000000" if real != "000000" else "111111"
        res = client.post(
            "/auth/password-reset/confirm",
            json={"email": EMAIL, "code": wrong, "new_password": NEW_PASSWORD},
        )
        assert res.status_code == 400
        assert res.json()["detail"]["code"] == "otp_invalid"

    def test_no_request_first_400_expired(self, client, verified_user):
        res = client.post(
            "/auth/password-reset/confirm",
            json={"email": EMAIL, "code": "123456", "new_password": NEW_PASSWORD},
        )
        assert res.status_code == 400
        assert res.json()["detail"]["code"] == "otp_expired"

    def test_registration_code_not_valid_for_reset(self, client, db_session, mailbox):
        # Purposes are isolated: a registration OTP can't reset a password.
        client.post(
            "/auth/signup",
            json={"email": EMAIL, "password": OLD_PASSWORD, "name": "X"},
        )
        code = mailbox.last_code()
        res = client.post(
            "/auth/password-reset/confirm",
            json={"email": EMAIL, "code": code, "new_password": NEW_PASSWORD},
        )
        assert res.status_code == 400
        assert res.json()["detail"]["code"] == "otp_expired"
