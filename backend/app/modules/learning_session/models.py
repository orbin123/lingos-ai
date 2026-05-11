"""LearningSession — one chat-driven learning loop persisted in Postgres.

The frontend identifies a session by its UUID `session_id` (string in the
URL); internally we still keep an integer primary key from IDMixin.

`pre_generated_tasks` holds the LLM-generated task content that drives
the practice phase. `messages` is the full conversation log so a
WebSocket reconnect can replay history.
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import IDMixin, TimestampMixin


class LearningSession(Base, IDMixin, TimestampMixin):
    __tablename__ = "learning_sessions"

    session_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("user_enrollments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_task_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    phase: Mapped[str] = mapped_column(
        String(32), nullable=False, default="teaching"
    )
    topic: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    skill_name: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    user_level: Mapped[int] = mapped_column(nullable=False, default=5)
    pre_generated_tasks: Mapped[dict] = mapped_column(JSONB, nullable=False)
    task_queue: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    current_task_index: Mapped[int] = mapped_column(nullable=False, default=0)
    messages: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    user_submission: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    evaluation: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    feedback: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    understanding_confirmed: Mapped[bool] = mapped_column(nullable=False, default=False)

    def __repr__(self) -> str:
        return (
            f"<LearningSession(id={self.id}, session_id={self.session_id!r}, "
            f"phase={self.phase!r}, topic={self.topic!r})>"
        )
