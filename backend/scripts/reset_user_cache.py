"""Reset every cached lesson artifact for a single user.

Use when a learner is stuck on stale session state — completed sessions
that should be retried, points that should be zeroed, a course preference
pointing at the wrong week. This wipes the per-user session history so
the next /sessions/start-today regenerates from scratch.

Tables touched (FK-child-first delete order):
  activity_feedback   → DELETE (children of activity_attempts)
  activity_evaluations → DELETE (children of activity_attempts)
  activity_attempts   → DELETE (children of daily_sessions)
  session_scorecards  → DELETE (children of daily_sessions)
  skill_points_logs   → DELETE (audit log entries for this user)
  daily_sessions      → DELETE
  progress_logs       → DELETE
  skill_points        → UPDATE points/display_score to 0 (the row
                        carries the user's earned baseline — we
                        zero it out rather than drop the row so
                        the schema invariant of one row per
                        (user, skill) survives)

With --restart-curriculum:
  user_course_preferences → UPDATE current_week=1, current_day_in_week=1,
                            last_completed_on=NULL

Usage:
    cd backend
    python -m scripts.reset_user_cache --user-id 42
    python -m scripts.reset_user_cache --email orbinsunny@gmail.com
    python -m scripts.reset_user_cache --user-id 42 --restart-curriculum

The script runs inside a single transaction. Use `--dry-run` to preview.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import text  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402


# (label, delete-sql, count-sql) tuples. The count-sql mirrors the
# delete-sql but returns a row count so dry-run can preview impact.
# Order matters — children before parents.
_DELETE_OPERATIONS: tuple[tuple[str, str, str], ...] = (
    (
        "activity_feedback",
        """
        DELETE FROM activity_feedback
         WHERE attempt_id IN (
           SELECT aa.id FROM activity_attempts aa
             JOIN daily_sessions ds ON ds.id = aa.session_id
            WHERE ds.user_id = :user_id
         )
        """,
        """
        SELECT COUNT(*) FROM activity_feedback
         WHERE attempt_id IN (
           SELECT aa.id FROM activity_attempts aa
             JOIN daily_sessions ds ON ds.id = aa.session_id
            WHERE ds.user_id = :user_id
         )
        """,
    ),
    (
        "activity_evaluations",
        """
        DELETE FROM activity_evaluations
         WHERE attempt_id IN (
           SELECT aa.id FROM activity_attempts aa
             JOIN daily_sessions ds ON ds.id = aa.session_id
            WHERE ds.user_id = :user_id
         )
        """,
        """
        SELECT COUNT(*) FROM activity_evaluations
         WHERE attempt_id IN (
           SELECT aa.id FROM activity_attempts aa
             JOIN daily_sessions ds ON ds.id = aa.session_id
            WHERE ds.user_id = :user_id
         )
        """,
    ),
    (
        "activity_attempts",
        """
        DELETE FROM activity_attempts
         WHERE session_id IN (
           SELECT id FROM daily_sessions WHERE user_id = :user_id
         )
        """,
        """
        SELECT COUNT(*) FROM activity_attempts
         WHERE session_id IN (
           SELECT id FROM daily_sessions WHERE user_id = :user_id
         )
        """,
    ),
    (
        "session_scorecards",
        """
        DELETE FROM session_scorecards
         WHERE session_id IN (
           SELECT id FROM daily_sessions WHERE user_id = :user_id
         )
        """,
        """
        SELECT COUNT(*) FROM session_scorecards
         WHERE session_id IN (
           SELECT id FROM daily_sessions WHERE user_id = :user_id
         )
        """,
    ),
    (
        "skill_points_logs",
        "DELETE FROM skill_points_logs WHERE user_id = :user_id",
        "SELECT COUNT(*) FROM skill_points_logs WHERE user_id = :user_id",
    ),
    (
        "daily_sessions",
        "DELETE FROM daily_sessions WHERE user_id = :user_id",
        "SELECT COUNT(*) FROM daily_sessions WHERE user_id = :user_id",
    ),
    (
        "progress_logs",
        "DELETE FROM progress_logs WHERE user_id = :user_id",
        "SELECT COUNT(*) FROM progress_logs WHERE user_id = :user_id",
    ),
)


_ZERO_SKILL_POINTS_SQL = """
UPDATE skill_points
   SET points = 0,
       display_score = 0.0
 WHERE user_id = :user_id
"""

_RESTART_CURRICULUM_SQL = """
UPDATE user_course_preferences
   SET current_week = 1,
       current_day_in_week = 1,
       last_completed_on = NULL
 WHERE user_id = :user_id
"""


def _resolve_user_id(session, *, user_id: int | None, email: str | None) -> int:
    if user_id is not None:
        row = session.execute(
            text("SELECT id FROM users WHERE id = :id"), {"id": user_id}
        ).first()
        if row is None:
            raise SystemExit(f"No user with id={user_id}")
        return int(row[0])

    if email is None:
        raise SystemExit("Specify either --user-id or --email.")

    row = session.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": email.lower()},
    ).first()
    if row is None:
        raise SystemExit(f"No user with email={email!r}")
    return int(row[0])


def reset_user(
    *,
    user_id: int | None,
    email: str | None,
    restart_curriculum: bool,
    dry_run: bool,
) -> None:
    session = SessionLocal()
    try:
        resolved_id = _resolve_user_id(session, user_id=user_id, email=email)
        print(f"Resolved user id: {resolved_id}")

        totals: dict[str, int] = {}

        for label, delete_sql, count_sql in _DELETE_OPERATIONS:
            if dry_run:
                count = session.execute(
                    text(count_sql), {"user_id": resolved_id}
                ).scalar_one()
                totals[label] = int(count)
            else:
                result = session.execute(
                    text(delete_sql), {"user_id": resolved_id}
                )
                totals[label] = int(result.rowcount or 0)

        if dry_run:
            count = session.execute(
                text(
                    "SELECT COUNT(*) FROM skill_points "
                    "WHERE user_id = :user_id "
                    "AND (points > 0 OR display_score > 0.0)"
                ),
                {"user_id": resolved_id},
            ).scalar_one()
            totals["skill_points (would zero out)"] = int(count)
        else:
            result = session.execute(
                text(_ZERO_SKILL_POINTS_SQL), {"user_id": resolved_id}
            )
            totals["skill_points (zeroed)"] = int(result.rowcount or 0)

        if restart_curriculum:
            if dry_run:
                row = session.execute(
                    text(
                        "SELECT current_week, current_day_in_week "
                        "FROM user_course_preferences "
                        "WHERE user_id = :user_id"
                    ),
                    {"user_id": resolved_id},
                ).first()
                if row is not None:
                    totals["user_course_preferences (would reset)"] = 1
                    print(
                        f"  preference currently at "
                        f"week={row[0]} day={row[1]}"
                    )
                else:
                    totals["user_course_preferences (would reset)"] = 0
            else:
                result = session.execute(
                    text(_RESTART_CURRICULUM_SQL),
                    {"user_id": resolved_id},
                )
                totals["user_course_preferences (reset)"] = int(
                    result.rowcount or 0
                )

        if dry_run:
            print("\n[DRY RUN] No rows changed. Counts that would be affected:")
            session.rollback()
        else:
            session.commit()
            print("\nRows deleted/updated:")

        for label, count in totals.items():
            print(f"  {label}: {count}")

        if not dry_run:
            print(
                f"\nDone. The next /sessions/start-today call for user "
                f"{resolved_id} will start a fresh session."
            )
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--user-id", type=int, help="Target user id")
    target.add_argument("--email", type=str, help="Target user email")
    parser.add_argument(
        "--restart-curriculum",
        action="store_true",
        help=(
            "Reset the user's course preference to Week 1 Day 1 "
            "(in addition to clearing session history)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without committing.",
    )
    args = parser.parse_args()

    reset_user(
        user_id=args.user_id,
        email=args.email,
        restart_curriculum=args.restart_curriculum,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
