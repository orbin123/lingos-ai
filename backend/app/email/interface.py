"""Email delivery contract.

Mirrors the app/ai capability pattern: a small Protocol, concrete provider
clients, and a get_default_email_client() factory so the provider is
swappable (console in dev/tests, Resend in prod) without touching callers.
"""

from typing import Protocol


class IEmailClient(Protocol):
    """Sends one transactional email. Sync on purpose — the auth routes are
    sync `def` endpoints and providers are a single short HTTP call."""

    def send(
        self,
        *,
        to: str,
        subject: str,
        html: str,
        text: str | None = None,
        reply_to: str | None = None,
    ) -> None:
        """Deliver an email or raise EmailSendError.

        `reply_to` lets a recipient reply to a third party (e.g. the contact
        form routes replies back to the visitor, not the sender address).
        """
        ...
