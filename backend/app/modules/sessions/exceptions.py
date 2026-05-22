"""Session-specific exceptions. Routes layer maps these to HTTP status codes."""


class SessionError(Exception):
    """Base for all session lifecycle errors."""


class SessionNotFound(SessionError):
    """404 — no session with that session_id (or not owned by the caller)."""


class DayNotFound(SessionError):
    """404 — `day_id` does not exist in the curriculum."""


class SessionAlreadyOpen(SessionError):
    """409 — user already has an in-progress session for this day."""


class SessionAlreadyCompleted(SessionError):
    """409 — session is COMPLETED; further submits / completes are no-ops."""


class SessionAdvanceBlocked(SessionError):
    """409 — the learner cannot advance from the current day yet."""


class SessionAbandoned(SessionError):
    """409 — session is ABANDONED; cannot be reactivated."""


class AttemptNotFound(SessionError):
    """404 — no attempt at that sequence in the session."""


class AttemptAlreadySubmitted(SessionError):
    """409 — attempt has already been evaluated; resubmit not allowed in Phase 3."""


class NoActivitiesPlanned(SessionError):
    """422 — planner returned an empty skeleton (no activities matched the day)."""


class InvalidTasksPerDay(SessionError):
    """422 — tasks_per_day outside 2..4."""
