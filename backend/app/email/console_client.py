"""Dev/test email client — logs instead of sending.

With EMAIL_PROVIDER=console (the default), OTP codes show up in the backend
console, so local dev and CI need no Resend key.
"""

import logging

logger = logging.getLogger(__name__)


class ConsoleEmailClient:
    def send(
        self,
        *,
        to: str,
        subject: str,
        html: str,
        text: str | None = None,
        reply_to: str | None = None,
    ) -> None:
        logger.info(
            "EMAIL (console) to=%s reply_to=%s subject=%r body=%r",
            to,
            reply_to,
            subject,
            text or html,
        )
