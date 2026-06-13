"""Pydantic shapes for the contact REST API."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactRequest(BaseModel):
    """Body for `POST /contact` — a visitor's contact-form submission."""

    full_name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    subject: str = Field(..., min_length=1, max_length=150)
    message: str = Field(..., min_length=1, max_length=4000)

    @field_validator("full_name", "subject", "message")
    @classmethod
    def _strip_and_require(cls, value: str) -> str:
        # Trim then re-check non-empty so whitespace-only fields are rejected.
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped


class ContactResponse(BaseModel):
    """Result of a contact submission."""

    ok: bool = True
    message: str = "Your message has been sent successfully."
