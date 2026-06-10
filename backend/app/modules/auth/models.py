"""Authentication module models - User and related tables"""

from datetime import date, datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, Date, DateTime, Index, Integer, UniqueConstraint
from sqlalchemy import Enum as SQLAlchemyEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.mixins import CreatedAtMixin, IDMixin, TimestampMixin


ROLE_LEARNER = "learner"
ROLE_ADMIN = "admin"
ROLE_SUPER_ADMIN = "super_admin"
ADMIN_ROLE_NAMES = {ROLE_ADMIN, ROLE_SUPER_ADMIN}
DEFAULT_ROLE_NAMES = (ROLE_LEARNER, ROLE_ADMIN, ROLE_SUPER_ADMIN)


# Enums for UserProfile
class SelfAssessedLevel(str, Enum):
    """User's own opinion of their English Level"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ContentExposure(str, Enum):
    """How often user consumes English content (reading, video, etc...)"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class UserGoal(str, Enum):
    """Why the user is learning English"""
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    ACADEMIC = "academic"

# User Base Class
class User(Base, IDMixin, TimestampMixin):
    """
    Represents a user account.

    Holds only authentication-critical data (email, password hash, name).
    Learning-related data (level, goal, skill scores) lives in UserProfile.

    password_hash is nullable because Google OAuth users have no password.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    # Nullable: Google OAuth users don't have a password
    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # Email-ownership verification (OTP at registration). Google OAuth users
    # are created verified — Google asserts ownership. Pre-existing accounts
    # were backfilled to verified in the migration.
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    profile: Mapped["UserProfile"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )

    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    role_links: Mapped[list["UserRole"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def role_names(self) -> list[str]:
        """Return effective role names, including legacy superuser fallback."""
        names = {link.role.name for link in self.role_links if link.role is not None}
        if self.is_superuser:
            names.add(ROLE_SUPER_ADMIN)
        if not names:
            names.add(ROLE_LEARNER)
        return sorted(names)

    def has_any_role(self, required_roles: set[str]) -> bool:
        return bool(set(self.role_names()) & required_roles)

    def has_permission(self, permission_key: str) -> bool:
        """Return whether the user's effective roles grant a permission."""
        if ROLE_SUPER_ADMIN in set(self.role_names()):
            return True
        for user_role in self.role_links:
            role = user_role.role
            if role is None:
                continue
            if role.has_permission(permission_key):
                return True
        return False

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email!r})>"


class Role(Base, IDMixin, CreatedAtMixin):
    """Application role that can be assigned to users."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    user_links: Mapped[list["UserRole"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )

    permission_links: Mapped[list["RolePermission"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )

    def permission_keys(self) -> list[str]:
        """Return permission keys assigned to this role."""
        keys = {
            link.permission.key
            for link in self.permission_links
            if link.permission is not None
        }
        return sorted(keys)

    def has_permission(self, permission_key: str) -> bool:
        return permission_key in set(self.permission_keys())

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name!r})>"


class UserRole(Base, IDMixin, CreatedAtMixin):
    """Junction table linking users to roles."""

    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship(back_populates="role_links")
    role: Mapped["Role"] = relationship(back_populates="user_links")

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),
    )

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class Permission(Base, IDMixin, CreatedAtMixin):
    """Named permission used by admin authorization checks."""

    __tablename__ = "permissions"

    key: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)

    role_links: Mapped[list["RolePermission"]] = relationship(
        back_populates="permission",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, key={self.key!r})>"


class RolePermission(Base):
    """Junction table linking roles to permissions."""

    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )

    role: Mapped["Role"] = relationship(back_populates="permission_links")
    permission: Mapped["Permission"] = relationship(back_populates="role_links")

    def __repr__(self) -> str:
        return (
            f"<RolePermission(role_id={self.role_id}, "
            f"permission_id={self.permission_id})>"
        )


class OAuthAccount(Base, IDMixin, TimestampMixin):
    """
    Stores a linked OAuth provider account for a user.

    One user can have multiple OAuth accounts (Google, GitHub, etc.).
    provider + provider_user_id is unique — prevents duplicate links.
    """

    __tablename__ = "oauth_accounts"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # e.g. "google"
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # The user's ID on Google's side (the "sub" field from Google's token)
    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="oauth_accounts")

    def __repr__(self) -> str:
        return (
            f"<OAuthAccount(id={self.id}, provider={self.provider!r}, "
            f"user_id={self.user_id})>"
        )


# User Profile Base Class
class UserProfile(Base, IDMixin, TimestampMixin):
    """
    Learning profile for a user.

    Created automatically on signup with default values.
    Updated when the user completes the diagnosis flow (or stay default if skipped)
    """

    __tablename__ = "user_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    self_assessed_level: Mapped[SelfAssessedLevel] = mapped_column(
        SQLAlchemyEnum(SelfAssessedLevel, name="self_assessed_level_enum"),
        default=SelfAssessedLevel.BEGINNER,
        nullable=False,
    )

    daily_time_minutes: Mapped[int] = mapped_column(
        default=15,
        nullable=False,
    )

    content_exposure: Mapped[ContentExposure] = mapped_column(
        SQLAlchemyEnum(ContentExposure, name="content_exposure_enum"),
        default=ContentExposure.LOW,
        nullable=False,
    )

    goal: Mapped[UserGoal] = mapped_column(
        SQLAlchemyEnum(UserGoal, name="user_goal_enum"),
        default=UserGoal.CASUAL,
        nullable=False,
    )

    interests: Mapped[str] = mapped_column(
        String(500),
        default="",
        nullable=False,
    )

    display_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    native_language: Mapped[str | None] = mapped_column(
        String(80),
        nullable=True,
    )

    primary_goals: Mapped[str] = mapped_column(
        String(500),
        default="",
        server_default="",
        nullable=False,
    )

    personalisation_context: Mapped[str] = mapped_column(
        String(500),
        default="",
        server_default="",
        nullable=False,
    )

    # Structured view of personalisation_context (+ goals, interests, etc.),
    # produced by the Personalization Engine. Cached so lesson generation
    # doesn't pay an LLM extraction call per turn. Refreshed on profile save
    # or diagnosis completion. Nullable until first extraction.
    structured_personalisation: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )

    structured_personalisation_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    diagnosis_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    daily_practice_reminder: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    streak_reminder: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False,
    )

    weekly_progress_email: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    feature_announcements: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    # ── Streak / activity tracking ────────────────────────────────────
    # IANA timezone identifier. Used to compute the user's local "today"
    # for streak / activity-grid logic. Falls back to Asia/Kolkata.
    timezone: Mapped[str] = mapped_column(
        String(64),
        default="Asia/Kolkata",
        server_default="Asia/Kolkata",
        nullable=False,
    )

    current_streak: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False,
    )

    longest_streak: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False,
    )

    # Date-only, expressed in the user's local timezone (NOT UTC).
    last_activity_date: Mapped[date | None] = mapped_column(
        Date, nullable=True,
    )

    streak_freezes: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False,
    )

    # Local-date the celebration animation was last acknowledged by the
    # client. Prevents replay on refresh.
    last_seen_streak_animation_date: Mapped[date | None] = mapped_column(
        Date, nullable=True,
    )

    # The animation kind to play next time the dashboard loads — set
    # inside record_daily_activity, cleared once acknowledged.
    # One of: "rekindle" | "on_fire" | "frozen_to_fire" | "frozen" | None
    last_animation_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="profile")

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>"


class OtpPurpose(str, Enum):
    """What an email OTP is allowed to prove."""

    REGISTRATION = "registration"
    PASSWORD_RESET = "password_reset"
    LOGIN_STEP_UP = "login_step_up"  # reserved — wired later behind a flag


class EmailOtp(Base, IDMixin, CreatedAtMixin):
    """
    One row per OTP *send*. Only the newest unconsumed row per
    (email, purpose) is valid; issuing a new code supersedes prior rows by
    setting consumed_at. Cooldown and the hourly send cap are derived from
    row created_at timestamps, so no counters live anywhere else.

    code_hash is an HMAC-SHA256 of the code (peppered) — the raw code is
    never stored.
    """

    __tablename__ = "email_otp"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Denormalized so verification can look up by the email the user typed
    # without joining users.
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    purpose: Mapped[str] = mapped_column(String(20), nullable=False)

    code_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # Set on successful verification OR when superseded by a newer code.
    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_email_otp_email_purpose", "email", "purpose"),
    )

    def __repr__(self) -> str:
        return (
            f"<EmailOtp(id={self.id}, email={self.email!r}, "
            f"purpose={self.purpose!r})>"
        )


class AuthSession(Base, IDMixin, CreatedAtMixin):
    """
    Refresh-token session. The opaque token is stored as a SHA-256 hash and
    rotated on every refresh; family_id ties a rotation chain together so a
    replayed (already-rotated) token revokes the whole chain (theft signal).
    """

    __tablename__ = "auth_sessions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    refresh_token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )

    # First session id of the rotation chain (self for the initial login).
    family_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    device_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Logout or rotation. A revoked token presented again = reuse → revoke family.
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<AuthSession(id={self.id}, user_id={self.user_id})>"
