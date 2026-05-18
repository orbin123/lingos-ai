"""Pushes the session scorecard into the user's SkillPoints + audit log.

Separated from `SessionService` because:
  - Scoring writes touch a different module (`progress/`)
  - Replay-guard logic is local to writing (only first attempt earns points)
  - Tests can verify the math integration without spinning up a full service

Public entry point is `apply_session_scorecard(...)`.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.modules.progress.repository import (
    SkillPointsLogRepository,
    SkillPointsRepository,
)
from app.modules.sessions.models import DailySession, SessionScorecard
from app.modules.skills.repository import SkillRepository


@dataclass(frozen=True)
class ApplyReport:
    """What the writer actually did. Returned for logging and tests."""

    applied: bool
    rows_written: int
    rows_skipped: int
    reason: str


def apply_session_scorecard(
    db: Session,
    *,
    session: DailySession,
    scorecard: SessionScorecard,
) -> ApplyReport:
    """Add the scorecard's `points_earned` into `SkillPoints` + audit log.

    Replay rule: only the first COMPLETED session for `(user_id, day_id)`
    awards points (`session.is_first_attempt == True`). Subsequent attempts
    record the scorecard but skip the points write — they are practice runs.

    Idempotent: a second call on the same scorecard (after `points_applied`
    has been flipped to True by the caller) is a no-op.
    """
    if scorecard.points_applied:
        return ApplyReport(
            applied=False,
            rows_written=0,
            rows_skipped=0,
            reason="scorecard already applied",
        )

    if not session.is_first_attempt:
        return ApplyReport(
            applied=False,
            rows_written=0,
            rows_skipped=len(scorecard.points_earned),
            reason="replay — points not awarded",
        )

    if not scorecard.points_earned:
        return ApplyReport(
            applied=True,
            rows_written=0,
            rows_skipped=0,
            reason="nothing earned",
        )

    skill_name_to_id = SkillRepository(db).name_to_id_map()
    points_repo = SkillPointsRepository(db)
    log_repo = SkillPointsLogRepository(db)

    written = 0
    skipped = 0
    for skill_name, delta in scorecard.points_earned.items():
        skill_id = skill_name_to_id.get(skill_name)
        if skill_id is None:
            # Unknown skill name — log and skip rather than crashing the whole
            # write. This shouldn't happen in production; surfaces if registry
            # and DB drift apart.
            skipped += 1
            continue

        current = points_repo.get_one(session.user_id, skill_id)
        old_points = current.points if current is not None else 0
        new_total = old_points + int(delta)

        points_repo.upsert_points(
            user_id=session.user_id,
            skill_id=skill_id,
            points=new_total,
        )
        log_repo.create(
            user_id=session.user_id,
            skill_id=skill_id,
            points_earned=int(delta),
            reason=f"session:{session.session_id}",
            session_id=session.id,
        )
        written += 1

    return ApplyReport(
        applied=True,
        rows_written=written,
        rows_skipped=skipped,
        reason="points applied",
    )
