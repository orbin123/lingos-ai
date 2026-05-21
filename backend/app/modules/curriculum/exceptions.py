"""Domain exceptions for the curriculum / enrollment layer."""


class NotEnrolled(Exception):
    """Raised when a user has no enrollment record."""


class EnrollmentNotActive(Exception):
    """Raised when a user's enrollment exists but is not in ACTIVE status."""
