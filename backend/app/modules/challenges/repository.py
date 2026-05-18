"""Repository helpers for the challenges module."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.challenges.models import (
    Challenge,
    ChallengeAttempt,
    ChallengeAttemptStatus,
    ChallengeLevel,
)


class ChallengeRepository:
    """Read access for challenge catalog data."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(self) -> list[Challenge]:
        return list(
            self.db.execute(
                select(Challenge)
                .where(Challenge.is_active.is_(True))
                .options(selectinload(Challenge.levels))
                .order_by(Challenge.sort_order, Challenge.id)
            ).scalars()
        )

    def get_active_by_slug(self, slug: str) -> Challenge | None:
        return self.db.execute(
            select(Challenge)
            .where(Challenge.slug == slug, Challenge.is_active.is_(True))
            .options(selectinload(Challenge.levels))
        ).scalar_one_or_none()


class ChallengeAttemptRepository:
    """Read helpers for learner challenge attempts."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_for_user(self, *, attempt_id: int, user_id: int) -> ChallengeAttempt | None:
        return self.db.execute(
            select(ChallengeAttempt)
            .where(
                ChallengeAttempt.id == attempt_id,
                ChallengeAttempt.user_id == user_id,
            )
            .options(selectinload(ChallengeAttempt.level))
        ).scalar_one_or_none()

    def best_scores_by_level(self, *, user_id: int, level_ids: list[int]) -> dict[int, float]:
        if not level_ids:
            return {}
        rows = self.db.execute(
            select(
                ChallengeAttempt.challenge_level_id,
                func.max(ChallengeAttempt.overall_score),
            )
            .where(
                ChallengeAttempt.user_id == user_id,
                ChallengeAttempt.challenge_level_id.in_(level_ids),
                ChallengeAttempt.status == ChallengeAttemptStatus.COMPLETED,
                ChallengeAttempt.overall_score.is_not(None),
            )
            .group_by(ChallengeAttempt.challenge_level_id)
        ).all()
        return {level_id: float(score) for level_id, score in rows if score is not None}

    def attempt_counts_by_level(
        self,
        *,
        user_id: int,
        level_ids: list[int],
    ) -> dict[int, int]:
        if not level_ids:
            return {}
        rows = self.db.execute(
            select(
                ChallengeAttempt.challenge_level_id,
                func.count(ChallengeAttempt.id),
            )
            .where(
                ChallengeAttempt.user_id == user_id,
                ChallengeAttempt.challenge_level_id.in_(level_ids),
            )
            .group_by(ChallengeAttempt.challenge_level_id)
        ).all()
        return {level_id: int(count) for level_id, count in rows}

    def list_for_challenge(
        self,
        *,
        user_id: int,
        challenge_id: int,
    ) -> list[ChallengeAttempt]:
        return list(
            self.db.execute(
                select(ChallengeAttempt)
                .join(ChallengeLevel, ChallengeLevel.id == ChallengeAttempt.challenge_level_id)
                .where(
                    ChallengeAttempt.user_id == user_id,
                    ChallengeLevel.challenge_id == challenge_id,
                )
                .options(selectinload(ChallengeAttempt.level))
                .order_by(ChallengeAttempt.created_at.desc(), ChallengeAttempt.id.desc())
            ).scalars()
        )

