"""Subscription endpoints: select-plan → start-trial flow + entitlement reads."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import Role, User, UserProfile, UserRole
from app.modules.preferences.models import UserCoursePreference
from app.modules.subscriptions.models import Purchase, Subscription
from app.modules.subscriptions.routes import subscription_router


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
            UserProfile.__table__,
            Role.__table__,
            UserRole.__table__,
            UserCoursePreference.__table__,
            Subscription.__table__,
            Purchase.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _user(db, *, verified: bool = True) -> User:
    user = User(
        email="endpoints@example.com",
        password_hash="x",
        name="E",
        email_verified=verified,
    )
    db.add(user)
    db.commit()
    return user


def _client(db, user: User) -> TestClient:
    app = FastAPI()
    app.include_router(subscription_router)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: user
    return TestClient(app)


class TestSelectPlanStartTrialFlow:
    def test_full_flow(self, db_session):
        user = _user(db_session)
        with _client(db_session, user) as client:
            res = client.post(
                "/api/subscriptions/select-plan", json={"plan_id": "beginner-24w"}
            )
            assert res.status_code == 200
            body = res.json()
            assert body["access_state"] == "verified"
            assert body["plan_id"] == "beginner-24w"
            assert body["amount"] == 999.0

            res = client.post("/api/subscriptions/start-trial")
            assert res.status_code == 200
            body = res.json()
            assert body["access_state"] == "trial"
            assert body["days_remaining"] == 7

            # Idempotent second call.
            res = client.post("/api/subscriptions/start-trial")
            assert res.status_code == 200
            assert res.json()["access_state"] == "trial"

    def test_start_trial_without_plan_409(self, db_session):
        user = _user(db_session)
        with _client(db_session, user) as client:
            res = client.post("/api/subscriptions/start-trial")
            assert res.status_code == 409
            assert res.json()["detail"]["code"] == "plan_not_selected"

    def test_select_unknown_plan_404(self, db_session):
        user = _user(db_session)
        with _client(db_session, user) as client:
            res = client.post(
                "/api/subscriptions/select-plan", json={"plan_id": "nope"}
            )
            assert res.status_code == 404

    def test_plan_locked_after_trial_409(self, db_session):
        user = _user(db_session)
        with _client(db_session, user) as client:
            client.post(
                "/api/subscriptions/select-plan", json={"plan_id": "beginner-24w"}
            )
            client.post("/api/subscriptions/start-trial")
            res = client.post(
                "/api/subscriptions/select-plan", json={"plan_id": "beginner-48w"}
            )
            assert res.status_code == 409
            assert res.json()["detail"]["code"] == "plan_locked"

    def test_trial_already_used_409(self, db_session):
        user = _user(db_session)
        with _client(db_session, user) as client:
            client.post(
                "/api/subscriptions/select-plan", json={"plan_id": "beginner-24w"}
            )
            client.post("/api/subscriptions/start-trial")
        # Expire the trial directly, then try to restart it.
        row = db_session.query(Subscription).one()
        row.trial_ends_at = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()
        with _client(db_session, user) as client:
            res = client.post("/api/subscriptions/start-trial")
            assert res.status_code == 409
            assert res.json()["detail"]["code"] == "trial_already_used"

    def test_unverified_user_403(self, db_session):
        user = _user(db_session, verified=False)
        with _client(db_session, user) as client:
            res = client.post(
                "/api/subscriptions/select-plan", json={"plan_id": "beginner-24w"}
            )
            assert res.status_code == 403
            assert res.json()["detail"]["code"] == "email_unverified"


class TestEntitlementRead:
    def test_get_me_returns_entitlement_view(self, db_session):
        user = _user(db_session)
        with _client(db_session, user) as client:
            res = client.get("/api/subscriptions/me")
            assert res.status_code == 200
            assert res.json()["access_state"] == "verified"

    def test_get_me_legacy_purchase_maps_active(self, db_session):
        user = _user(db_session)
        db_session.add(
            Purchase(
                user_id=user.id,
                plan_id="beginner-48w",
                plan_name="48-Week Plan",
                amount_paid=1999.0,
                status="paid",
                access_expires_at=datetime.now(timezone.utc) + timedelta(days=400),
            )
        )
        db_session.commit()
        with _client(db_session, user) as client:
            body = client.get("/api/subscriptions/me").json()
            assert body["access_state"] == "active"
            assert body["plan_id"] == "beginner-48w"
            assert body["amount"] == 1999.0

    def test_cancel_active_subscription(self, db_session):
        user = _user(db_session)
        with _client(db_session, user) as client:
            client.post(
                "/api/subscriptions/select-plan", json={"plan_id": "beginner-24w"}
            )
            client.post("/api/subscriptions/start-trial")
            res = client.post("/api/subscriptions/cancel")
            assert res.status_code == 200
            assert res.json()["access_state"] == "cancelled"

    def test_cancel_without_subscription_409(self, db_session):
        user = _user(db_session)
        with _client(db_session, user) as client:
            res = client.post("/api/subscriptions/cancel")
            assert res.status_code == 409
            assert res.json()["detail"]["code"] == "not_cancellable"

    def test_mock_purchase_410_when_flag_off(self, db_session):
        user = _user(db_session)
        with _client(db_session, user) as client:
            res = client.post(
                "/api/subscriptions/purchase", json={"plan_id": "beginner-24w"}
            )
            assert res.status_code == 410
            assert res.json()["detail"]["code"] == "mock_purchase_disabled"


class TestAuthMeAccessFields:
    def _auth_me_client(self, db, user: User) -> TestClient:
        from app.modules.auth.routes import router as auth_router

        app = FastAPI()
        # main.py mounts the auth router under /auth.
        app.include_router(auth_router, prefix="/auth")
        app.dependency_overrides[get_db] = lambda: db
        app.dependency_overrides[get_current_user] = lambda: user
        return TestClient(app)

    def test_auth_me_includes_access_fields(self, db_session):
        user = _user(db_session)
        with self._auth_me_client(db_session, user) as client:
            body = client.get("/auth/me").json()
            assert body["access_state"] == "verified"
            assert body["subscription_status"] is None
            assert body["plan_id"] is None
            assert body["trial_ends_at"] is None
            assert body["days_remaining"] is None

    def test_auth_me_days_remaining_during_trial(self, db_session):
        user = _user(db_session)
        with _client(db_session, user) as sub_client:
            sub_client.post(
                "/api/subscriptions/select-plan", json={"plan_id": "beginner-24w"}
            )
            sub_client.post("/api/subscriptions/start-trial")
        with self._auth_me_client(db_session, user) as client:
            body = client.get("/auth/me").json()
            assert body["access_state"] == "trial"
            assert body["days_remaining"] == 7
            assert body["plan_id"] == "beginner-24w"
            assert body["trial_ends_at"] is not None
