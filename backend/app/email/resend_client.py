"""Resend email client — one httpx POST, no SDK dependency.

Sandbox note: without a verified domain, Resend only accepts the
onboarding@resend.dev sender and only delivers to the account owner's
address. Verify a domain (DKIM/SPF) before real users.
"""

import logging

import httpx

from app.core.config import settings
from app.email.exceptions import EmailAuthError, EmailSendError

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"
_TIMEOUT_S = 10.0


class ResendEmailClient:
    def __init__(self, api_key: str | None = None, from_address: str | None = None):
        self._api_key = api_key or settings.RESEND_API_KEY
        self._from = from_address or settings.EMAIL_FROM

    def send(
        self,
        *,
        to: str,
        subject: str,
        html: str,
        text: str | None = None,
        reply_to: str | None = None,
    ) -> None:
        payload: dict[str, object] = {
            "from": self._from,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        if text:
            payload["text"] = text
        if reply_to:
            payload["reply_to"] = [reply_to]
        try:
            response = httpx.post(
                RESEND_API_URL,
                json=payload,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=_TIMEOUT_S,
            )
        except httpx.HTTPError as exc:
            raise EmailSendError(f"Resend request failed: {exc}") from exc

        if response.status_code in (401, 403):
            raise EmailAuthError(
                f"Resend rejected credentials (HTTP {response.status_code})"
            )
        if response.status_code >= 300:
            # Body is logged (not raised) so provider details never leak
            # into HTTP error responses.
            logger.error(
                "Resend send failed: HTTP %s body=%s",
                response.status_code,
                response.text[:500],
            )
            raise EmailSendError(f"Resend send failed (HTTP {response.status_code})")
