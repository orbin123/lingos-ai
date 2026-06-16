"""Activity heatmap counts — evaluated attempts bucketed by local date."""

from __future__ import annotations

from datetime import date, datetime, timedelta, time, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.sessions.models import ActivityAttempt, AttemptStatus, DailySession
from app.modules.streaks.dates import _resolve_zone


def count_evaluated_activities_by_local_date(
    db: Session,
    *,
    user_id: int,
    tz: str,
    start: date,
    end: date,
) -> dict[date, int]:
    """Return how many evaluated activities the user submitted on each local date.

    The heatmap uses this — not completed sessions — so a single daily session
    with four activities renders as intensity 4 once all four are submitted.
    """
    zone = _resolve_zone(tz)
    window_start_utc = datetime.combine(start, time.min, tzinfo=zone).astimezone(
        timezone.utc
    )
    window_end_utc = datetime.combine(
        end + timedelta(days=1),
        time.min,
        tzinfo=zone,
    ).astimezone(timezone.utc)

    submitted_times = db.execute(
        select(ActivityAttempt.submitted_at)
        .join(DailySession, DailySession.id == ActivityAttempt.session_id)
        .where(
            DailySession.user_id == user_id,
            ActivityAttempt.status == AttemptStatus.EVALUATED,
            ActivityAttempt.submitted_at.isnot(None),
            ActivityAttempt.submitted_at >= window_start_utc,
            ActivityAttempt.submitted_at < window_end_utc,
        )
    ).scalars()

    counts: dict[date, int] = {}
    for submitted_at in submitted_times:
        if submitted_at is None:
            continue
        if submitted_at.tzinfo is None:
            submitted_at = submitted_at.replace(tzinfo=timezone.utc)
        local_d = submitted_at.astimezone(zone).date()
        if start <= local_d <= end:
            counts[local_d] = counts.get(local_d, 0) + 1
    return counts
