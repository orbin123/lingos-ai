"""Admin monitoring models."""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import CreatedAtMixin, IDMixin, TimestampMixin


class AdminAuditLog(Base, IDMixin, CreatedAtMixin):
    """Append-only record of important admin actions."""

    __tablename__ = "admin_audit_logs"

    admin_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_id: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    old_value: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    new_value: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)

    admin_user = relationship("User")


class AIRequestLog(Base, IDMixin, CreatedAtMixin):
    """Append-only operational log for AI provider calls."""

    __tablename__ = "ai_request_logs"

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    trace_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    input_tokens: Mapped[int | None] = mapped_column(nullable=True)
    output_tokens: Mapped[int | None] = mapped_column(nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(120), nullable=True)

    user = relationship("User")


class FeedbackReview(Base, IDMixin, TimestampMixin):
    """Admin review annotation for a single piece of learner-facing feedback.

    Feedback comes in two shapes that live in different tables:
      - "specific" → `activity_feedback.id`  (per-activity feedback)
      - "rag"      → `session_scorecards.id`  (session-level Coach's Note)

    This table is a polymorphic side-car keyed by (feedback_type, feedback_id)
    so the append-only feedback tables stay untouched. A row is created lazily
    the first time an admin reviews a target; absence ⇒ status "pending".
    """

    __tablename__ = "feedback_reviews"
    __table_args__ = (
        UniqueConstraint(
            "feedback_type", "feedback_id", name="uq_feedback_review_target"
        ),
    )

    # "specific" | "rag" — which source table `feedback_id` points at.
    feedback_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    # No hard FK: the id targets one of two tables depending on feedback_type.
    feedback_id: Mapped[int] = mapped_column(nullable=False, index=True)
    # "pending" | "approved" | "flagged" | "fixed"
    review_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )
    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    reviewer = relationship("User")
