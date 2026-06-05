"""Billing, subscription, and mock purchase records."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import CreatedAtMixin, IDMixin, TimestampMixin


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
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    trial_ends_at: Mapped[datetime | None] = mapped_column(
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
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
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
