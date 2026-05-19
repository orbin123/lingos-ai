"""Streak / daily-activity module.

Tracks one row per (user, local_date) of successful lesson completions and
derives current/longest streak counters, animation state, and the
GitHub-style 13-week activity grid that the dashboard renders.

Public surface:
  - StreakService.record_in_same_tx(user_id, session_id=None)
        Hook called from SessionService.complete_session — does NOT commit.
  - StreakService.get_streak_data(user_id) -> StreakDataResponse
        Used by GET /streak/me.
"""
