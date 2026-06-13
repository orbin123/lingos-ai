"""Locked constants for the feedback-prompt system.

Tuning these changes behaviour with no migration. The eligibility thresholds
and cooldowns mirror the product spec; ``SHOW_PROBABILITY`` keeps the prompt
from feeling spammy even once a user is eligible.
"""

# ── Eligibility thresholds (ANY one met → eligible) ────────────────
ELIGIBLE_COMPLETED_TASKS = 5
ELIGIBLE_DAYS_SINCE_SIGNUP = 3
ELIGIBLE_FEEDBACK_REPORTS = 10
ELIGIBLE_ACTIVE_MINUTES = 30.0

# ── Cooldowns ──────────────────────────────────────────────────────
DISMISS_COOLDOWN_DAYS = 7
SUBMIT_COOLDOWN_DAYS = 30

# ── Randomized display ─────────────────────────────────────────────
# Once eligible and outside cooldown, only show the prompt this fraction of
# navigation checks. Keeps the experience SaaS-like rather than nagging.
SHOW_PROBABILITY = 0.25

# ── Trigger types (also surfaced to the client + prompt log) ───────
TRIGGER_TASK_MILESTONE = "TASK_MILESTONE"
TRIGGER_DAY_3 = "DAY_3"
TRIGGER_FEEDBACK_REPORTS = "FEEDBACK_REPORTS"
TRIGGER_TIME_SPENT = "TIME_SPENT"

# How many days of history the admin trend chart spans.
TREND_WINDOW_DAYS = 30
