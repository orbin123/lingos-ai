"""Timezone-aware date helpers for the streak system.

All streak comparisons operate on date-only values in the user's local
timezone. NEVER compare raw UTC timestamps for streak decisions — a
session completed at 19:30 UTC counts as the next day in IST.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TIMEZONE = "Asia/Kolkata"


def _resolve_zone(tz: str | None) -> ZoneInfo:
    try:
        return ZoneInfo(tz or DEFAULT_TIMEZONE)
    except ZoneInfoNotFoundError:
        return ZoneInfo(DEFAULT_TIMEZONE)


def get_user_local_date(tz: str | None, now_utc: datetime | None = None) -> date:
    """Return today's date in the user's timezone."""
    now_utc = now_utc or datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    return now_utc.astimezone(_resolve_zone(tz)).date()


def get_previous_local_date(d: date) -> date:
    return d - timedelta(days=1)


def get_date_gap_in_days(last: date, current: date) -> int:
    """Return `current - last` in whole days. May be negative if clocks skew."""
    return (current - last).days


def build_last_n_days(end_date: date, n: int = 91) -> list[date]:
    """Return `n` dates ending at `end_date` (inclusive), ascending."""
    start = end_date - timedelta(days=n - 1)
    return [start + timedelta(days=i) for i in range(n)]
