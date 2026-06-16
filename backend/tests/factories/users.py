"""User/role/profile factories returning persisted ORM rows.

Replaces the per-file `User(email=..., password_hash="x", name="...")` +
`UserRole(role=Role(name=...))` boilerplate scattered across the auth/admin/
preferences tests. Roles are get-or-created so multiple users can share a role
without tripping the unique constraint on `roles.name`.
"""

from __future__ import annotations

from itertools import count

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.modules.auth.models import (
    ROLE_ADMIN,
    ROLE_LEARNER,
    ROLE_SUPER_ADMIN,
    Role,
    User,
    UserProfile,
    UserRole,
)

# Process-wide counter → unique emails without the caller having to think.
_email_seq = count(1)

# Default password every factory user gets; handy for login round-trip tests.
DEFAULT_PASSWORD = "Password123!"


def _get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter_by(name=name).first()
    if role is None:
        role = Role(name=name)
        db.add(role)
        db.flush()
    return role


def make_user(
    db: Session,
    *,
    email: str | None = None,
    password: str | None = DEFAULT_PASSWORD,
    name: str = "Test Learner",
    verified: bool = True,
    roles: tuple[str, ...] = (ROLE_LEARNER,),
    is_superuser: bool = False,
    with_profile: bool = True,
    timezone: str = "Asia/Kolkata",
) -> User:
    """Create and persist a `User` (+ optional profile + roles)."""
    user = User(
        email=email or f"user{next(_email_seq)}@example.com",
        password_hash=hash_password(password) if password else None,
        name=name,
        email_verified=verified,
        is_superuser=is_superuser,
    )
    db.add(user)
    for role_name in roles:
        # Add the link row explicitly (user already in session) so the
        # association is unambiguous and no cascade SAWarning fires.
        db.add(UserRole(user=user, role=_get_or_create_role(db, role_name)))
    db.flush()
    if with_profile:
        db.add(UserProfile(user_id=user.id, timezone=timezone))
    db.commit()
    return user


def make_verified_user(db: Session, **kwargs) -> User:
    """A verified learner (the common case)."""
    kwargs.setdefault("verified", True)
    return make_user(db, **kwargs)


def make_unverified_user(db: Session, **kwargs) -> User:
    kwargs["verified"] = False
    return make_user(db, **kwargs)


def make_admin(db: Session, **kwargs) -> User:
    """Learner + admin (admins typically also hold the learner surface)."""
    kwargs.setdefault("roles", (ROLE_LEARNER, ROLE_ADMIN))
    kwargs.setdefault("name", "Test Admin")
    return make_user(db, **kwargs)


def make_super_admin(db: Session, **kwargs) -> User:
    kwargs.setdefault("roles", (ROLE_LEARNER, ROLE_SUPER_ADMIN))
    kwargs.setdefault("name", "Test SuperAdmin")
    return make_user(db, **kwargs)
