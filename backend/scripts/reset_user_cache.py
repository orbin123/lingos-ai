"""Reset every cached lesson artifact for a single user.

Use after the curriculum/personalisation refactor when a user is still
seeing the old "What does 'mother' mean?"-style content. The migration
wipes daily_plans for everyone, but tasks, learning sessions, responses,
evaluations, and feedback persist per-user. This script clears all of
that for one user so the next chat visit regenerates from scratch under
the new objective-driven planner.

Usage:
    cd backend
    python -m scripts.reset_user_cache --user-id 42
    python -m scripts.reset_user_cache --email orbinsunny@gmail.com
    python -m scripts.reset_user_cache --user-id 42 --restart-curriculum

`--restart-curriculum` also resets the enrollment to Week 1 Day 1 so the
learner gets the new W1D1 lesson immediately.

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


# Order matters — children before parents.
_DELETE_STATEMENTS = (
    (
        "feedback",
        """
        DELETE FROM feedback
         WHERE evaluation_id IN (
           SELECT e.id
             FROM evaluations e
             JOIN user_responses r ON r.id = e.response_id
             JOIN user_tasks ut ON ut.id = r.user_task_id
            WHERE ut.user_id = :user_id
         )
        """,
    ),
    (
        "evaluations",
        """
        DELETE FROM evaluations
         WHERE response_id IN (
           SELECT r.id
             FROM user_responses r
             JOIN user_tasks ut ON ut.id = r.user_task_id
            WHERE ut.user_id = :user_id
         )
        """,
    ),
    (
        "user_responses",
        """
        DELETE FROM user_responses
         WHERE user_task_id IN (
           SELECT id FROM user_tasks WHERE user_id = :user_id
         )
        """,
    ),
    (
        "learning_sessions",
        "DELETE FROM learning_sessions WHERE user_id = :user_id",
    ),
    (
        "user_tasks",
        "DELETE FROM user_tasks WHERE user_id = :user_id",
    ),
    (
        "daily_plans",
        "DELETE FROM daily_plans WHERE user_id = :user_id",
    ),
)


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
        for label, statement in _DELETE_STATEMENTS:
            if dry_run:
                # Count first so the operator can preview impact.
                count_stmt = statement.replace(
                    "DELETE FROM ", "SELECT COUNT(*) FROM "
                ).replace("\n        ", " ")
                # The subquery DELETEs need to keep their WHERE shape — only
                # the outer DELETE FROM <table> is being swapped here.
                if "IN (" in count_stmt:
                    # Fall back to a simpler count of the parent table.
                    parent_table = label
                    count_stmt = (
                        f"SELECT COUNT(*) FROM {parent_table} "
                        f"WHERE id IN ({statement.split('WHERE', 1)[1]})"
                    )
                count = session.execute(
                    text(count_stmt), {"user_id": resolved_id}
                ).scalar_one()
                totals[label] = int(count)
            else:
                result = session.execute(
                    text(statement), {"user_id": resolved_id}
                )
                totals[label] = int(result.rowcount or 0)

        if restart_curriculum:
            if dry_run:
                row = session.execute(
                    text(
                        "SELECT current_week, current_day_in_week "
                        "FROM user_enrollments WHERE user_id = :user_id"
                    ),
                    {"user_id": resolved_id},
                ).first()
                if row is not None:
                    totals["user_enrollments (would reset)"] = 1
                    print(
                        f"  enrollment currently at week={row[0]} day={row[1]}"
                    )
            else:
                result = session.execute(
                    text(
                        "UPDATE user_enrollments "
                        "   SET current_week = 1, "
                        "       current_day_in_week = 1, "
                        "       last_completed_on = NULL "
                        " WHERE user_id = :user_id"
                    ),
                    {"user_id": resolved_id},
                )
                totals["user_enrollments (reset)"] = int(result.rowcount or 0)

        if dry_run:
            print("\n[DRY RUN] No rows changed. Counts that would be deleted:")
            session.rollback()
        else:
            session.commit()
            print("\nRows deleted/updated:")

        for label, count in totals.items():
            print(f"  {label}: {count}")

        if not dry_run:
            print(
                f"\nDone. Next chat session for user {resolved_id} will "
                "regenerate under the new objective-driven planner."
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
        help="Reset the user's enrollment to Week 1 Day 1.",
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
