"""Pydantic schemas for auth module - API boundary contracts"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.modules.curriculum.schemas import EnrollmentRead
from app.modules.subscriptions.schemas import NotificationSettings

class UserCreate(BaseModel):
    """Input schema for signup. What the client sends."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=100)

class UserLogin(BaseModel):
    """Input schema for login"""
    email: EmailStr
    password: str

class UserOut(BaseModel):
    """Output schema - What we send back to the client. Never includes password_hash"""
    id: int
    email: EmailStr
    name: str
    display_name: str
    created_at: datetime
    auth_provider: str = "password"
    is_superuser: bool = False
    is_active: bool = True
    roles: list[str] = Field(default_factory=lambda: ["learner"])
    role: str = "learner"
    diagnosis_completed: bool = False  # tells frontend where to send the user
    enrollment: EnrollmentRead | None = None
    phone_number: str | None = None
    country: str | None = None
    native_language: str | None = None
    primary_goals: list[str] = Field(default_factory=list)
    personalisation_context: str = ""
    # Structured view derived by the Personalization Engine. Surfaced so the
    # frontend can show "what the AI knows about you" and gate copy on
    # extraction_source (llm / fallback / empty).
    structured_personalisation: dict[str, Any] | None = None
    self_assessed_level: str | None = None
    goal: str | None = None
    interests: list[str] = Field(default_factory=list)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Editable account/profile fields for PATCH /auth/me."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=1, max_length=128)
    phone_number: str | None = Field(default=None, max_length=40)
    country: str | None = Field(default=None, max_length=80)
    native_language: str | None = Field(default=None, max_length=80)
    primary_goals: list[str] | None = Field(default=None, max_length=8)
    personalisation_context: str | None = Field(default=None, max_length=500)

class TokenOut(BaseModel):
    """Output Schema returned after successful login."""
    access_token: str
    token_type: str = "bearer"
