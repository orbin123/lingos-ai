"""Audit log of feedback prompts shown to users.

One row per time the prompt is actually displayed. ``dismissed``/``submitted``
are set when the user acts on it, which drives the cooldown windows and the
admin submission-rate metric.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import CreatedAtMixin, IDMixin


class FeedbackPromptLog(Base, IDMixin, CreatedAtMixin):
    """One row per displayed feedback prompt."""

    __tablename__ = "feedback_prompt_logs"
    __table_args__ = (
        Index("ix_feedback_prompt_user_created", "user_id", "created_at"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prompted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    dismissed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    submitted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    # TASK_MILESTONE | DAY_3 | FEEDBACK_REPORTS | TIME_SPENT
    trigger_type: Mapped[str] = mapped_column(String(40), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<FeedbackPromptLog(user_id={self.user_id}, "
            f"trigger={self.trigger_type!r}, submitted={self.submitted}, "
            f"dismissed={self.dismissed})>"
        )
