"""Auth module exceptions."""


class EmailAlreadyExists(Exception):
    """Raised when attempting to signup with an email already in use."""

    pass


class InvalidCredentials(Exception):
    """Raised when login Credentials don't match."""

    pass


class EmailNotVerified(Exception):
    """Raised on login when the account exists, the password is correct,
    but the email has not been verified yet."""

    pass


class PasswordLoginUnavailable(Exception):
    """Raised on email/password login for an account that has no password
    (signed up via Google OAuth). The user should continue with Google."""

    pass


class OtpNotFoundOrExpired(Exception):
    """No active (unconsumed, unexpired) OTP for this email+purpose."""

    pass


class OtpMismatch(Exception):
    """The submitted code does not match the active OTP."""

    pass


class OtpAttemptsExceeded(Exception):
    """Too many wrong codes against the active OTP — request a new one."""

    pass


class OtpCooldownActive(Exception):
    """A code was sent too recently; retry after `retry_after` seconds."""

    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(f"Resend available in {retry_after}s")


class OtpSendLimitExceeded(Exception):
    """Hourly OTP send cap reached for this email+purpose."""

    pass


class EmailDeliveryFailed(Exception):
    """The OTP was created but the email could not be delivered."""

    pass


class InvalidRefreshToken(Exception):
    """Refresh token missing, unknown, expired, revoked, or reused."""

    pass
