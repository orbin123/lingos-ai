"""Domain exceptions for the contact module.

Routes translate these into HTTPException at the boundary.
"""

from __future__ import annotations


class ContactError(Exception):
    """Base class for any contact domain error."""


class ContactDeliveryError(ContactError):
    """The contact message could not be delivered (email provider failed)."""
