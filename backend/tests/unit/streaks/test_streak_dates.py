"""Unit tests for streak date utilities (no DB)."""

from __future__ import annotations

from datetime import date, datetime, timezone

from app.modules.streaks.dates import (
    build_last_n_days,
    get_date_gap_in_days,
    get_previous_local_date,
    get_user_local_date,
)


class TestUserLocalDate:
    def test_kolkata_evening_utc_is_already_next_day_in_ist(self):
        # 2026-05-19 19:30 UTC == 2026-05-20 01:00 IST
        now_utc = datetime(2026, 5, 19, 19, 30, tzinfo=timezone.utc)
        assert get_user_local_date("Asia/Kolkata", now_utc=now_utc) == date(2026, 5, 20)

    def test_kolkata_afternoon_utc_is_same_day_in_ist(self):
        # 2026-05-19 12:00 UTC == 2026-05-19 17:30 IST
        now_utc = datetime(2026, 5, 19, 12, 0, tzinfo=timezone.utc)
        assert get_user_local_date("Asia/Kolkata", now_utc=now_utc) == date(2026, 5, 19)

    def test_invalid_timezone_falls_back_to_default(self):
        now_utc = datetime(2026, 5, 19, 12, 0, tzinfo=timezone.utc)
        # Garbage zone resolves to Asia/Kolkata (the default).
        assert get_user_local_date("Not/A/Zone", now_utc=now_utc) == date(2026, 5, 19)


class TestGapAndPrev:
    def test_get_previous_local_date(self):
        assert get_previous_local_date(date(2026, 5, 19)) == date(2026, 5, 18)

    def test_gap_is_calendar_days(self):
        assert get_date_gap_in_days(date(2026, 5, 18), date(2026, 5, 19)) == 1
        assert get_date_gap_in_days(date(2026, 5, 17), date(2026, 5, 19)) == 2
        assert get_date_gap_in_days(date(2026, 5, 19), date(2026, 5, 19)) == 0


class TestBuildLastNDays:
    def test_length_91_and_ascending(self):
        end = date(2026, 5, 19)
        out = build_last_n_days(end, 91)
        assert len(out) == 91
        assert out[-1] == end
        assert out[0] == date(2026, 2, 18)  # 90 days earlier
        # Ascending
        assert all(out[i] < out[i + 1] for i in range(90))
