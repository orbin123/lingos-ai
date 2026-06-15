"""Entitlement state machine — the single source of truth for access.

`resolve_access` is a pure read with lazy expiry: a trial whose
`trial_ends_at` has passed resolves EXPIRED even though the stored status
still says "trial". Stored statuses are only flipped by explicit
transitions (start_trial, activate_from_payment, cancel) and by the
`expire_due_trials` admin sweep — never as a side effect of a read, so
the guard path stays write-free.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum

from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.auth.models import User, UserProfile
from app.modules.auth.repository import UserProfileRepository
from app.modules.preferences.repository import UserCoursePreferenceRepository
from app.modules.subscriptions.catalog import PLAN_CATALOG, add_years
from app.modules.subscriptions.exceptions import (
    NoPlanSelected,
    NotCancellable,
    PlanLocked,
    PlanNotFound,
    PurchaseNotFound,
    TrialAlreadyUsed,
)
from app.modules.subscriptions.models import (
    Purchase,
    Subscription,
    SubscriptionStatus,
)
from app.modules.subscriptions.repository import SubscriptionRepository


class AccessState(str, Enum):
    """Effective access level — what the user may do right now (§2.3)."""

    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


PREMIUM_STATES = frozenset({AccessState.TRIAL, AccessState.ACTIVE})


@dataclass(frozen=True)
class AccessResolution:
    """The one access decision everything consumes (guard, /auth/me, admin)."""

    state: AccessState
    subscription_status: str | None = None  # raw stored status, may lag state
    plan_id: str | None = None
    plan_name: str | None = None
    trial_started_at: datetime | None = None
    trial_ends_at: datetime | None = None
    current_period_end: datetime | None = None
    days_remaining: int | None = None


def _as_aware(dt: datetime | None) -> datetime | None:
    """SQLite returns naive datetimes; treat stored values as UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _days_remaining(until: datetime | None, now: datetime) -> int | None:
    """Whole days until `until`, rounded up, floored at 0.

    Computed once here so the navbar pill, dashboard banner, and admin
    views can never disagree.
    """
    until = _as_aware(until)
    if until is None:
        return None
    seconds = (until - now).total_seconds()
    return max(0, math.ceil(seconds / 86400))


def resolve_effective_status(
    subscription: Subscription, now: datetime | None = None
) -> AccessState:
    """Lazy-expiry resolution of a stored subscription row.

    Exported separately so admin listings use the exact same rules as the
    premium guard.
    """
    now = now or datetime.now(timezone.utc)
    status = subscription.status
    trial_ends_at = _as_aware(subscription.trial_ends_at)
    period_end = _as_aware(subscription.current_period_end)

    if status == SubscriptionStatus.TRIAL.value:
        if trial_ends_at is not None and now <= trial_ends_at:
            return AccessState.TRIAL
        return AccessState.EXPIRED
    if status == SubscriptionStatus.ACTIVE.value:
        if period_end is None or now <= period_end:
            return AccessState.ACTIVE
        return AccessState.EXPIRED
    if status == SubscriptionStatus.CANCELLED.value:
        # Paid access survives cancellation until the period ends (§7.1).
        if period_end is not None and now <= period_end:
            return AccessState.ACTIVE
        return AccessState.CANCELLED
    if status == SubscriptionStatus.VERIFIED.value:
        return AccessState.VERIFIED
    # EXPIRED / PAST_DUE / anything unknown → no access.
    return AccessState.EXPIRED


class SubscriptionService:
    """Owns the entitlement state machine and its commits."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SubscriptionRepository(db)
        self.pref_repo = UserCoursePreferenceRepository(db)
        self.profile_repo = UserProfileRepository(db)

    # ── the one function everything calls ─────────────────────────────

    def resolve_access(self, user: User) -> AccessResolution:
        now = datetime.now(timezone.utc)

        if not user.email_verified:
            return AccessResolution(state=AccessState.UNVERIFIED)

        subscription = self.repo.get_for_user(user.id)
        if subscription is not None:
            return self._resolve_subscription(subscription, now)

        purchase = self.repo.get_purchase_for_user(user.id)
        if purchase is not None:
            return self._resolve_legacy_purchase(purchase, now)

        return AccessResolution(state=AccessState.VERIFIED)

    def _resolve_subscription(
        self, subscription: Subscription, now: datetime
    ) -> AccessResolution:
        state = resolve_effective_status(subscription, now)
        if state is AccessState.TRIAL:
            remaining = _days_remaining(subscription.trial_ends_at, now)
        elif state is AccessState.ACTIVE:
            remaining = _days_remaining(subscription.current_period_end, now)
        else:
            remaining = None
        return AccessResolution(
            state=state,
            subscription_status=subscription.status,
            plan_id=subscription.plan_id,
            plan_name=subscription.plan_name,
            trial_started_at=_as_aware(subscription.trial_started_at),
            trial_ends_at=_as_aware(subscription.trial_ends_at),
            current_period_end=_as_aware(subscription.current_period_end),
            days_remaining=remaining,
        )

    def _resolve_legacy_purchase(
        self, purchase: Purchase, now: datetime
    ) -> AccessResolution:
        # Pre-subscription one-time purchases. "paused" was always a
        # schedule-only flag (see routes.pause_course_access docstring),
        # never an access gate, so it still resolves ACTIVE.
        expires_at = _as_aware(purchase.access_expires_at)
        active = expires_at is None or now <= expires_at
        state = AccessState.ACTIVE if active else AccessState.EXPIRED
        return AccessResolution(
            state=state,
            subscription_status=purchase.status,
            plan_id=purchase.plan_id,
            plan_name=purchase.plan_name,
            current_period_end=expires_at,
            days_remaining=_days_remaining(expires_at, now) if active else None,
        )

    # ── transitions ───────────────────────────────────────────────────

    def select_plan(self, user: User, plan_id: str) -> Subscription:
        """Store the chosen plan pre-trial; locked once TRIAL/ACTIVE."""
        plan = PLAN_CATALOG.get(plan_id)
        if plan is None:
            raise PlanNotFound(plan_id)

        subscription = self.repo.get_for_user(user.id)
        if subscription is not None:
            state = resolve_effective_status(subscription)
            if state in PREMIUM_STATES or subscription.trial_started_at is not None:
                if subscription.plan_id != plan_id:
                    raise PlanLocked(plan_id)
                return subscription
            subscription.plan_id = plan_id
            subscription.plan_name = str(plan["name"])
        else:
            subscription = self.repo.get_or_create_for_user(
                user.id, plan_id=plan_id, plan_name=str(plan["name"])
            )

        preference = self.pref_repo.get_or_create_for_user(user.id)
        preference.course_length = str(plan["course_length"])

        self.db.commit()
        return subscription

    def start_trial(self, user: User) -> Subscription:
        """VERIFIED → TRIAL. One trial per user; idempotent while running."""
        subscription = self.repo.get_for_user(user.id)
        if subscription is None or not subscription.plan_id:
            raise NoPlanSelected()

        state = resolve_effective_status(subscription)
        if state in PREMIUM_STATES:
            return subscription  # already running — idempotent
        if subscription.trial_started_at is not None:
            raise TrialAlreadyUsed()

        now = datetime.now(timezone.utc)
        subscription.status = SubscriptionStatus.TRIAL.value
        subscription.trial_started_at = now
        subscription.trial_ends_at = now + timedelta(days=settings.TRIAL_DAYS)
        self.db.commit()
        return subscription

    def activate_from_payment(
        self,
        user: User,
        *,
        plan_id: str,
        provider: str,
        provider_payment_id: str | None = None,
    ) -> Subscription:
        """Any state → ACTIVE after a verified payment. Idempotent.

        MVP: the paid period starts now — remaining trial days are not
        credited (blueprint Appendix B #2).
        """
        plan = PLAN_CATALOG.get(plan_id)
        if plan is None:
            raise PlanNotFound(plan_id)

        now = datetime.now(timezone.utc)
        subscription = self.repo.get_or_create_for_user(
            user.id, plan_id=plan_id, plan_name=str(plan["name"])
        )
        if (
            subscription.status == SubscriptionStatus.ACTIVE.value
            and subscription.provider == provider
            and resolve_effective_status(subscription, now) is AccessState.ACTIVE
        ):
            return subscription  # duplicate webhook/verify — no-op

        subscription.provider = provider
        subscription.plan_id = plan_id
        subscription.plan_name = str(plan["name"])
        subscription.status = SubscriptionStatus.ACTIVE.value
        subscription.current_period_start = now
        # Paid access window is ACCESS_WINDOW_YEARS (2y), matching the legacy
        # Purchase promise — course length is curriculum, not an access cap.
        subscription.current_period_end = add_years(now, settings.ACCESS_WINDOW_YEARS)
        subscription.cancelled_at = None

        preference = self.pref_repo.get_or_create_for_user(user.id)
        preference.course_length = str(plan["course_length"])

        self.db.commit()
        return subscription

    def cancel(self, user: User) -> Subscription:
        """TRIAL/ACTIVE → CANCELLED. Paid access keeps current_period_end."""
        subscription = self.repo.get_for_user(user.id)
        if subscription is None:
            raise NotCancellable()
        state = resolve_effective_status(subscription)
        if state not in PREMIUM_STATES:
            raise NotCancellable()

        now = datetime.now(timezone.utc)
        if subscription.status == SubscriptionStatus.TRIAL.value:
            # A cancelled trial ends access immediately: drop the window.
            subscription.trial_ends_at = now
            subscription.current_period_end = None
        subscription.status = SubscriptionStatus.CANCELLED.value
        subscription.cancelled_at = now
        self.db.commit()
        return subscription

    # ── account / plan actions ────────────────────────────────────────

    def pause_course(self, user: User) -> Purchase:
        """Pause the learner's plan without changing purchase history.

        The status flip lives on `Purchase` only — it was always a
        schedule-only flag, never an access gate (see resolve_access /
        `_resolve_legacy_purchase`).
        """
        purchase = self.repo.get_purchase_for_user(user.id)
        if purchase is None:
            raise PurchaseNotFound()
        purchase.status = "paused"
        self.db.commit()
        self.db.refresh(purchase)
        return purchase

    def update_notifications(
        self, user: User, updates: dict[str, object]
    ) -> UserProfile:
        """Patch notification preferences, creating a default profile if none.

        `updates` is the request's set fields (model_dump(exclude_unset=True));
        None values are ignored so a partial PATCH only touches sent fields.
        """
        profile = self.profile_repo.get_by_user_id(user.id)
        if profile is None:
            profile = self.profile_repo.create_default(user.id)
        for field, value in updates.items():
            if value is not None:
                setattr(profile, field, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete_account(self, user: User) -> None:
        """Permanently delete the current account."""
        self.repo.delete_user(user)
        self.db.commit()

    # ── maintenance ───────────────────────────────────────────────────

    def expire_due_trials(self) -> int:
        """Flip stored status on trials past their end. Idempotent sweep.

        Lazy resolution already enforces expiry at request time; this only
        keeps stored statuses clean for admin reporting.
        """
        now = datetime.now(timezone.utc)
        rows = (
            self.db.query(Subscription)
            .filter(Subscription.status == SubscriptionStatus.TRIAL.value)
            .all()
        )
        flipped = 0
        for row in rows:
            ends_at = _as_aware(row.trial_ends_at)
            if ends_at is None or now > ends_at:
                row.status = SubscriptionStatus.EXPIRED.value
                flipped += 1
        if flipped:
            self.db.commit()
        return flipped
