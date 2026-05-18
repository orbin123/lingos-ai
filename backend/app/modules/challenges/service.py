"""Business logic for the challenges read API."""

from __future__ import annotations

from app.modules.challenges.models import Challenge, ChallengeAttempt
from app.modules.challenges.repository import (
    ChallengeAttemptRepository,
    ChallengeRepository,
)
from app.modules.challenges.schemas import (
    ChallengeDetailRead,
    ChallengeHistoryAttempt,
    ChallengeHistoryRead,
    ChallengeLevelRead,
    ChallengeListItem,
)


class ChallengeNotFound(Exception):
    """Raised when an active challenge cannot be found."""


class ChallengeAttemptNotFound(Exception):
    """Raised when an attempt cannot be found for the current user."""


class ChallengeReadService:
    """Read-side orchestration for challenge catalog and learner progress."""

    def __init__(self, db) -> None:
        self.challenge_repo = ChallengeRepository(db)
        self.attempt_repo = ChallengeAttemptRepository(db)

    def list_challenges(self) -> list[ChallengeListItem]:
        challenges = self.challenge_repo.list_active()
        return [
            ChallengeListItem(
                id=challenge.id,
                slug=challenge.slug,
                name=challenge.name,
                short_description=challenge.short_description,
                icon=challenge.icon,
                level_count=len(challenge.levels),
            )
            for challenge in challenges
        ]

    def get_detail(self, *, slug: str, user_id: int) -> ChallengeDetailRead:
        challenge = self.challenge_repo.get_active_by_slug(slug)
        if challenge is None:
            raise ChallengeNotFound(f"challenge {slug!r} not found")
        return self._detail_for(challenge=challenge, user_id=user_id)

    def get_history(self, *, slug: str, user_id: int) -> ChallengeHistoryRead:
        challenge = self.challenge_repo.get_active_by_slug(slug)
        if challenge is None:
            raise ChallengeNotFound(f"challenge {slug!r} not found")

        attempts = self.attempt_repo.list_for_challenge(
            user_id=user_id,
            challenge_id=challenge.id,
        )
        best_attempt_ids = self._best_attempt_ids(attempts)
        return ChallengeHistoryRead(
            challenge_slug=challenge.slug,
            challenge_name=challenge.name,
            attempts=[
                ChallengeHistoryAttempt(
                    id=attempt.id,
                    challenge_level_id=attempt.challenge_level_id,
                    level_number=attempt.level.level_number,
                    level_name=attempt.level.name,
                    status=attempt.status,
                    started_at=attempt.started_at,
                    completed_at=attempt.completed_at,
                    expires_at=attempt.expires_at,
                    overall_score=(
                        float(attempt.overall_score)
                        if attempt.overall_score is not None
                        else None
                    ),
                    section_scores=attempt.section_scores,
                    passed=attempt.passed,
                    is_best_for_level=attempt.id in best_attempt_ids,
                    created_at=attempt.created_at,
                )
                for attempt in attempts
            ],
        )

    def get_attempt(self, *, attempt_id: int, user_id: int) -> ChallengeAttempt:
        attempt = self.attempt_repo.get_for_user(attempt_id=attempt_id, user_id=user_id)
        if attempt is None:
            raise ChallengeAttemptNotFound(f"attempt {attempt_id!r} not found")
        return attempt

    def _detail_for(self, *, challenge: Challenge, user_id: int) -> ChallengeDetailRead:
        levels = sorted(challenge.levels, key=lambda level: level.level_number)
        level_ids = [level.id for level in levels]
        best_scores = self.attempt_repo.best_scores_by_level(
            user_id=user_id,
            level_ids=level_ids,
        )
        attempt_counts = self.attempt_repo.attempt_counts_by_level(
            user_id=user_id,
            level_ids=level_ids,
        )

        unlocked_level_numbers = {1}
        levels_by_number = {level.level_number: level for level in levels}
        for level in levels:
            previous = levels_by_number.get(level.level_number - 1)
            if previous is None:
                continue
            previous_best = best_scores.get(previous.id)
            if (
                previous_best is not None
                and previous_best >= float(previous.pass_threshold)
            ):
                unlocked_level_numbers.add(level.level_number)

        return ChallengeDetailRead(
            id=challenge.id,
            slug=challenge.slug,
            name=challenge.name,
            short_description=challenge.short_description,
            rules_md=challenge.rules_md,
            icon=challenge.icon,
            levels=[
                ChallengeLevelRead(
                    id=level.id,
                    level_number=level.level_number,
                    name=level.name,
                    time_limit_seconds=level.time_limit_seconds,
                    pass_threshold=float(level.pass_threshold),
                    config=level.config,
                    unlocked=level.level_number in unlocked_level_numbers,
                    best_score=best_scores.get(level.id),
                    attempt_count=attempt_counts.get(level.id, 0),
                )
                for level in levels
            ],
        )

    @staticmethod
    def _best_attempt_ids(attempts: list[ChallengeAttempt]) -> set[int]:
        best_by_level: dict[int, tuple[float, int]] = {}
        for attempt in attempts:
            if attempt.overall_score is None:
                continue
            score = float(attempt.overall_score)
            current = best_by_level.get(attempt.challenge_level_id)
            if current is None or score > current[0]:
                best_by_level[attempt.challenge_level_id] = (score, attempt.id)
        return {attempt_id for _score, attempt_id in best_by_level.values()}

