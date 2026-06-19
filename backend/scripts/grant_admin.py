"""Grant (or revoke) admin / super-admin on a single user.

Production has a **fresh, separate** database (RDS), so none of your local dev
data carries over — including roles. New signups get only the `learner` role
(auth.service), and the role-seeding migration granted `super_admin` only to
users already flagged `is_superuser=true`. A fresh prod DB therefore has **no
admin**, and `PUT /admin/users/{id}/roles` requires an existing super-admin
(chicken-and-egg). This script is the one-time bootstrap: it grants the admin
roles directly, in a single transaction, reusing the app's own RoleRepository
(so `is_superuser` and the role links stay consistent).

It is **additive** by default — existing roles (e.g. `learner`) are preserved.

Usage (locally, from backend/):
    python -m scripts.grant_admin --email orbinsunny@gmail.com
    python -m scripts.grant_admin --email orbinsunny@gmail.com --dry-run
    python -m scripts.grant_admin --user-id 2 --revoke   # drop admin roles

In production, run it as a one-off ECS task using the backend task definition
(which already injects DATABASE_URL from Secrets Manager) — never put the prod
DB password in a plain env override. See docs/RUNBOOK.md for the exact
`aws ecs run-task` invocation.

Exit codes: 0 success / no-op; 1 user not found; 2 bad arguments.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.database import SessionLocal  # noqa: E402
from app.modules.auth.models import (  # noqa: E402
    ROLE_ADMIN,
    ROLE_LEARNER,
    ROLE_SUPER_ADMIN,
)
from app.modules.auth.repository import RoleRepository, UserRepository  # noqa: E402

# Granting "admin" implies the read-scoped admin role too, so the user shows up
# for both `require_admin` and `require_super_admin` guards.
_ADMIN_ROLES = {ROLE_ADMIN, ROLE_SUPER_ADMIN}


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--email", help="User email (case-insensitive).")
    target.add_argument("--user-id", type=int, help="User id.")
    parser.add_argument(
        "--revoke",
        action="store_true",
        help="Remove admin + super_admin (keep learner) instead of granting.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the change without committing.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    db = SessionLocal()
    try:
        users = UserRepository(db)
        roles = RoleRepository(db)

        user = (
            users.get_by_email(args.email)
            if args.email
            else users.get_by_id(args.user_id)
        )
        if user is None:
            ident = args.email or f"id={args.user_id}"
            print(f"ERROR: no user found for {ident}", file=sys.stderr)
            return 1

        current = set(user.role_names())
        if args.revoke:
            target = (current - _ADMIN_ROLES) or {ROLE_LEARNER}
            action = "REVOKE admin/super_admin"
        else:
            target = current | _ADMIN_ROLES
            action = "GRANT admin/super_admin"

        print(f"User: id={user.id} email={user.email}")
        print(f"  action:        {action}")
        print(f"  current roles: {sorted(current)}")
        print(f"  target roles:  {sorted(target)}")
        print(f"  is_superuser:  {user.is_superuser} -> {ROLE_SUPER_ADMIN in target}")

        if target == current:
            print("  no change needed — already in the desired state.")
            return 0

        if args.dry_run:
            print("  [dry-run] not committed.")
            return 0

        # replace_user_roles keeps the role links and is_superuser consistent.
        roles.replace_user_roles(user=user, role_names=target)
        db.commit()
        print("  committed.")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
