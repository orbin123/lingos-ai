"""Admin subscribers view reads stored subscription state, not derived trials."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.modules.admin.repository import AdminRepository
from app.modules.auth.models import Role, User, UserRole
from app.modules.subscriptions.models import (
    Purchase,
    Subscription,
    SubscriptionStatus,
)


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


def _user(db, email: str, *, verified: bool = True) -> User:
    user = User(email=email, password_hash="x", name=email, email_verified=verified)
    db.add(user)
    db.commit()
    return user


class TestStoredTrials:
    def test_trial_user_listed_from_stored_subscription(self, db_session):
        user = _user(db_session, "trial@example.com")
        started = _now() - timedelta(days=2)
        ends = _now() + timedelta(days=5)
        db_session.add(
            Subscription(
                user_id=user.id,
                provider="internal",
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                status=SubscriptionStatus.TRIAL.value,
                trial_started_at=started,
                trial_ends_at=ends,
            )
        )
        db_session.commit()

        overview = AdminRepository(db_session).list_subscribers()
        assert overview.subscribers == []
        (item,) = overview.trials
        assert item.status == "trial"
        assert item.trial_started_at is not None
        assert item.trial_ends_at is not None

    def test_expired_trial_listed_expired(self, db_session):
        user = _user(db_session, "ended@example.com")
        db_session.add(
            Subscription(
                user_id=user.id,
                provider="internal",
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                status=SubscriptionStatus.TRIAL.value,
                trial_started_at=_now() - timedelta(days=10),
                trial_ends_at=_now() - timedelta(days=3),
            )
        )
        db_session.commit()
        (item,) = AdminRepository(db_session).list_subscribers().trials
        assert item.status == "expired"

    def test_unverified_user_flagged(self, db_session):
        _user(db_session, "unverified@example.com", verified=False)
        (item,) = AdminRepository(db_session).list_subscribers().trials
        assert item.status == "unverified"
        assert item.email_verified is False
        assert item.trial_ends_at is None

    def test_verified_no_trial_listed_not_started(self, db_session):
        _user(db_session, "fresh@example.com")
        (item,) = AdminRepository(db_session).list_subscribers().trials
        assert item.status == "not_started"
        assert item.trial_ends_at is None

    def test_paid_subscription_listed_as_subscriber(self, db_session):
        user = _user(db_session, "paid@example.com")
        db_session.add(
            Subscription(
                user_id=user.id,
                provider="razorpay",
                plan_id="beginner-48w",
                plan_name="48-Week Plan",
                status=SubscriptionStatus.ACTIVE.value,
                current_period_start=_now(),
                current_period_end=_now() + timedelta(days=700),
            )
        )
        db_session.commit()

        overview = AdminRepository(db_session).list_subscribers()
        assert overview.trials == []
        (item,) = overview.subscribers
        assert item.status == "active"
        assert item.plan_id == "beginner-48w"
        assert item.amount_paid == 1999.0

    def test_legacy_purchaser_still_in_subscribers(self, db_session):
        user = _user(db_session, "legacy@example.com")
        db_session.add(
            Purchase(
                user_id=user.id,
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                amount_paid=999.0,
                status="paid",
                access_expires_at=_now() + timedelta(days=300),
            )
        )
        db_session.commit()

        overview = AdminRepository(db_session).list_subscribers()
        assert overview.trials == []
        (item,) = overview.subscribers
        assert item.status == "active"
        assert item.plan_id == "beginner-24w"

    def test_cancelled_paid_subscription_shows_cancelled(self, db_session):
        user = _user(db_session, "cxl@example.com")
        db_session.add(
            Subscription(
                user_id=user.id,
                provider="razorpay",
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                status=SubscriptionStatus.CANCELLED.value,
                cancelled_at=_now(),
                current_period_start=_now() - timedelta(days=30),
                current_period_end=_now() + timedelta(days=600),
            )
        )
        db_session.commit()
        (item,) = AdminRepository(db_session).list_subscribers().subscribers
        assert item.status == "cancelled"
