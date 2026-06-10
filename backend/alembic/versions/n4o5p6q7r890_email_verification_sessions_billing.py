"""email verification, auth sessions, billing groundwork

Revision ID: n4o5p6q7r890
Revises: m3n4o5p6q789
Create Date: 2026-06-10 12:00:00.000000

Phase 0 of the payment/subscription/email-verification plan
(docs/payment_subscription_and_email_verification_plan.md):

- users.email_verified(+at), backfilled to true for every pre-existing
  account (password and OAuth alike) so nobody is locked out.
- email_otp: one row per OTP send; code stored as peppered HMAC only.
- auth_sessions: hashed, rotated refresh tokens with family-based reuse
  (theft) detection.
- subscriptions: plan_id / trial_started_at / cancelled_at so the stored row
  becomes the authoritative entitlement (replacing the derived trial).
- payments: Razorpay order id + method + failure_reason.
- payment_events: webhook idempotency (unique event_id) + raw-payload audit.

Status columns stay plain strings validated by Python StrEnums — no DB enum
DDL (SQLite test compatibility; consistent with existing status columns).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "n4o5p6q7r890"
down_revision: Union[str, Sequence[str], None] = "m3n4o5p6q789"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users: email verification ─────────────────────────────────────
    op.add_column(
        "users",
        sa.Column(
            "email_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "users",
        sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True),
    )
    # Every account that exists before this migration is trusted — the OTP
    # gate applies to new signups only.
    op.execute(
        "UPDATE users SET email_verified = true, email_verified_at = now()"
    )

    # ── email_otp ─────────────────────────────────────────────────────
    op.create_table(
        "email_otp",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("purpose", sa.String(length=20), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(op.f("ix_email_otp_user_id"), "email_otp", ["user_id"])
    op.create_index(op.f("ix_email_otp_expires_at"), "email_otp", ["expires_at"])
    op.create_index("ix_email_otp_email_purpose", "email_otp", ["email", "purpose"])

    # ── auth_sessions ─────────────────────────────────────────────────
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("refresh_token_hash", sa.String(length=64), nullable=False),
        sa.Column("family_id", sa.Integer(), nullable=True),
        sa.Column("device_id", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(op.f("ix_auth_sessions_user_id"), "auth_sessions", ["user_id"])
    op.create_index(
        op.f("ix_auth_sessions_refresh_token_hash"),
        "auth_sessions",
        ["refresh_token_hash"],
        unique=True,
    )
    op.create_index(op.f("ix_auth_sessions_family_id"), "auth_sessions", ["family_id"])

    # ── subscriptions: stored entitlement columns ─────────────────────
    op.add_column(
        "subscriptions", sa.Column("plan_id", sa.String(length=50), nullable=True)
    )
    op.add_column(
        "subscriptions",
        sa.Column("trial_started_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "subscriptions",
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f("ix_subscriptions_plan_id"), "subscriptions", ["plan_id"])
    op.create_index(
        "ix_subscriptions_user_status", "subscriptions", ["user_id", "status"]
    )

    # ── payments: Razorpay order linkage ──────────────────────────────
    op.add_column(
        "payments",
        sa.Column("provider_order_id", sa.String(length=255), nullable=True),
    )
    op.add_column("payments", sa.Column("method", sa.String(length=40), nullable=True))
    op.add_column(
        "payments", sa.Column("failure_reason", sa.String(length=255), nullable=True)
    )
    op.create_index(
        op.f("ix_payments_provider_order_id"), "payments", ["provider_order_id"]
    )

    # ── payment_events: webhook idempotency + audit ───────────────────
    op.create_table(
        "payment_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("event_id", sa.String(length=255), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column(
            "payload",
            sa.JSON().with_variant(postgresql.JSONB(), "postgresql"),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(op.f("ix_payment_events_provider"), "payment_events", ["provider"])
    op.create_index(
        op.f("ix_payment_events_event_id"),
        "payment_events",
        ["event_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_payment_events_event_id"), table_name="payment_events")
    op.drop_index(op.f("ix_payment_events_provider"), table_name="payment_events")
    op.drop_table("payment_events")

    op.drop_index(op.f("ix_payments_provider_order_id"), table_name="payments")
    op.drop_column("payments", "failure_reason")
    op.drop_column("payments", "method")
    op.drop_column("payments", "provider_order_id")

    op.drop_index("ix_subscriptions_user_status", table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_plan_id"), table_name="subscriptions")
    op.drop_column("subscriptions", "cancelled_at")
    op.drop_column("subscriptions", "trial_started_at")
    op.drop_column("subscriptions", "plan_id")

    op.drop_index(op.f("ix_auth_sessions_family_id"), table_name="auth_sessions")
    op.drop_index(
        op.f("ix_auth_sessions_refresh_token_hash"), table_name="auth_sessions"
    )
    op.drop_index(op.f("ix_auth_sessions_user_id"), table_name="auth_sessions")
    op.drop_table("auth_sessions")

    op.drop_index("ix_email_otp_email_purpose", table_name="email_otp")
    op.drop_index(op.f("ix_email_otp_expires_at"), table_name="email_otp")
    op.drop_index(op.f("ix_email_otp_user_id"), table_name="email_otp")
    op.drop_table("email_otp")

    op.drop_column("users", "email_verified_at")
    op.drop_column("users", "email_verified")
