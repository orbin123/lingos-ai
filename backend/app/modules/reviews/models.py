"""App review models — learners rating the application itself."""

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import IDMixin, TimestampMixin


class AppReview(Base, IDMixin, TimestampMixin):
    """A learner's review of the LingosAI application.

    Distinct from per-session feedback: this is the user reviewing the product.
    The user-facing submission UI is added later; the admin list reads these.
    """

    __tablename__ = "app_reviews"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1–5
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    # "published" by default; room for "hidden"/"flagged" moderation later.
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="published",
        server_default="published",
        index=True,
    )

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<AppReview(user_id={self.user_id}, rating={self.rating})>"
