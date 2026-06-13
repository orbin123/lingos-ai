"""ContactService — renders and sends a contact-form submission by email.

No DB: the message goes straight to the support inbox. The email client is
injected (defaulting to the configured provider) so tests can swap in a stub.
"""

from __future__ import annotations

import logging

from app.core.config import settings
from app.email import EmailError, IEmailClient, get_default_email_client
from app.email.templates import contact_message_email
from app.modules.contact.exceptions import ContactDeliveryError
from app.modules.contact.schemas import ContactRequest

logger = logging.getLogger(__name__)


class ContactService:
    def __init__(self, email_client: IEmailClient | None = None) -> None:
        self.email_client = email_client or get_default_email_client()

    def submit(self, payload: ContactRequest) -> None:
        """Email the submission to support, with reply-to = the visitor.

        Raises:
            ContactDeliveryError: the email provider failed to deliver.
        """
        subject, html, text = contact_message_email(
            full_name=payload.full_name,
            email=payload.email,
            subject=payload.subject,
            message=payload.message,
        )
        try:
            self.email_client.send(
                to=settings.CONTACT_RECIPIENT_EMAIL,
                subject=subject,
                html=html,
                text=text,
                reply_to=payload.email,
            )
        except EmailError as exc:
            # Provider details stay in logs; the route surfaces a generic error.
            logger.error("Contact message delivery failed: %s", exc)
            raise ContactDeliveryError(str(exc)) from exc
