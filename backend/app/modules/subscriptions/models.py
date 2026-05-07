"""Mock one-time course purchase records."""

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import IDMixin, TimestampMixin


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

    def __repr__(self) -> str:
        return f"<Purchase(user_id={self.user_id}, plan_id={self.plan_id!r})>"
