"""require_active_access guard: per-state behavior + premium-route wiring."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.websockets import WebSocketDisconnect

from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.modules.auth.models import Role, User, UserRole
from app.modules.preferences.models import UserCoursePreference
from app.modules.subscriptions.dependencies import (
    WS_PAYMENT_REQUIRED,
    check_ws_access,
    require_active_access,
)
from app.modules.subscriptions.models import Purchase, Subscription, SubscriptionStatus


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
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _user(db, *, verified: bool = True, email: str = "g@example.com") -> User:
    user = User(email=email, password_hash="x", name="G", email_verified=verified)
    db.add(user)
    db.commit()
    return user


def _subscription(db, user: User, **overrides) -> Subscription:
    row = Subscription(
        user_id=user.id,
        provider="internal",
        plan_id="beginner-24w",
        plan_name="24-Week Foundation",
        status=SubscriptionStatus.TRIAL.value,
        trial_started_at=_now(),
        trial_ends_at=_now() + timedelta(days=7),
    )
    for key, value in overrides.items():
        setattr(row, key, value)
    db.add(row)
    db.commit()
    return row


class TestGuardStates:
    def test_trial_user_passes(self, db_session):
        user = _user(db_session)
        _subscription(db_session, user)
        assert require_active_access(current_user=user, db=db_session) is user

    def test_active_user_passes(self, db_session):
        user = _user(db_session)
        _subscription(
            db_session,
            user,
            status=SubscriptionStatus.ACTIVE.value,
            current_period_start=_now(),
            current_period_end=_now() + timedelta(days=700),
        )
        assert require_active_access(current_user=user, db=db_session) is user

    def test_unverified_403_email_unverified(self, db_session):
        user = _user(db_session, verified=False)
        with pytest.raises(HTTPException) as exc_info:
            require_active_access(current_user=user, db=db_session)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "email_unverified"

    def test_verified_403_trial_not_started(self, db_session):
        user = _user(db_session)
        with pytest.raises(HTTPException) as exc_info:
            require_active_access(current_user=user, db=db_session)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["code"] == "trial_not_started"

    def test_expired_402_subscription_expired(self, db_session):
        user = _user(db_session)
        _subscription(
            db_session,
            user,
            trial_started_at=_now() - timedelta(days=10),
            trial_ends_at=_now() - timedelta(days=3),
        )
        with pytest.raises(HTTPException) as exc_info:
            require_active_access(current_user=user, db=db_session)
        assert exc_info.value.status_code == 402
        assert exc_info.value.detail["code"] == "subscription_expired"

    def test_cancelled_402_subscription_cancelled(self, db_session):
        user = _user(db_session)
        _subscription(
            db_session,
            user,
            status=SubscriptionStatus.CANCELLED.value,
            cancelled_at=_now(),
            trial_started_at=None,
            trial_ends_at=None,
            current_period_end=None,
        )
        with pytest.raises(HTTPException) as exc_info:
            require_active_access(current_user=user, db=db_session)
        assert exc_info.value.status_code == 402
        assert exc_info.value.detail["code"] == "subscription_cancelled"

    def test_check_ws_access_mirrors_guard(self, db_session):
        trial_user = _user(db_session, email="ws-t@example.com")
        _subscription(db_session, trial_user)
        assert check_ws_access(trial_user, db_session) is True

        verified_user = _user(db_session, email="ws-v@example.com")
        assert check_ws_access(verified_user, db_session) is False


def _route_dependency_funcs(router, path: str, method: str = "POST"):
    for route in router.routes:
        if getattr(route, "path", None) == path and method in getattr(
            route, "methods", set()
        ):
            return [dep.call for dep in route.dependant.dependencies]
    raise AssertionError(f"route {path} not found")


class TestPremiumRouteWiring:
    """Every AI-spending route must declare the entitlement guard."""

    def test_sessions_routes_declare_guard(self):
        from app.modules.sessions.routes import router

        for path in (
            "/sessions/today/start-or-continue",
            "/sessions/start",
            "/sessions/start-today",
            "/sessions/{session_id}/activities/{sequence}/submit",
            "/sessions/{session_id}/complete",
            "/sessions/pronunciation-score",
        ):
            assert require_active_access in _route_dependency_funcs(
                router, path
            ), f"{path} missing require_active_access"

    def test_learning_routes_declare_guard(self):
        from app.modules.learning_session.router import rest_router

        for path in (
            "/learning/sessions/start",
            "/learning/sessions/{session_id}/restart",
        ):
            assert require_active_access in _route_dependency_funcs(
                rest_router, path
            ), f"{path} missing require_active_access"

    def test_transcribe_route_declares_guard(self):
        from app.modules.responses.routes import router

        assert require_active_access in _route_dependency_funcs(
            router, "/responses/transcribe-audio"
        )

    def test_a2z_audio_route_declares_guard(self):
        from app.modules.challenges.a2z_game.routes import router

        assert require_active_access in _route_dependency_funcs(
            router, "/challenges/a2z/rounds/{round_id}/audio-chunks"
        )

    def test_diagnosis_stays_verified_only(self):
        """Diagnosis is pre-trial: require_verified, never the premium guard."""
        from app.modules.diagnosis.routes import router as diagnosis_router
        from app.modules.auth.dependencies import require_verified

        router_deps = [dep.dependency for dep in diagnosis_router.dependencies]
        assert require_verified in router_deps
        assert require_active_access not in router_deps


class TestLearningWebSocket:
    def test_learning_ws_closes_4402_for_expired_user(self, db_session):
        from app.modules.learning_session.router import ws_router

        user = _user(db_session, email="ws-expired@example.com")
        _subscription(
            db_session,
            user,
            trial_started_at=_now() - timedelta(days=10),
            trial_ends_at=_now() - timedelta(days=3),
        )

        app = FastAPI()
        app.include_router(ws_router)
        app.dependency_overrides[get_db] = lambda: db_session
        token = create_access_token(data={"sub": str(user.id)})

        with TestClient(app) as client:
            with pytest.raises(WebSocketDisconnect) as exc_info:
                with client.websocket_connect(
                    f"/ws/learning/some-session?token={token}"
                ) as ws:
                    ws.receive_text()
        assert exc_info.value.code == WS_PAYMENT_REQUIRED
