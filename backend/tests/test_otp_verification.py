"""Email-OTP registration flow: signup, verify, resend, rate caps,
anti-enumeration guarantees, unverified-login contract."""

from __future__ import annotations

import re
from datetime import timedelta

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
from app.modules.auth.models import (
    EmailOtp,
    OAuthAccount,
    Permission,
    Role,
    RolePermission,
    User,
    UserProfile,
    UserRole,
)
from app.modules.auth.otp_service import _utcnow
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
]

SIGNUP = {"email": "new@example.com", "password": "password123", "name": "New"}


class CaptureEmailClient:
    def __init__(self):
        self.sent: list[dict] = []

    def send(self, *, to, subject, html, text=None):
        self.sent.append({"to": to, "subject": subject, "html": html, "text": text})

    def last_code(self) -> str:
        match = re.search(r"\d{6}", self.sent[-1]["text"])
        assert match, f"no code in {self.sent[-1]}"
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


def _get_user(db, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def _latest_otp(db) -> EmailOtp:
    return db.execute(
        select(EmailOtp).order_by(EmailOtp.id.desc()).limit(1)
    ).scalar_one()


def _backdate_latest_otp(db, *, seconds: int = 0, expire: bool = False) -> None:
    otp = _latest_otp(db)
    if seconds:
        otp.created_at = otp.created_at - timedelta(seconds=seconds)
    if expire:
        otp.expires_at = _utcnow() - timedelta(seconds=1)
    db.commit()


class TestSignup:
    def test_creates_unverified_user_and_sends_code(self, client, db_session, mailbox):
        res = client.post("/auth/signup", json=SIGNUP)
        assert res.status_code == 201
        body = res.json()
        assert body["status"] == "pending_verification"
        assert body["email"] == SIGNUP["email"]
        assert "access_token" not in body

        user = _get_user(db_session, SIGNUP["email"])
        assert user is not None
        assert user.email_verified is False
        assert user.role_names() == ["learner"]
        assert len(mailbox.sent) == 1
        assert mailbox.sent[0]["to"] == SIGNUP["email"]
        assert re.search(r"\d{6}", mailbox.sent[0]["text"])

    def test_existing_unverified_email_reissues_code_same_response(
        self, client, db_session, mailbox
    ):
        first = client.post("/auth/signup", json=SIGNUP).json()
        _backdate_latest_otp(db_session, seconds=61)  # clear cooldown
        second = client.post("/auth/signup", json=SIGNUP)
        assert second.status_code == 201
        assert second.json() == first
        # No duplicate user; a second OTP was sent to the same account.
        users = db_session.execute(select(User)).scalars().all()
        assert len(users) == 1
        assert len(mailbox.sent) == 2

    def test_existing_verified_email_generic_response_with_notice_email(
        self, client, db_session, mailbox
    ):
        first = client.post("/auth/signup", json=SIGNUP).json()
        code = mailbox.last_code()
        client.post(
            "/auth/verify-email", json={"email": SIGNUP["email"], "code": code}
        )
        res = client.post("/auth/signup", json=SIGNUP)
        assert res.status_code == 201
        assert res.json() == first  # indistinguishable from a fresh signup
        assert "already have" in mailbox.sent[-1]["subject"].lower()


class TestVerifyEmail:
    def test_correct_code_verifies_and_returns_token(self, client, db_session, mailbox):
        client.post("/auth/signup", json=SIGNUP)
        code = mailbox.last_code()
        res = client.post(
            "/auth/verify-email", json={"email": SIGNUP["email"], "code": code}
        )
        assert res.status_code == 200
        assert res.json()["access_token"]
        user = _get_user(db_session, SIGNUP["email"])
        assert user.email_verified is True
        assert user.email_verified_at is not None
        assert _latest_otp(db_session).consumed_at is not None

    def test_wrong_code_400_and_attempt_counted(self, client, db_session, mailbox):
        client.post("/auth/signup", json=SIGNUP)
        real = mailbox.last_code()
        wrong = "000000" if real != "000000" else "111111"
        res = client.post(
            "/auth/verify-email", json={"email": SIGNUP["email"], "code": wrong}
        )
        assert res.status_code == 400
        assert res.json()["detail"]["code"] == "otp_invalid"
        assert _latest_otp(db_session).attempts == 1

    def test_attempts_exhausted_blocks_even_correct_code(self, client, mailbox):
        client.post("/auth/signup", json=SIGNUP)
        real = mailbox.last_code()
        wrong = "000000" if real != "000000" else "111111"
        for i in range(settings.OTP_MAX_VERIFY_ATTEMPTS):
            res = client.post(
                "/auth/verify-email", json={"email": SIGNUP["email"], "code": wrong}
            )
        assert res.status_code == 429
        assert res.json()["detail"]["code"] == "otp_attempts_exceeded"
        res = client.post(
            "/auth/verify-email", json={"email": SIGNUP["email"], "code": real}
        )
        assert res.status_code == 429

    def test_expired_code_400(self, client, db_session, mailbox):
        client.post("/auth/signup", json=SIGNUP)
        code = mailbox.last_code()
        _backdate_latest_otp(db_session, expire=True)
        res = client.post(
            "/auth/verify-email", json={"email": SIGNUP["email"], "code": code}
        )
        assert res.status_code == 400
        assert res.json()["detail"]["code"] == "otp_expired"

    def test_no_otp_at_all_400(self, client):
        res = client.post(
            "/auth/verify-email", json={"email": "ghost@example.com", "code": "123456"}
        )
        assert res.status_code == 400
        assert res.json()["detail"]["code"] == "otp_expired"


class TestResend:
    def test_cooldown_429_with_retry_after(self, client, mailbox):
        client.post("/auth/signup", json=SIGNUP)
        res = client.post("/auth/resend-otp", json={"email": SIGNUP["email"]})
        assert res.status_code == 429
        assert res.json()["detail"]["code"] == "otp_cooldown"
        assert int(res.headers["Retry-After"]) > 0

    def test_resend_after_cooldown_latest_code_wins(self, client, db_session, mailbox):
        client.post("/auth/signup", json=SIGNUP)
        old_code = mailbox.last_code()
        _backdate_latest_otp(db_session, seconds=61)
        res = client.post("/auth/resend-otp", json={"email": SIGNUP["email"]})
        assert res.status_code == 200
        new_code = mailbox.last_code()

        old_res = client.post(
            "/auth/verify-email", json={"email": SIGNUP["email"], "code": old_code}
        )
        # Old code was superseded — rejected even if digits happen to differ.
        if old_code != new_code:
            assert old_res.status_code == 400
        new_res = client.post(
            "/auth/verify-email", json={"email": SIGNUP["email"], "code": new_code}
        )
        assert new_res.status_code == 200

    def test_hourly_send_cap(self, client, db_session, mailbox):
        client.post("/auth/signup", json=SIGNUP)
        # Sends 2..5 (signup was #1), backdating cooldown each time.
        for _ in range(settings.OTP_MAX_SENDS_PER_HOUR - 1):
            _backdate_latest_otp(db_session, seconds=61)
            assert (
                client.post(
                    "/auth/resend-otp", json={"email": SIGNUP["email"]}
                ).status_code
                == 200
            )
        _backdate_latest_otp(db_session, seconds=61)
        res = client.post("/auth/resend-otp", json={"email": SIGNUP["email"]})
        assert res.status_code == 429
        assert res.json()["detail"]["code"] == "otp_send_limit"

    def test_unknown_email_generic_200_no_send(self, client, mailbox):
        res = client.post("/auth/resend-otp", json={"email": "ghost@example.com"})
        assert res.status_code == 200
        assert mailbox.sent == []

    def test_verified_email_generic_200_no_send(self, client, db_session, mailbox):
        client.post("/auth/signup", json=SIGNUP)
        code = mailbox.last_code()
        client.post(
            "/auth/verify-email", json={"email": SIGNUP["email"], "code": code}
        )
        sent_before = len(mailbox.sent)
        res = client.post("/auth/resend-otp", json={"email": SIGNUP["email"]})
        assert res.status_code == 200
        assert len(mailbox.sent) == sent_before


class TestLoginContract:
    def test_unverified_login_403_email_unverified(self, client):
        client.post("/auth/signup", json=SIGNUP)
        res = client.post(
            "/auth/login",
            json={"email": SIGNUP["email"], "password": SIGNUP["password"]},
        )
        assert res.status_code == 403
        detail = res.json()["detail"]
        assert detail["code"] == "email_unverified"
        assert detail["email"] == SIGNUP["email"]

    def test_bad_password_unverified_still_401(self, client):
        # Credentials are checked before verification state — a wrong
        # password must not reveal that the account is unverified.
        client.post("/auth/signup", json=SIGNUP)
        res = client.post(
            "/auth/login", json={"email": SIGNUP["email"], "password": "wrongpass1"}
        )
        assert res.status_code == 401

    def test_verified_login_succeeds(self, client, mailbox):
        client.post("/auth/signup", json=SIGNUP)
        code = mailbox.last_code()
        client.post(
            "/auth/verify-email", json={"email": SIGNUP["email"], "code": code}
        )
        res = client.post(
            "/auth/login",
            json={"email": SIGNUP["email"], "password": SIGNUP["password"]},
        )
        assert res.status_code == 200
        assert res.json()["access_token"]
