"""Refresh-token sessions: create, rotate, revoke.

The raw token is a 384-bit opaque string handed to the browser as an
httpOnly cookie; only its SHA-256 hash is stored. Every refresh rotates the
token (old row revoked, new row inserted in the same family). Presenting an
already-rotated token is treated as theft and revokes the whole family.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.auth.exceptions import InvalidRefreshToken
from app.modules.auth.models import AuthSession, User

REFRESH_COOKIE_NAME = "lingosai_refresh"
# Scoped so the browser only attaches the cookie to /auth/* requests.
REFRESH_COOKIE_PATH = "/auth"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime) -> datetime:
    """SQLite returns naive datetimes for tz-aware columns; normalize."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


class SessionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(
        self,
        *,
        user: User,
        remember: bool = False,
        device_id: str | None = None,
        user_agent: str | None = None,
        ip: str | None = None,
    ) -> tuple[str, AuthSession]:
        """Start a new session (login/verify). Returns (raw_token, row)."""
        raw = secrets.token_urlsafe(48)
        days = (
            settings.REFRESH_TOKEN_REMEMBER_DAYS
            if remember
            else settings.REFRESH_TOKEN_TTL_DAYS
        )
        session = AuthSession(
            user_id=user.id,
            refresh_token_hash=_hash_token(raw),
            device_id=device_id,
            user_agent=(user_agent or "")[:255] or None,
            ip=ip,
            expires_at=_utcnow() + timedelta(days=days),
        )
        self.db.add(session)
        self.db.flush()
        # A fresh login starts its own rotation chain.
        session.family_id = session.id
        self.db.commit()
        return raw, session

    def rotate(self, *, raw_token: str) -> tuple[str, AuthSession]:
        """Exchange a valid refresh token for a new one (rotation).

        Raises InvalidRefreshToken for unknown/expired tokens. A revoked
        token being replayed revokes its entire family first (theft signal).
        """
        now = _utcnow()
        current = self._get_by_raw(raw_token)
        if current is None:
            raise InvalidRefreshToken()

        if current.revoked_at is not None:
            # Reuse after rotation — someone is replaying an old token.
            self._revoke_family(current.family_id or current.id, now=now)
            self.db.commit()
            raise InvalidRefreshToken()

        if _aware(current.expires_at) < now:
            raise InvalidRefreshToken()

        current.revoked_at = now
        current.last_used_at = now

        new_raw = secrets.token_urlsafe(48)
        # Carry the original window length so "remember me" survives rotation.
        window = _aware(current.expires_at) - _aware(current.created_at)
        replacement = AuthSession(
            user_id=current.user_id,
            refresh_token_hash=_hash_token(new_raw),
            family_id=current.family_id or current.id,
            device_id=current.device_id,
            user_agent=current.user_agent,
            ip=current.ip,
            expires_at=now + window,
        )
        self.db.add(replacement)
        self.db.commit()
        return new_raw, replacement

    def revoke(self, *, raw_token: str) -> None:
        """Logout: revoke the presented session. Idempotent, never raises."""
        session = self._get_by_raw(raw_token)
        if session is not None and session.revoked_at is None:
            session.revoked_at = _utcnow()
            self.db.commit()

    def revoke_all_for_user(self, *, user_id: int) -> None:
        """Kill every session for a user (e.g. after a password reset)."""
        now = _utcnow()
        rows = self.db.execute(
            select(AuthSession).where(
                AuthSession.user_id == user_id,
                AuthSession.revoked_at.is_(None),
            )
        ).scalars()
        for row in rows:
            row.revoked_at = now
        self.db.commit()

    def _get_by_raw(self, raw_token: str) -> AuthSession | None:
        return self.db.execute(
            select(AuthSession).where(
                AuthSession.refresh_token_hash == _hash_token(raw_token)
            )
        ).scalar_one_or_none()

    def _revoke_family(self, family_id: int, *, now: datetime) -> None:
        rows = self.db.execute(
            select(AuthSession).where(
                AuthSession.family_id == family_id,
                AuthSession.revoked_at.is_(None),
            )
        ).scalars()
        for row in rows:
            row.revoked_at = now
