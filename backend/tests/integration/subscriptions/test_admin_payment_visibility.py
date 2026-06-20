"""Phase 6 — Admin Data Verification (verify-only, no admin-panel changes).

Proves the redesign's central claim: the new Pay-Now-from-`verified` flow and
the Free-Trial flow write the *same* `Payment` / `Subscription` rows the existing
admin module already reads, so `admin/payments`, `admin/subscribers`, and
`admin/users/{id}/billing` populate automatically — with provider-ID masking
intact — without any admin code change.

These tests drive the *real* payment routes (mock Razorpay provider) and the
real `SubscriptionService`, then read the *existing* `AdminRepository` on the
same session. No admin code is touched.

It also documents the one known gap: `admin/user-progress`
(`AdminRepository.list_user_progress`) keys plan/access off the legacy
`Purchase` table, which the new `Subscription`-based Pay-Now flow never writes.
See `test_pay_now_writes_subscription_not_purchase` and the flagged follow-up.
"""

from __future__ import annotations

import hashlib
import hmac
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base, get_db
from app.modules.admin.repository import AdminRepository
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import Role, User, UserRole
from app.modules.preferences.models import UserCoursePreference
from app.modules.subscriptions.models import (
    Payment,
    PaymentEvent,
    Purchase,
    Subscription,
    SubscriptionStatus,
)
from app.modules.subscriptions.payment_routes import payments_router
from app.modules.subscriptions.service import SubscriptionService
from app.payments import _reset_default_razorpay_client

KEY_SECRET = "rzp_test_key_secret"
WEBHOOK_SECRET = "rzp_test_webhook_secret"


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            Role.__table__,
            UserRole.__table__,
            UserCoursePreference.__table__,
            Subscription.__table__,
            Purchase.__table__,
            Payment.__table__,
            PaymentEvent.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


@pytest.fixture()
def user(db_session) -> User:
    row = User(
        email="payer@example.com", password_hash="x", name="P", email_verified=True
    )
    db_session.add(row)
    db_session.commit()
    return row


@pytest.fixture()
def client(db_session, user, monkeypatch):
    monkeypatch.setattr(settings, "RAZORPAY_KEY_ID", "rzp_test_keyid")
    monkeypatch.setattr(settings, "RAZORPAY_KEY_SECRET", KEY_SECRET)
    monkeypatch.setattr(settings, "RAZORPAY_WEBHOOK_SECRET", WEBHOOK_SECRET)
    # Force the mock provider despite keys being "configured" above.
    _reset_default_razorpay_client()
    import app.payments as payments_pkg
    from app.payments import mock_client

    monkeypatch.setattr(
        payments_pkg, "_default_client", mock_client.MockRazorpayClient()
    )

    app = FastAPI()
    app.include_router(payments_router)
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: user
    with TestClient(app) as test_client:
        yield test_client
    _reset_default_razorpay_client()


def _checkout_signature(order_id: str, payment_id: str) -> str:
    return hmac.new(
        KEY_SECRET.encode(), f"{order_id}|{payment_id}".encode(), hashlib.sha256
    ).hexdigest()


def _webhook(client, body: dict, *, event_id: str, sign: bool = True):
    raw = json.dumps(body).encode()
    signature = (
        hmac.new(WEBHOOK_SECRET.encode(), raw, hashlib.sha256).hexdigest()
        if sign
        else "bogus"
    )
    return client.post(
        "/api/payments/webhook",
        content=raw,
        headers={
            "x-razorpay-signature": signature,
            "x-razorpay-event-id": event_id,
            "content-type": "application/json",
        },
    )


def _captured_event(order_id: str, *, payment_id: str = "pay_123") -> dict:
    return {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": payment_id,
                    "order_id": order_id,
                    "method": "upi",
                    "notes": {"plan_id": "beginner-24w"},
                }
            }
        },
    }


def _create_order(client, plan_id: str = "beginner-24w") -> str:
    res = client.post("/api/payments/create-order", json={"plan_id": plan_id})
    assert res.status_code == 200
    return res.json()["order_id"]


def _pay_now(client, plan_id: str = "beginner-24w") -> str:
    """Run a full Pay-Now: create-order → verify (fast path) → captured webhook.

    Mirrors the live ordering (verify wins the race, webhook backfills `method`)
    so the resulting rows are exactly what a real reviewer payment produces.
    """
    order_id = _create_order(client, plan_id)
    payment_id = "pay_live_abcdef1234"  # long → exercises the `....` masking form
    res = client.post(
        "/api/payments/verify",
        json={
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": _checkout_signature(order_id, payment_id),
        },
    )
    assert res.status_code == 200
    assert _webhook(
        client, _captured_event(order_id), event_id="evt_admin_vis"
    ).status_code == 200
    return order_id


class TestAdminPaymentsView:
    """GET /admin/payments surfaces the new transaction with masked IDs."""

    def test_pay_now_payment_visible_in_admin_payments(self, client, db_session):
        order_id = _pay_now(client)

        payments = AdminRepository(db_session).list_payments()
        assert len(payments) == 1
        payment = payments[0]
        assert payment.status == "paid"
        assert payment.method == "upi"  # webhook backfilled it (Phase 4)
        assert payment.amount == 999.0
        assert payment.currency == "INR"
        # Provider IDs are masked at the repository layer (no raw id leaks).
        assert payment.provider_order_id != order_id
        assert "..." in (payment.provider_order_id or "")
        assert payment.provider_payment_id != "pay_live_abcdef1234"
        assert "..." in (payment.provider_payment_id or "")


class TestAdminSubscribersView:
    """GET /admin/subscribers groups payers vs trial users from stored rows."""

    def test_pay_now_payer_listed_as_subscriber(self, client, db_session, user):
        _pay_now(client)

        overview = AdminRepository(db_session).list_subscribers()
        payer = next(
            (s for s in overview.subscribers if s.user_id == user.id), None
        )
        assert payer is not None, "payer should appear under subscribers"
        assert payer.status == "active"
        assert payer.plan_id == "beginner-24w"
        assert payer.plan_name == "24-Week Foundation"
        assert payer.amount_paid == 999.0
        assert payer.currency == "INR"
        assert payer.access_expires_at is not None  # 2-year paid window
        # The payer is not double-listed as a trial user.
        assert all(t.user_id != user.id for t in overview.trials)

    def test_trial_user_listed_in_trials(self, db_session):
        # A separate `verified` user takes the Free-Trial branch.
        trial_user = User(
            email="trialist@example.com",
            password_hash="x",
            name="T",
            email_verified=True,
        )
        db_session.add(trial_user)
        db_session.commit()

        service = SubscriptionService(db_session)
        service.select_plan(trial_user, "beginner-24w")
        service.start_trial(trial_user)

        overview = AdminRepository(db_session).list_subscribers()
        item = next(
            (t for t in overview.trials if t.user_id == trial_user.id), None
        )
        assert item is not None, "trial user should appear under trials"
        assert item.status == "trial"
        assert item.email_verified is True
        assert item.trial_started_at is not None
        assert item.trial_ends_at is not None
        # A trial user is never listed as a paying subscriber.
        assert all(s.user_id != trial_user.id for s in overview.subscribers)


class TestAdminUserBillingView:
    """GET /admin/users/{id}/billing shows subscription + payment history."""

    def test_user_billing_shows_subscription_and_payments(
        self, client, db_session, user
    ):
        _pay_now(client)

        billing = AdminRepository(db_session).get_user_billing(user.id)
        assert billing is not None
        assert billing.subscription is not None
        assert billing.subscription.status == SubscriptionStatus.ACTIVE.value
        assert billing.subscription.plan_id == "beginner-24w"
        assert billing.subscription.current_period_end is not None
        assert len(billing.payments) == 1
        # Payment history masks provider IDs too.
        assert billing.payments[0].status == "paid"
        assert "..." in (billing.payments[0].provider_order_id or "")


class TestUserProgressGap:
    """Documents the one verified gap (flagged as a follow-up, not patched).

    `AdminRepository.list_user_progress` reads plan/access from the legacy
    `Purchase` table only. The new Pay-Now flow activates via `Subscription`
    (`activate_from_payment`) and never writes a `Purchase`, so the admin
    User-Progress view shows new-flow payers with no plan/access. We pin that
    behaviour here: a future fix that teaches user-progress to read
    `Subscription` should flip this assertion deliberately.
    """

    def test_pay_now_writes_subscription_not_purchase(self, client, db_session):
        _pay_now(client)

        # New flow → exactly one active Subscription, and NO legacy Purchase.
        assert db_session.query(Subscription).count() == 1
        assert db_session.query(Purchase).count() == 0
