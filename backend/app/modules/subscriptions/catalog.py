"""Plan catalog — the server-side source of truth for purchasable plans.

Amounts live here and only here: payment order amounts are always taken
from this catalog, never from the client.
"""

from datetime import datetime

# Course length is the only per-plan piece of state the daily-sessions flow
# cares about — the rest (title, level) is presentational and rendered by the
# frontend from the plan_id directly.
PLAN_CATALOG: dict[str, dict[str, object]] = {
    "beginner-24w": {
        "course_length": "24w",
        "name": "24-Week Foundation",
        "amount_paid": 999.0,
        "currency": "INR",
    },
    "beginner-48w": {
        "course_length": "48w",
        "name": "48-Week Plan",
        "amount_paid": 1999.0,
        "currency": "INR",
    },
}


def add_years(moment: datetime, years: int) -> datetime:
    """Add calendar years, clamping Feb 29 → Feb 28 on non-leap targets."""
    try:
        return moment.replace(year=moment.year + years)
    except ValueError:
        return moment.replace(year=moment.year + years, day=28)
