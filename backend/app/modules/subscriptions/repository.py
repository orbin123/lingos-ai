"""Read/write helpers for subscription and billing rows. No business logic."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.models import User
from app.modules.subscriptions.models import (
    Purchase,
    Subscription,
    SubscriptionStatus,
)


class SubscriptionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ── read ──────────────────────────────────────────────────────────

    def get_for_user(self, user_id: int) -> Subscription | None:
        """Return the user's current subscription row.

        One-row-per-user is service-enforced; if historical duplicates ever
        exist, the newest row wins.
        """
        return self.db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.id.desc())
            .limit(1)
        ).scalar_one_or_none()

    def get_purchase_for_user(self, user_id: int) -> Purchase | None:
        """Legacy one-time purchase row (pre-subscription billing)."""
        return self.db.execute(
            select(Purchase).where(Purchase.user_id == user_id)
        ).scalar_one_or_none()

    # ── write ─────────────────────────────────────────────────────────

    def delete_user(self, user: User) -> None:
        """Remove a user row (account deletion). Caller owns the commit."""
        self.db.delete(user)

    # ── upsert ────────────────────────────────────────────────────────

    def get_or_create_for_user(
        self,
        user_id: int,
        *,
        plan_id: str,
        plan_name: str,
    ) -> Subscription:
        """Return the user's subscription row, creating a pre-trial one if
        missing. Concurrent creates resolved via flush + re-read."""
        existing = self.get_for_user(user_id)
        if existing is not None:
            return existing

        row = Subscription(
            user_id=user_id,
            provider="internal",
            plan_id=plan_id,
            plan_name=plan_name,
            status=SubscriptionStatus.VERIFIED.value,
        )
        self.db.add(row)
        try:
            self.db.flush()
        except IntegrityError:
            self.db.rollback()
            existing = self.get_for_user(user_id)
            if existing is None:
                raise
            return existing
        return row
