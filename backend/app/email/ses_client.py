"""Amazon SES email client — boto3 `send_email`, no API key in env.

Auth comes from the ambient AWS environment: in production the ECS **task
role** granted `ses:SendEmail`; locally the developer's AWS profile. This
mirrors `ResendEmailClient` (sync `send`, same error mapping) so the provider
is swappable behind `EMAIL_PROVIDER` without touching callers.

Sandbox note: a brand-new SES account is in the sandbox — it only delivers to
*verified* addresses and from a verified identity. Verify the `lingosai.com`
domain (DKIM/SPF) and request production sending access before real users.
"""

import logging

from app.core.config import settings
from app.email.exceptions import EmailAuthError, EmailSendError

logger = logging.getLogger(__name__)


class SESEmailClient:
    def __init__(
        self,
        region: str | None = None,
        from_address: str | None = None,
        client: object | None = None,
    ):
        self._region = region or settings.SES_REGION
        self._from = from_address or settings.EMAIL_FROM
        # Optional injected client for tests; otherwise built lazily so import
        # stays cheap and no AWS session is created until the first send.
        self._client = client

    def _get_client(self) -> object:
        if self._client is None:
            import boto3

            self._client = boto3.client("ses", region_name=self._region)
        return self._client

    def send(
        self,
        *,
        to: str,
        subject: str,
        html: str,
        text: str | None = None,
        reply_to: str | None = None,
    ) -> None:
        body: dict[str, object] = {"Html": {"Data": html, "Charset": "UTF-8"}}
        if text:
            body["Text"] = {"Data": text, "Charset": "UTF-8"}
        kwargs: dict[str, object] = {
            "Source": self._from,
            "Destination": {"ToAddresses": [to]},
            "Message": {
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": body,
            },
        }
        if reply_to:
            kwargs["ReplyToAddresses"] = [reply_to]

        try:
            self._get_client().send_email(**kwargs)  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001 — normalize to email errors
            if _is_auth_error(exc):
                raise EmailAuthError(f"SES rejected credentials: {exc}") from exc
            # Detail is logged (not raised) so provider internals never leak
            # into HTTP error responses.
            logger.error("SES send failed: %s", exc)
            raise EmailSendError("SES send failed") from exc


def _is_auth_error(exc: Exception) -> bool:
    """True if a boto3 SES exception is an auth/authorization failure.

    Checked structurally so we don't import botocore at module load.
    """
    response = getattr(exc, "response", None)
    if isinstance(response, dict):
        code = str(response.get("Error", {}).get("Code", ""))
        if code in (
            "AccessDenied",
            "AccessDeniedException",
            "InvalidClientTokenId",
            "SignatureDoesNotMatch",
            "UnauthorizedOperation",
        ):
            return True
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status in (401, 403):
            return True
    return False
