"""Email delivery exceptions."""


class EmailError(Exception):
    """Base class for email delivery failures."""


class EmailSendError(EmailError):
    """The provider rejected or failed to deliver the message."""


class EmailAuthError(EmailError):
    """The provider rejected our credentials (bad/expired API key)."""
