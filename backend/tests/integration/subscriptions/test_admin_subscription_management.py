"""Admin Phase 5: status filter, subscription PATCH, trial sweep, payments."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.modules.admin.models import AdminAuditLog
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import SubscriptionAdminUpdate
from app.modules.admin.service import AdminService
from app.modules.auth.models import Role, User, UserRole
from app.modules.subscriptions.models import (
    Payment,
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
            Payment.__table__,
            AdminAuditLog.__table__,
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


def _trial(db, user: User, *, ends_in_days: int) -> Subscription:
    row = Subscription(
        user_id=user.id,
        provider="internal",
        plan_id="beginner-24w",
        plan_name="24-Week Foundation",
        status=SubscriptionStatus.TRIAL.value,
        trial_started_at=_now() + timedelta(days=ends_in_days - 7),
        trial_ends_at=_now() + timedelta(days=ends_in_days),
    )
    db.add(row)
    db.commit()
    return row


class TestStatusFilter:
    def test_filters_trials_by_status(self, db_session):
        _trial(db_session, _user(db_session, "t@example.com"), ends_in_days=5)
        _trial(db_session, _user(db_session, "e@example.com"), ends_in_days=-2)
        _user(db_session, "fresh@example.com")

        repo = AdminRepository(db_session)
        assert [t.status for t in repo.list_subscribers(status="trial").trials] == [
            "trial"
        ]
        assert [t.status for t in repo.list_subscribers(status="expired").trials] == [
            "expired"
        ]
        assert [
            t.status for t in repo.list_subscribers(status="not_started").trials
        ] == ["not_started"]
        # No filter → everyone.
        assert len(repo.list_subscribers().trials) == 3

    def test_filters_subscribers_by_status(self, db_session):
        active = _user(db_session, "a@example.com")
        db_session.add(
            Subscription(
                user_id=active.id,
                provider="razorpay",
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                status=SubscriptionStatus.ACTIVE.value,
                current_period_start=_now(),
                current_period_end=_now() + timedelta(days=700),
            )
        )
        db_session.commit()

        repo = AdminRepository(db_session)
        assert len(repo.list_subscribers(status="active").subscribers) == 1
        assert len(repo.list_subscribers(status="cancelled").subscribers) == 0


class TestSubscriptionAdminUpdate:
    def test_extends_trial_with_audit(self, db_session):
        user = _user(db_session, "extend@example.com")
        row = _trial(db_session, user, ends_in_days=-1)  # expired
        actor = _user(db_session, "admin@example.com")

        new_end = _now() + timedelta(days=14)
        result = AdminService(db_session).update_subscriber_subscription(
            user_id=user.id,
            update=SubscriptionAdminUpdate(trial_ends_at=new_end, status="trial"),
            actor=actor,
        )
        assert result is not None
        db_session.refresh(row)
        assert row.trial_ends_at.replace(tzinfo=timezone.utc) == new_end
        audit = (
            db_session.query(AdminAuditLog)
            .filter_by(action="subscription.admin_update")
            .one()
        )
        assert audit.old_value is not None  # row existed before

    def test_grants_trial_when_no_row(self, db_session):
        user = _user(db_session, "grant@example.com")
        actor = _user(db_session, "admin2@example.com")

        result = AdminService(db_session).update_subscriber_subscription(
            user_id=user.id,
            update=SubscriptionAdminUpdate(
                status="trial",
                trial_started_at=_now(),
                trial_ends_at=_now() + timedelta(days=7),
            ),
            actor=actor,
        )
        assert result is not None
        assert result.status == "trial"
        row = db_session.query(Subscription).filter_by(user_id=user.id).one()
        assert row.provider == "admin"
        assert row.trial_ends_at is not None

    def test_unknown_user_returns_none(self, db_session):
        actor = _user(db_session, "admin3@example.com")
        result = AdminService(db_session).update_subscriber_subscription(
            user_id=99999,
            update=SubscriptionAdminUpdate(status="trial"),
            actor=actor,
        )
        assert result is None

    def test_invalid_status_raises(self, db_session):
        user = _user(db_session, "bad@example.com")
        actor = _user(db_session, "admin4@example.com")
        with pytest.raises(ValueError):
            AdminService(db_session).update_subscriber_subscription(
                user_id=user.id,
                update=SubscriptionAdminUpdate(status="bogus"),
                actor=actor,
            )


class TestExpireDueTrialsAdmin:
    def test_sweep_flips_due_rows_and_audits(self, db_session):
        _trial(db_session, _user(db_session, "due@example.com"), ends_in_days=-3)
        _trial(db_session, _user(db_session, "live@example.com"), ends_in_days=4)
        actor = _user(db_session, "sweeper@example.com")

        service = AdminService(db_session)
        assert service.expire_due_trials(actor=actor) == 1
        assert service.expire_due_trials(actor=actor) == 0  # idempotent
        assert (
            db_session.query(AdminAuditLog)
            .filter_by(action="subscription.expire_due_trials")
            .count()
            == 2
        )


class TestPaymentsView:
    def test_payments_include_order_id_and_failure(self, db_session):
        user = _user(db_session, "payer@example.com")
        db_session.add(
            Payment(
                user_id=user.id,
                provider="razorpay",
                provider_payment_id="pay_abcdef123456",
                provider_order_id="order_abcdef123456",
                amount=999.0,
                currency="INR",
                status="failed",
                method="card",
                failure_reason="Card declined",
            )
        )
        db_session.commit()

        (payment,) = AdminRepository(db_session).list_payments()
        # Provider ids are masked in admin views.
        assert payment.provider_order_id == "orde...3456"
        assert payment.method == "card"
        assert payment.failure_reason == "Card declined"
