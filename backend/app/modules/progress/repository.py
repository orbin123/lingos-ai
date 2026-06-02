"""Data access for ProgressLog — append-only history of skill score changes, plus points-based tracking."""

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.modules.progress.models import ProgressLog, SkillPoints, SkillPointsLog


class ProgressLogRepository:
    """All DB access for ProgressLog rows.

    Append-only by design: no update(), no delete(). The full history
    of every score change is kept forever — used for charts and audits.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # Reads
    def list_for_user_skill(
        self,
        *,
        user_id: int,
        skill_id: int,
        days: int,
    ) -> list[ProgressLog]:
        """Return history rows for one (user, skill) within the last N days.

        Ordered oldest → newest, so the line chart can render left to right
        without the frontend having to sort.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            self.db.query(ProgressLog)
            .filter(
                ProgressLog.user_id == user_id,
                ProgressLog.skill_id == skill_id,
                ProgressLog.created_at >= cutoff,
            )
            .order_by(ProgressLog.created_at.asc())
            .all()
        )

    # Writes
    def create(
        self,
        *,
        user_id: int,
        skill_id: int,
        score: float,
    ) -> ProgressLog:
        """Insert one history row. Service layer handles the commit."""
        row = ProgressLog(
            user_id=user_id,
            skill_id=skill_id,
            score=score,
        )
        self.db.add(row)
        self.db.flush()
        return row


class SkillPointsRepository:
    """CRUD for points-based skill tracking.

    One row per (user, skill). Mutable — points and display_score
    are updated on every relevant task.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # Reads
    def get_all_for_user(self, user_id: int) -> list[SkillPoints]:
        """All skill-points rows for a user, or empty list if none exist."""
        return (
            self.db.query(SkillPoints)
            .filter(SkillPoints.user_id == user_id)
            .all()
        )

    def get_one(self, user_id: int, skill_id: int) -> SkillPoints | None:
        """Single (user, skill) row, or None if not yet initialised."""
        return (
            self.db.query(SkillPoints)
            .filter(
                SkillPoints.user_id == user_id,
                SkillPoints.skill_id == skill_id,
            )
            .first()
        )

    # Writes
    def upsert_points(
        self,
        *,
        user_id: int,
        skill_id: int,
        points: int,
    ) -> SkillPoints:
        """Insert or update points, auto-capping at 10000."""
        points = min(points, 10000)

        existing = self.get_one(user_id, skill_id)
        if existing is not None:
            existing.points = points
            existing.display_score = min(10.0, points / 1000.0)
            self.db.flush()
            return existing

        new_row = SkillPoints(
            user_id=user_id,
            skill_id=skill_id,
            points=points,
            display_score=min(10.0, points / 1000.0),
        )
        self.db.add(new_row)
        self.db.flush()
        return new_row


class SkillPointsLogRepository:
    """Append-only audit log of points earned per task."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # Reads
    def list_for_user(
        self,
        *,
        user_id: int,
        skill_id: int | None = None,
        limit: int = 50,
    ) -> list[SkillPointsLog]:
        """Return recent points gains, newest first. Optionally filter by skill."""
        q = (
            self.db.query(SkillPointsLog)
            .filter(SkillPointsLog.user_id == user_id)
            .order_by(SkillPointsLog.created_at.desc())
        )
        if skill_id is not None:
            q = q.filter(SkillPointsLog.skill_id == skill_id)
        return q.limit(limit).all()

    def has_for_session(self, session_id: int) -> bool:
        """True if any points were ever logged for this DailySession.

        Survives scorecard deletion (reset/restart drop the scorecard but never
        the append-only log), so the completion path can tell that points were
        already awarded for this session and avoid double-counting on re-complete.
        """
        return (
            self.db.query(SkillPointsLog.id)
            .filter(SkillPointsLog.session_id == session_id)
            .first()
            is not None
        )

    # Writes
    def create(
        self,
        *,
        user_id: int,
        skill_id: int,
        points_earned: int,
        reason: str,
        session_id: int | None = None,
    ) -> SkillPointsLog:
        """Insert one log row. Service layer handles the commit."""
        log = SkillPointsLog(
            user_id=user_id,
            skill_id=skill_id,
            points_earned=points_earned,
            reason=reason,
            session_id=session_id,
        )
        self.db.add(log)
        self.db.flush()
        return log