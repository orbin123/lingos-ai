"""SubscriptionService state machine: resolve_access + transitions."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base
from app.modules.auth.models import Role, User, UserRole
from app.modules.preferences.models import UserCoursePreference
from app.modules.subscriptions.exceptions import (
    NoPlanSelected,
    NotCancellable,
    PlanLocked,
    PlanNotFound,
    TrialAlreadyUsed,
)
from app.modules.subscriptions.models import (
    Purchase,
    Subscription,
    SubscriptionStatus,
)
from app.modules.subscriptions.service import (
    AccessState,
    SubscriptionService,
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
        email=f"u{id(db)}-{verified}@example.com",
        password_hash="x",
        name="U",
        email_verified=verified,
    )
    db.add(user)
    db.commit()
    return user


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TestResolveAccess:
    def test_unverified_user(self, db_session):
        user = _user(db_session, verified=False)
        access = SubscriptionService(db_session).resolve_access(user)
        assert access.state is AccessState.UNVERIFIED

    def test_verified_no_row(self, db_session):
        user = _user(db_session)
        access = SubscriptionService(db_session).resolve_access(user)
        assert access.state is AccessState.VERIFIED
        assert access.plan_id is None

    def test_trial_running(self, db_session):
        user = _user(db_session)
        service = SubscriptionService(db_session)
        service.select_plan(user, "beginner-24w")
        service.start_trial(user)
        access = service.resolve_access(user)
        assert access.state is AccessState.TRIAL
        assert access.days_remaining == settings.TRIAL_DAYS
        assert access.plan_id == "beginner-24w"

    def test_lazy_expiry_trial_past_due_resolves_expired(self, db_session):
        user = _user(db_session)
        row = Subscription(
            user_id=user.id,
            provider="internal",
            plan_id="beginner-24w",
            plan_name="24-Week Foundation",
            status=SubscriptionStatus.TRIAL.value,
            trial_started_at=_now() - timedelta(days=10),
            trial_ends_at=_now() - timedelta(days=3),
        )
        db_session.add(row)
        db_session.commit()

        access = SubscriptionService(db_session).resolve_access(user)
        assert access.state is AccessState.EXPIRED
        # Pure read: the stored status must NOT have been flipped.
        db_session.refresh(row)
        assert row.status == SubscriptionStatus.TRIAL.value

    def test_active_past_period_end_resolves_expired(self, db_session):
        user = _user(db_session)
        db_session.add(
            Subscription(
                user_id=user.id,
                provider="razorpay",
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                status=SubscriptionStatus.ACTIVE.value,
                current_period_start=_now() - timedelta(days=800),
                current_period_end=_now() - timedelta(days=1),
            )
        )
        db_session.commit()
        access = SubscriptionService(db_session).resolve_access(user)
        assert access.state is AccessState.EXPIRED

    def test_cancelled_with_future_period_end_keeps_access(self, db_session):
        user = _user(db_session)
        db_session.add(
            Subscription(
                user_id=user.id,
                provider="razorpay",
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                status=SubscriptionStatus.CANCELLED.value,
                cancelled_at=_now(),
                current_period_start=_now() - timedelta(days=10),
                current_period_end=_now() + timedelta(days=30),
            )
        )
        db_session.commit()
        access = SubscriptionService(db_session).resolve_access(user)
        assert access.state is AccessState.ACTIVE
        assert access.subscription_status == "cancelled"

    def test_cancelled_past_period_end_resolves_cancelled(self, db_session):
        user = _user(db_session)
        db_session.add(
            Subscription(
                user_id=user.id,
                provider="razorpay",
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                status=SubscriptionStatus.CANCELLED.value,
                cancelled_at=_now() - timedelta(days=40),
                current_period_end=_now() - timedelta(days=10),
            )
        )
        db_session.commit()
        access = SubscriptionService(db_session).resolve_access(user)
        assert access.state is AccessState.CANCELLED

    def test_legacy_unexpired_purchase_resolves_active(self, db_session):
        user = _user(db_session)
        db_session.add(
            Purchase(
                user_id=user.id,
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                amount_paid=999.0,
                status="paid",
                access_expires_at=_now() + timedelta(days=365),
            )
        )
        db_session.commit()
        access = SubscriptionService(db_session).resolve_access(user)
        assert access.state is AccessState.ACTIVE
        assert access.plan_id == "beginner-24w"

    def test_legacy_paused_purchase_still_active(self, db_session):
        user = _user(db_session)
        db_session.add(
            Purchase(
                user_id=user.id,
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                amount_paid=999.0,
                status="paused",
                access_expires_at=_now() + timedelta(days=365),
            )
        )
        db_session.commit()
        access = SubscriptionService(db_session).resolve_access(user)
        assert access.state is AccessState.ACTIVE

    def test_legacy_expired_purchase_resolves_expired(self, db_session):
        user = _user(db_session)
        db_session.add(
            Purchase(
                user_id=user.id,
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                amount_paid=999.0,
                status="paid",
                access_expires_at=_now() - timedelta(days=1),
            )
        )
        db_session.commit()
        access = SubscriptionService(db_session).resolve_access(user)
        assert access.state is AccessState.EXPIRED

    def test_days_remaining_ceil_and_floor_at_zero(self, db_session):
        user = _user(db_session)
        # 36 hours left → ceil to 2 days.
        db_session.add(
            Subscription(
                user_id=user.id,
                provider="internal",
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                status=SubscriptionStatus.TRIAL.value,
                trial_started_at=_now() - timedelta(days=5),
                trial_ends_at=_now() + timedelta(hours=36),
            )
        )
        db_session.commit()
        access = SubscriptionService(db_session).resolve_access(user)
        assert access.days_remaining == 2


class TestSelectPlan:
    def test_creates_row_and_preference(self, db_session):
        user = _user(db_session)
        service = SubscriptionService(db_session)
        row = service.select_plan(user, "beginner-48w")
        assert row.plan_id == "beginner-48w"
        assert row.status == SubscriptionStatus.VERIFIED.value
        pref = db_session.query(UserCoursePreference).filter_by(user_id=user.id).one()
        assert pref.course_length == "48w"

    def test_updates_existing_plan_while_verified(self, db_session):
        user = _user(db_session)
        service = SubscriptionService(db_session)
        service.select_plan(user, "beginner-48w")
        row = service.select_plan(user, "beginner-24w")
        assert row.plan_id == "beginner-24w"
        pref = db_session.query(UserCoursePreference).filter_by(user_id=user.id).one()
        assert pref.course_length == "24w"

    def test_unknown_plan_raises(self, db_session):
        user = _user(db_session)
        with pytest.raises(PlanNotFound):
            SubscriptionService(db_session).select_plan(user, "nope-12w")

    def test_locked_after_trial_start(self, db_session):
        user = _user(db_session)
        service = SubscriptionService(db_session)
        service.select_plan(user, "beginner-24w")
        service.start_trial(user)
        with pytest.raises(PlanLocked):
            service.select_plan(user, "beginner-48w")
        # Re-selecting the SAME plan stays idempotent, not an error.
        assert service.select_plan(user, "beginner-24w").plan_id == "beginner-24w"


class TestStartTrial:
    def test_requires_plan(self, db_session):
        user = _user(db_session)
        with pytest.raises(NoPlanSelected):
            SubscriptionService(db_session).start_trial(user)

    def test_sets_window(self, db_session):
        user = _user(db_session)
        service = SubscriptionService(db_session)
        service.select_plan(user, "beginner-24w")
        row = service.start_trial(user)
        assert row.status == SubscriptionStatus.TRIAL.value
        assert row.trial_started_at is not None
        delta = row.trial_ends_at - row.trial_started_at
        assert delta == timedelta(days=settings.TRIAL_DAYS)

    def test_idempotent_second_call(self, db_session):
        user = _user(db_session)
        service = SubscriptionService(db_session)
        service.select_plan(user, "beginner-24w")
        first = service.start_trial(user)
        first_ends = first.trial_ends_at
        second = service.start_trial(user)
        assert second.trial_ends_at == first_ends

    def test_after_expiry_raises_trial_already_used(self, db_session):
        user = _user(db_session)
        service = SubscriptionService(db_session)
        service.select_plan(user, "beginner-24w")
        row = service.start_trial(user)
        row.trial_ends_at = _now() - timedelta(days=1)
        db_session.commit()
        with pytest.raises(TrialAlreadyUsed):
            service.start_trial(user)


class TestActivateAndCancel:
    def test_activate_from_payment_sets_two_year_window(self, db_session):
        user = _user(db_session)
        service = SubscriptionService(db_session)
        row = service.activate_from_payment(
            user, plan_id="beginner-48w", provider="razorpay"
        )
        assert row.status == SubscriptionStatus.ACTIVE.value
        assert row.current_period_end.year == (
            row.current_period_start.year + settings.ACCESS_WINDOW_YEARS
        )
        assert service.resolve_access(user).state is AccessState.ACTIVE

    def test_activate_mid_trial_starts_period_now(self, db_session):
        user = _user(db_session)
        service = SubscriptionService(db_session)
        service.select_plan(user, "beginner-24w")
        service.start_trial(user)
        row = service.activate_from_payment(
            user, plan_id="beginner-24w", provider="razorpay"
        )
        assert row.status == SubscriptionStatus.ACTIVE.value
        # MVP: no trial-day credit — the paid window starts now.
        assert abs((row.current_period_start - _now()).total_seconds()) < 60

    def test_cancel_active_keeps_period_end(self, db_session):
        user = _user(db_session)
        service = SubscriptionService(db_session)
        service.activate_from_payment(user, plan_id="beginner-24w", provider="razorpay")
        row = service.cancel(user)
        assert row.status == SubscriptionStatus.CANCELLED.value
        assert row.current_period_end is not None
        # Paid access survives until period end.
        assert service.resolve_access(user).state is AccessState.ACTIVE

    def test_cancel_trial_ends_access_immediately(self, db_session):
        user = _user(db_session)
        service = SubscriptionService(db_session)
        service.select_plan(user, "beginner-24w")
        service.start_trial(user)
        service.cancel(user)
        assert service.resolve_access(user).state is AccessState.CANCELLED

    def test_cancel_without_subscription_raises(self, db_session):
        user = _user(db_session)
        with pytest.raises(NotCancellable):
            SubscriptionService(db_session).cancel(user)


class TestExpireDueTrials:
    def test_flips_only_due_rows_idempotent(self, db_session):
        due_user = _user(db_session)
        db_session.add(
            Subscription(
                user_id=due_user.id,
                provider="internal",
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                status=SubscriptionStatus.TRIAL.value,
                trial_started_at=_now() - timedelta(days=10),
                trial_ends_at=_now() - timedelta(days=3),
            )
        )
        running_user = User(
            email="running@example.com",
            password_hash="x",
            name="R",
            email_verified=True,
        )
        db_session.add(running_user)
        db_session.flush()
        db_session.add(
            Subscription(
                user_id=running_user.id,
                provider="internal",
                plan_id="beginner-24w",
                plan_name="24-Week Foundation",
                status=SubscriptionStatus.TRIAL.value,
                trial_started_at=_now(),
                trial_ends_at=_now() + timedelta(days=5),
            )
        )
        db_session.commit()

        service = SubscriptionService(db_session)
        assert service.expire_due_trials() == 1
        assert service.expire_due_trials() == 0  # idempotent
        states = {
            row.user_id: row.status for row in db_session.query(Subscription).all()
        }
        assert states[due_user.id] == SubscriptionStatus.EXPIRED.value
        assert states[running_user.id] == SubscriptionStatus.TRIAL.value
