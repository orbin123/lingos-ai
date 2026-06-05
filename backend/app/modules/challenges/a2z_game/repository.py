"""Repository helpers for A2Z Challenge progress and rounds."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.challenges.a2z_game.models import A2ZUserProgress
from app.modules.challenges.models import ChallengeAttempt, ChallengeAttemptStatus


class A2ZProgressRepository:
    """CRUD for the ``a2z_user_progress`` table."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_and_challenge(
        self,
        *,
        user_id: int,
        challenge_id: int,
    ) -> A2ZUserProgress | None:
        return self.db.execute(
            select(A2ZUserProgress).where(
                A2ZUserProgress.user_id == user_id,
                A2ZUserProgress.challenge_id == challenge_id,
            )
        ).scalar_one_or_none()

    def get_or_create(
        self,
        *,
        user_id: int,
        challenge_id: int,
    ) -> A2ZUserProgress:
        """Return existing progress or create a fresh one with empty clearances."""
        progress = self.get_by_user_and_challenge(
            user_id=user_id, challenge_id=challenge_id
        )
        if progress is None:
            progress = A2ZUserProgress(
                user_id=user_id,
                challenge_id=challenge_id,
                cleared_letters={"1": [], "2": [], "3": []},
                game_completed_at=None,
                last_restarted_at=None,
            )
            self.db.add(progress)
            self.db.flush()
            self.db.refresh(progress)
        return progress

    def save(self, progress: A2ZUserProgress) -> A2ZUserProgress:
        """Persist changes to an existing progress row."""
        self.db.flush()
        self.db.refresh(progress)
        return progress


class A2ZRoundRepository:
    """Queries for A2Z challenge attempts (rounds)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_for_user(
        self,
        *,
        round_id: int,
        user_id: int,
    ) -> ChallengeAttempt | None:
        """Fetch one attempt belonging to *user_id* with its level eagerly loaded."""
        return self.db.execute(
            select(ChallengeAttempt)
            .where(
                ChallengeAttempt.id == round_id,
                ChallengeAttempt.user_id == user_id,
            )
            .options(selectinload(ChallengeAttempt.level))
        ).scalar_one_or_none()

    def get_in_progress_for_user(
        self,
        *,
        round_id: int,
        user_id: int,
    ) -> ChallengeAttempt | None:
        """Fetch an in-progress attempt belonging to *user_id*."""
        return self.db.execute(
            select(ChallengeAttempt)
            .where(
                ChallengeAttempt.id == round_id,
                ChallengeAttempt.user_id == user_id,
                ChallengeAttempt.status == ChallengeAttemptStatus.IN_PROGRESS,
            )
            .options(selectinload(ChallengeAttempt.level))
        ).scalar_one_or_none()
