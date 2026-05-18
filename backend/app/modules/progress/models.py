"""Progress tracking — append-only log of skill score changes, plus points-based tracking."""

from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.mixins import CreatedAtMixin, IDMixin, TimestampMixin


class ProgressLog(Base, IDMixin, CreatedAtMixin):
    """
    One row per skill-score change. Append-only — never updated, never deleted.

    Used to:
      - Power the "score over time" line chart
      - Audit how a user's scores evolved
      - Rebuild UserSkillScore if it ever gets corrupted
    """

    __tablename__ = "progress_logs"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    score: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False)
    # Optional context — link back to the task that caused this change
    user_task_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_tasks.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<ProgressLog(user_id={self.user_id}, skill_id={self.skill_id}, "
            f"score={self.score}, at={self.created_at})>"
        )


class SkillPoints(Base, IDMixin, TimestampMixin):
    """Points-based tracking for gamification (0–10000 = 0–10.0).

    Mutable state table — points and display_score are updated on every
    relevant task. Lives alongside UserSkillScore (WMA-based).

    One row per (user, skill) pair.
    """

    __tablename__ = "skill_points"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    points: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3000
    )
    display_score: Mapped[float] = mapped_column(
        Numeric(3, 1), nullable=False, default=3.0
    )

    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skill_points"),
    )

    def __repr__(self) -> str:
        return (
            f"<SkillPoints(user_id={self.user_id}, skill_id={self.skill_id}, "
            f"points={self.points})>"
        )


class SkillPointsLog(Base, IDMixin, CreatedAtMixin):
    """Append-only log of points earned per task (parallel to ProgressLog).

    Useful for:
      - "You earned +55 points!" notifications
      - Audit trail of point gains
      - Understanding which tasks were most rewarding
    """

    __tablename__ = "skill_points_logs"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    points_earned: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(100), nullable=False)
    user_task_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_tasks.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    # New in Phase 3: link a points entry to its source `daily_sessions` row.
    # Nullable so legacy entries (written via the WMA path) remain valid.
    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("daily_sessions.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<SkillPointsLog(user_id={self.user_id}, skill_id={self.skill_id}, "
            f"earned={self.points_earned})>"
        )