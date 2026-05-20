"""Repositories for session lifecycle tables.

Read- and write-helpers only. Business decisions (replay rule, scoring) live
in `service.py` and `scoring_writer.py`.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityEvaluation,
    ActivityFeedback,
    AttemptStatus,
    DailySession,
    SessionScorecard,
    SessionStatus,
)


class DailySessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_session_id(self, session_id: str) -> DailySession | None:
        return self.db.execute(
            select(DailySession).where(DailySession.session_id == session_id)
        ).scalar_one_or_none()

    def get_with_attempts(self, session_id: str) -> DailySession | None:
        return self.db.execute(
            select(DailySession)
            .options(
                selectinload(DailySession.attempts).selectinload(ActivityAttempt.evaluation),
                selectinload(DailySession.attempts).selectinload(ActivityAttempt.feedback),
                selectinload(DailySession.scorecard),
            )
            .where(DailySession.session_id == session_id)
        ).scalar_one_or_none()

    def get_in_progress(self, *, user_id: int, day_id: str) -> DailySession | None:
        return self.db.execute(
            select(DailySession).where(
                DailySession.user_id == user_id,
                DailySession.day_id == day_id,
                DailySession.status == SessionStatus.IN_PROGRESS,
            )
        ).scalar_one_or_none()

    def get_latest_for_day(
        self, *, user_id: int, day_id: str, status: SessionStatus | None = None
    ) -> DailySession | None:
        stmt = (
            select(DailySession)
            .options(selectinload(DailySession.attempts))
            .where(DailySession.user_id == user_id, DailySession.day_id == day_id)
            .order_by(DailySession.id.desc())
            .limit(1)
        )
        if status is not None:
            stmt = stmt.where(DailySession.status == status)
        return self.db.execute(stmt).scalar_one_or_none()

    def has_completed_for_day(self, *, user_id: int, day_id: str) -> bool:
        existing = self.db.execute(
            select(DailySession.id).where(
                DailySession.user_id == user_id,
                DailySession.day_id == day_id,
                DailySession.status == SessionStatus.COMPLETED,
            ).limit(1)
        ).first()
        return existing is not None

    def add(self, session: DailySession) -> DailySession:
        self.db.add(session)
        self.db.flush()
        return session


class ActivityAttemptRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, *, session_pk: int, sequence: int) -> ActivityAttempt | None:
        return self.db.execute(
            select(ActivityAttempt).where(
                ActivityAttempt.session_id == session_pk,
                ActivityAttempt.sequence == sequence,
            )
        ).scalar_one_or_none()

    def list_for_session(self, session_pk: int) -> list[ActivityAttempt]:
        return list(
            self.db.execute(
                select(ActivityAttempt)
                .where(ActivityAttempt.session_id == session_pk)
                .order_by(ActivityAttempt.sequence)
            ).scalars()
        )

    def first_pending(self, session_pk: int) -> ActivityAttempt | None:
        return self.db.execute(
            select(ActivityAttempt)
            .where(
                ActivityAttempt.session_id == session_pk,
                ActivityAttempt.status == AttemptStatus.PENDING,
            )
            .order_by(ActivityAttempt.sequence)
            .limit(1)
        ).scalar_one_or_none()


class EvaluationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, evaluation: ActivityEvaluation) -> ActivityEvaluation:
        self.db.add(evaluation)
        self.db.flush()
        return evaluation


class FeedbackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, feedback: ActivityFeedback) -> ActivityFeedback:
        self.db.add(feedback)
        self.db.flush()
        return feedback


class ScorecardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, scorecard: SessionScorecard) -> SessionScorecard:
        self.db.add(scorecard)
        self.db.flush()
        return scorecard

    def get_for_session(self, session_pk: int) -> SessionScorecard | None:
        return self.db.execute(
            select(SessionScorecard).where(SessionScorecard.session_id == session_pk)
        ).scalar_one_or_none()
