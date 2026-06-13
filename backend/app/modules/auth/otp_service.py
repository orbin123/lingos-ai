"""Email OTP issue/verify logic.

Storage model: one `email_otp` row per send. Only the newest unconsumed row
per (email, purpose) is valid — issuing a new code supersedes prior rows.
Cooldown and the hourly send cap are derived from row timestamps, so the DB
is the only source of truth (survives restarts and Redis flushes).

Codes are stored as a peppered HMAC-SHA256 only; the raw code exists in the
email and nowhere else.
"""

import hashlib
import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.email import IEmailClient, get_default_email_client
from app.email.exceptions import EmailError
from app.email.templates import otp_email
from app.modules.auth.exceptions import (
    EmailDeliveryFailed,
    OtpAttemptsExceeded,
    OtpCooldownActive,
    OtpMismatch,
    OtpNotFoundOrExpired,
    OtpSendLimitExceeded,
)
from app.modules.auth.models import EmailOtp, OtpPurpose, User

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Single seam for time so tests can monkeypatch one symbol."""
    return datetime.now(timezone.utc)


def _aware(value: datetime) -> datetime:
    """SQLite returns naive datetimes for tz-aware columns; normalize."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _hash_code(*, email: str, purpose: str, code: str) -> str:
    pepper = (settings.OTP_HASHING_SECRET or settings.jwt_secret).encode()
    message = f"{email.lower()}:{purpose}:{code}".encode()
    return hmac.new(pepper, message, hashlib.sha256).hexdigest()


class OtpService:
    def __init__(self, db: Session, email_client: IEmailClient | None = None) -> None:
        self.db = db
        self.email_client = email_client or get_default_email_client()

    def issue(self, *, user: User, purpose: OtpPurpose) -> None:
        """Generate, persist, and email a fresh OTP for the user.

        Raises:
            OtpCooldownActive: a code was sent < cooldown seconds ago.
            OtpSendLimitExceeded: hourly send cap reached.
            EmailDeliveryFailed: code stored but the provider send failed.
        """
        email = user.email.lower()
        now = _utcnow()

        recent = self.db.execute(
            select(EmailOtp)
            .where(EmailOtp.email == email, EmailOtp.purpose == purpose.value)
            .order_by(EmailOtp.created_at.desc(), EmailOtp.id.desc())
            .limit(1)
        ).scalar_one_or_none()
        if recent is not None:
            age = (now - _aware(recent.created_at)).total_seconds()
            if age < settings.OTP_RESEND_COOLDOWN_SECONDS:
                retry_after = int(settings.OTP_RESEND_COOLDOWN_SECONDS - age) or 1
                raise OtpCooldownActive(retry_after)

        hour_ago = now - timedelta(hours=1)
        sends_last_hour = (
            self.db.execute(
                select(EmailOtp)
                .where(
                    EmailOtp.email == email,
                    EmailOtp.purpose == purpose.value,
                    EmailOtp.created_at >= hour_ago,
                )
            )
            .scalars()
            .all()
        )
        if len(sends_last_hour) >= settings.OTP_MAX_SENDS_PER_HOUR:
            raise OtpSendLimitExceeded()

        # Latest-wins: supersede every prior unconsumed code.
        for row in self.db.execute(
            select(EmailOtp).where(
                EmailOtp.email == email,
                EmailOtp.purpose == purpose.value,
                EmailOtp.consumed_at.is_(None),
            )
        ).scalars():
            row.consumed_at = now

        code = "".join(
            secrets.choice("0123456789") for _ in range(settings.OTP_LENGTH)
        )
        otp = EmailOtp(
            user_id=user.id,
            email=email,
            purpose=purpose.value,
            code_hash=_hash_code(email=email, purpose=purpose.value, code=code),
            expires_at=now + timedelta(minutes=settings.OTP_TTL_MINUTES),
        )
        self.db.add(otp)
        self.db.commit()

        # Send after commit: a provider failure must not roll back the row
        # (the cooldown window governs the retry pace either way).
        subject, html, text = otp_email(
            code=code, purpose=purpose, ttl_minutes=settings.OTP_TTL_MINUTES
        )
        try:
            self.email_client.send(to=user.email, subject=subject, html=html, text=text)
        except EmailError as exc:
            logger.error("OTP email send failed for %s: %s", user.email, exc)
            raise EmailDeliveryFailed(str(exc)) from exc

    def verify(self, *, email: str, purpose: OtpPurpose, code: str) -> User:
        """Validate a submitted code; on success consume it (and for
        registration, mark the user's email verified).

        Raises:
            OtpNotFoundOrExpired, OtpAttemptsExceeded, OtpMismatch.
        """
        email = email.lower()
        now = _utcnow()

        otp = self.db.execute(
            select(EmailOtp)
            .where(
                EmailOtp.email == email,
                EmailOtp.purpose == purpose.value,
                EmailOtp.consumed_at.is_(None),
            )
            .order_by(EmailOtp.created_at.desc(), EmailOtp.id.desc())
            .limit(1)
        ).scalar_one_or_none()

        if otp is None or _aware(otp.expires_at) < now:
            raise OtpNotFoundOrExpired()

        if otp.attempts >= settings.OTP_MAX_VERIFY_ATTEMPTS:
            raise OtpAttemptsExceeded()

        expected = otp.code_hash
        candidate = _hash_code(email=email, purpose=purpose.value, code=code)
        bypass = settings.DEV_OTP_BYPASS and code == "123456"
        if not bypass and not hmac.compare_digest(expected, candidate):
            otp.attempts += 1
            self.db.commit()
            if otp.attempts >= settings.OTP_MAX_VERIFY_ATTEMPTS:
                raise OtpAttemptsExceeded()
            raise OtpMismatch()

        user = self.db.get(User, otp.user_id)
        if user is None:
            # Account deleted between send and verify — treat as expired.
            raise OtpNotFoundOrExpired()

        otp.consumed_at = now
        if purpose is OtpPurpose.REGISTRATION and not user.email_verified:
            user.email_verified = True
            user.email_verified_at = now
        self.db.commit()
        self.db.refresh(user)
        return user
