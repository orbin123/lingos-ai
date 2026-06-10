"""Billing, subscription, and mock purchase records."""

from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import CreatedAtMixin, IDMixin, TimestampMixin


class SubscriptionStatus(str, Enum):
    """Entitlement state machine values stored in Subscription.status.

    Kept as a Python-level enum over a plain String column (not a DB enum)
    for SQLite test compatibility and to avoid ALTER TYPE migrations when
    reserved states activate. UNVERIFIED/VERIFIED-without-a-row are derived
    from User.email_verified; a stored row starts at TRIAL or later.
    """

    VERIFIED = "verified"
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"  # reserved for recurring billing


class Purchase(Base, IDMixin, TimestampMixin):
    """Current one-time course purchase for a user.

    Payments are mocked, but the app records the selected plan and amount paid
    so settings can show the user's actual purchase details.
    """

    __tablename__ = "purchases"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    plan_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    plan_name: Mapped[str] = mapped_column(String(120), nullable=False)
    amount_paid: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
        server_default="INR",
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="paid",
        server_default="paid",
        index=True,
    )
    # A one-time course purchase grants a fixed access window (2 years from the
    # purchase date). Stored explicitly rather than computed so admins can
    # extend/override per user and so "expired" is queryable in SQL.
    access_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<Purchase(user_id={self.user_id}, plan_id={self.plan_id!r})>"


class Subscription(Base, IDMixin, TimestampMixin):
    """Provider-backed subscription record.

    Only provider identifiers are stored. Card details never belong in this
    application database.
    """

    __tablename__ = "subscriptions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    provider_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )
    plan_name: Mapped[str] = mapped_column(String(120), nullable=False)
    # Catalog key (e.g. "beginner-24w"); mirrors PLAN_CATALOG.
    plan_id: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )
    # A SubscriptionStatus value. String column + Python enum (see above).
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    trial_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    user = relationship("User")

    __table_args__ = (
        # "One current subscription per user" is service-enforced; this index
        # makes the lookup cheap.
        Index("ix_subscriptions_user_status", "user_id", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"<Subscription(user_id={self.user_id}, provider={self.provider!r}, "
            f"status={self.status!r})>"
        )


class Payment(Base, IDMixin, CreatedAtMixin):
    """Provider payment record without card details."""

    __tablename__ = "payments"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_payment_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )
    # Razorpay order id the payment belongs to. The checkout signature is
    # verified against it and then discarded — never stored.
    provider_order_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    method: Mapped[str | None] = mapped_column(String(40), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    user = relationship("User")

    def __repr__(self) -> str:
        return (
            f"<Payment(user_id={self.user_id}, provider={self.provider!r}, "
            f"status={self.status!r})>"
        )


class PaymentEvent(Base, IDMixin, CreatedAtMixin):
    """Raw provider webhook events — idempotency guard + audit trail.

    event_id is unique: a duplicate webhook delivery fails the insert and is
    dropped without reprocessing.
    """

    __tablename__ = "payment_events"

    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<PaymentEvent(provider={self.provider!r}, "
            f"event_id={self.event_id!r}, event_type={self.event_type!r})>"
        )
