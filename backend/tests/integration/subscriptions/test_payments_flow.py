"""Razorpay payment flow: order creation, verify, webhook (mock provider)."""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base, get_db
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
from app.modules.subscriptions.service import AccessState, SubscriptionService
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
    from app.payments import mock_client
    import app.payments as payments_pkg

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


class TestCreateOrder:
    def test_uses_server_catalog_amount(self, client):
        res = client.post(
            "/api/payments/create-order", json={"plan_id": "beginner-24w"}
        )
        assert res.status_code == 200
        body = res.json()
        assert body["amount"] == 99900  # ₹999 in paise, from PLAN_CATALOG
        assert body["currency"] == "INR"
        assert body["key_id"] == "rzp_test_keyid"
        assert body["order_id"].startswith("order_mock_")

    def test_unknown_plan_404(self, client):
        res = client.post("/api/payments/create-order", json={"plan_id": "nope"})
        assert res.status_code == 404

    def test_persists_created_payment(self, client, db_session, user):
        res = client.post(
            "/api/payments/create-order", json={"plan_id": "beginner-48w"}
        )
        order_id = res.json()["order_id"]
        payment = (
            db_session.query(Payment)
            .filter(Payment.provider_order_id == order_id)
            .one()
        )
        assert payment.user_id == user.id
        assert payment.status == "created"
        assert float(payment.amount) == 1999.0


class TestVerify:
    def _create_order(self, client) -> str:
        res = client.post(
            "/api/payments/create-order", json={"plan_id": "beginner-24w"}
        )
        return res.json()["order_id"]

    def test_valid_signature_activates_subscription(self, client, db_session, user):
        order_id = self._create_order(client)
        res = client.post(
            "/api/payments/verify",
            json={
                "razorpay_order_id": order_id,
                "razorpay_payment_id": "pay_ok",
                "razorpay_signature": _checkout_signature(order_id, "pay_ok"),
            },
        )
        assert res.status_code == 200
        assert res.json()["access_state"] == "active"

        payment = (
            db_session.query(Payment)
            .filter(Payment.provider_order_id == order_id)
            .one()
        )
        assert payment.status == "paid"
        assert payment.provider_payment_id == "pay_ok"

        subscription = db_session.query(Subscription).one()
        assert subscription.status == SubscriptionStatus.ACTIVE.value
        # 2-year paid window (ACCESS_WINDOW_YEARS).
        assert (
            subscription.current_period_end.year
            == datetime.now(timezone.utc).year + settings.ACCESS_WINDOW_YEARS
        )

    def test_bad_signature_400_no_activation(self, client, db_session, user):
        order_id = self._create_order(client)
        res = client.post(
            "/api/payments/verify",
            json={
                "razorpay_order_id": order_id,
                "razorpay_payment_id": "pay_ok",
                "razorpay_signature": "tampered",
            },
        )
        assert res.status_code == 400
        assert res.json()["detail"]["code"] == "signature_invalid"
        payment = (
            db_session.query(Payment)
            .filter(Payment.provider_order_id == order_id)
            .one()
        )
        assert payment.status == "created"  # state unchanged (§14)
        assert (
            SubscriptionService(db_session).resolve_access(user).state
            is AccessState.VERIFIED
        )

    def test_idempotent_double_call(self, client):
        order_id = self._create_order(client)
        payload = {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": "pay_ok",
            "razorpay_signature": _checkout_signature(order_id, "pay_ok"),
        }
        assert client.post("/api/payments/verify", json=payload).status_code == 200
        res = client.post("/api/payments/verify", json=payload)
        assert res.status_code == 200
        assert res.json()["access_state"] == "active"

    def test_order_of_other_user_404(self, client, db_session):
        other = User(
            email="other@example.com",
            password_hash="x",
            name="O",
            email_verified=True,
        )
        db_session.add(other)
        db_session.flush()
        db_session.add(
            Payment(
                user_id=other.id,
                provider="razorpay",
                provider_order_id="order_foreign",
                amount=999.0,
                currency="INR",
                status="created",
            )
        )
        db_session.commit()
        res = client.post(
            "/api/payments/verify",
            json={
                "razorpay_order_id": "order_foreign",
                "razorpay_payment_id": "pay_x",
                "razorpay_signature": _checkout_signature("order_foreign", "pay_x"),
            },
        )
        assert res.status_code == 404


class TestByOrder:
    """GET /api/payments/by-order/{order_id} — the success-page proof read."""

    def _create_order(self, client, plan_id: str = "beginner-24w") -> str:
        res = client.post("/api/payments/create-order", json={"plan_id": plan_id})
        return res.json()["order_id"]

    def _verify(self, client, order_id: str, payment_id: str = "pay_proof") -> None:
        client.post(
            "/api/payments/verify",
            json={
                "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": _checkout_signature(order_id, payment_id),
            },
        )

    def test_verified_user_pay_now_then_proof_fields(self, client):
        # Fresh `verified` user (the fixture) can Pay-Now end-to-end and read
        # back a fully-populated proof record.
        order_id = self._create_order(client)
        self._verify(client, order_id)

        res = client.get(f"/api/payments/by-order/{order_id}")
        assert res.status_code == 200
        body = res.json()
        assert body["provider_order_id"] == order_id
        assert body["provider_payment_id"] == "pay_proof"
        assert body["amount"] == 999.0  # rupees (catalog), not paise
        assert body["currency"] == "INR"
        assert body["status"] == "paid"
        assert body["plan_id"] == "beginner-24w"
        assert body["plan_name"] == "24-Week Foundation"
        assert body["subscription_status"] == "active"
        assert body["paid_at"] is not None
        assert body["current_period_end"] is not None

    def test_method_null_after_verify_only(self, client):
        # The checkout verify fast-path does not set `method` — it stays null
        # until the webhook lands (success page renders "Processing…").
        order_id = self._create_order(client)
        self._verify(client, order_id)
        res = client.get(f"/api/payments/by-order/{order_id}")
        assert res.json()["method"] is None

    def test_method_null_pre_webhook_populated_when_webhook_activates(self, client):
        # Webhook-wins ordering: method is null right after create-order and is
        # populated once the webhook activates the payment.
        order_id = self._create_order(client)
        pre = client.get(f"/api/payments/by-order/{order_id}").json()
        assert pre["status"] == "created"
        assert pre["method"] is None
        assert pre["subscription_status"] == "verified"

        _webhook(client, _captured_event(order_id), event_id="evt_proof")
        post = client.get(f"/api/payments/by-order/{order_id}").json()
        assert post["status"] == "paid"
        assert post["method"] == "upi"
        assert post["subscription_status"] == "active"

    def test_unknown_order_404(self, client):
        res = client.get("/api/payments/by-order/order_missing")
        assert res.status_code == 404

    def test_other_users_order_404_no_idor(self, client, db_session):
        other = User(
            email="other-proof@example.com",
            password_hash="x",
            name="O",
            email_verified=True,
        )
        db_session.add(other)
        db_session.flush()
        db_session.add(
            Payment(
                user_id=other.id,
                provider="razorpay",
                provider_order_id="order_other_idor",
                provider_payment_id="pay_other",
                amount=999.0,
                currency="INR",
                status="paid",
            )
        )
        db_session.commit()
        res = client.get("/api/payments/by-order/order_other_idor")
        assert res.status_code == 404


class TestWebhook:
    def _create_order(self, client) -> str:
        res = client.post(
            "/api/payments/create-order", json={"plan_id": "beginner-24w"}
        )
        return res.json()["order_id"]

    def test_bad_signature_400_event_not_stored(self, client, db_session):
        res = _webhook(
            client,
            _captured_event("order_x"),
            event_id="evt_bad",
            sign=False,
        )
        assert res.status_code == 400
        assert db_session.query(PaymentEvent).count() == 0

    def test_payment_captured_activates(self, client, db_session, user):
        order_id = self._create_order(client)
        res = _webhook(client, _captured_event(order_id), event_id="evt_1")
        assert res.status_code == 200

        payment = (
            db_session.query(Payment)
            .filter(Payment.provider_order_id == order_id)
            .one()
        )
        assert payment.status == "paid"
        assert payment.method == "upi"
        assert (
            SubscriptionService(db_session).resolve_access(user).state
            is AccessState.ACTIVE
        )
        event = db_session.query(PaymentEvent).one()
        assert event.event_id == "evt_1"
        assert event.processed_at is not None

    def test_duplicate_event_id_noop(self, client, db_session):
        order_id = self._create_order(client)
        assert (
            _webhook(client, _captured_event(order_id), event_id="evt_dup").status_code
            == 200
        )
        assert (
            _webhook(client, _captured_event(order_id), event_id="evt_dup").status_code
            == 200
        )
        assert db_session.query(PaymentEvent).count() == 1

    def test_webhook_then_verify_race_idempotent(self, client, db_session):
        order_id = self._create_order(client)
        _webhook(client, _captured_event(order_id), event_id="evt_race")
        res = client.post(
            "/api/payments/verify",
            json={
                "razorpay_order_id": order_id,
                "razorpay_payment_id": "pay_123",
                "razorpay_signature": _checkout_signature(order_id, "pay_123"),
            },
        )
        assert res.status_code == 200
        assert res.json()["access_state"] == "active"
        assert db_session.query(Subscription).count() == 1

    def test_verify_then_webhook_race_idempotent(self, client, db_session):
        order_id = self._create_order(client)
        client.post(
            "/api/payments/verify",
            json={
                "razorpay_order_id": order_id,
                "razorpay_payment_id": "pay_123",
                "razorpay_signature": _checkout_signature(order_id, "pay_123"),
            },
        )
        res = _webhook(client, _captured_event(order_id), event_id="evt_after")
        assert res.status_code == 200
        assert db_session.query(Subscription).count() == 1

    def test_verify_then_webhook_backfills_method(self, client, db_session):
        # Common Pay-Now ordering: verify wins the race and activates without
        # setting `method`; the later captured webhook must backfill `method` on
        # the already-paid row (so the success page / admin views show the real
        # instrument) without re-activating.
        order_id = self._create_order(client)
        client.post(
            "/api/payments/verify",
            json={
                "razorpay_order_id": order_id,
                "razorpay_payment_id": "pay_123",
                "razorpay_signature": _checkout_signature(order_id, "pay_123"),
            },
        )
        payment = (
            db_session.query(Payment)
            .filter(Payment.provider_order_id == order_id)
            .one()
        )
        assert payment.status == "paid"
        assert payment.method is None  # verify fast-path never sets it

        res = _webhook(client, _captured_event(order_id), event_id="evt_backfill")
        assert res.status_code == 200

        db_session.refresh(payment)
        assert payment.method == "upi"  # webhook backfilled it
        assert payment.provider_payment_id == "pay_123"  # verify's id, untouched
        assert db_session.query(Subscription).count() == 1  # no double activation

    def test_payment_failed_records_reason_no_activation(
        self, client, db_session, user
    ):
        order_id = self._create_order(client)
        body = {
            "event": "payment.failed",
            "payload": {
                "payment": {
                    "entity": {
                        "id": "pay_fail",
                        "order_id": order_id,
                        "method": "card",
                        "error_description": "Card declined",
                    }
                }
            },
        }
        res = _webhook(client, body, event_id="evt_fail")
        assert res.status_code == 200
        payment = (
            db_session.query(Payment)
            .filter(Payment.provider_order_id == order_id)
            .one()
        )
        assert payment.status == "failed"
        assert payment.failure_reason == "Card declined"
        assert (
            SubscriptionService(db_session).resolve_access(user).state
            is AccessState.VERIFIED
        )

    def test_mid_trial_upgrade_starts_period_now(self, client, db_session, user):
        service = SubscriptionService(db_session)
        service.select_plan(user, "beginner-24w")
        service.start_trial(user)

        order_id = self._create_order(client)
        _webhook(client, _captured_event(order_id), event_id="evt_trial_up")

        subscription = db_session.query(Subscription).one()
        assert subscription.status == SubscriptionStatus.ACTIVE.value
        # No trial-day credit: the paid period starts at activation time.
        now = datetime.now(timezone.utc)
        start = subscription.current_period_start.replace(tzinfo=timezone.utc)
        assert abs((start - now).total_seconds()) < 60
