"""App review models — learners rating the application itself."""

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import IDMixin, TimestampMixin


class AppReview(Base, IDMixin, TimestampMixin):
    """A learner's review of the LingosAI application.

    Distinct from per-session feedback: this is the user reviewing the product.
    Collected by the in-app feedback prompt (see ``app.modules.feedback``); the
    admin "User Reviews" list reads these rows.

    The three structured text fields (``positive_feedback`` / ``improvement_feedback``
    / ``bug_report``) are what the prompt collects. ``title``/``body`` are kept and
    synthesised from them so legacy readers and the older POST /api/reviews path
    keep working.
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

    # Structured feedback collected by the in-app prompt.
    positive_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    improvement_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    bug_report: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Context snapshot captured at submission time (for analytics / cohorting).
    task_count_when_submitted: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    days_since_signup: Mapped[int | None] = mapped_column(Integer, nullable=True)
    app_version: Mapped[str | None] = mapped_column(String(40), nullable=True)

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<AppReview(user_id={self.user_id}, rating={self.rating})>"
