"""Schemas for purchase and notification settings."""

from datetime import datetime

from pydantic import BaseModel, Field


class NotificationSettings(BaseModel):
    daily_practice_reminder: bool = True
    streak_reminder: bool = True
    weekly_progress_email: bool = False
    feature_announcements: bool = False


class NotificationSettingsUpdate(BaseModel):
    daily_practice_reminder: bool | None = None
    streak_reminder: bool | None = None
    weekly_progress_email: bool | None = None
    feature_announcements: bool | None = None


class PlanSelect(BaseModel):
    plan_id: str = Field(..., min_length=1, max_length=50)


class CreateOrderIn(BaseModel):
    plan_id: str = Field(..., min_length=1, max_length=50)


class CreateOrderOut(BaseModel):
    """What the Razorpay Checkout widget needs. Amount is in paise and
    comes from PLAN_CATALOG — never from the client."""

    order_id: str
    amount: int
    currency: str
    key_id: str
    plan_id: str
    plan_name: str


class PaymentVerifyIn(BaseModel):
    razorpay_order_id: str = Field(..., min_length=1, max_length=255)
    razorpay_payment_id: str = Field(..., min_length=1, max_length=255)
    razorpay_signature: str = Field(..., min_length=1, max_length=512)


class EntitlementRead(BaseModel):
    """The user's current entitlement, derived by resolve_access.

    This is what GET /api/subscriptions/me returns; legacy one-time
    purchases surface here as access_state="active".
    """

    access_state: str
    subscription_status: str | None = None
    plan_id: str | None = None
    plan_name: str | None = None
    amount: float | None = None
    currency: str | None = None
    trial_started_at: datetime | None = None
    trial_ends_at: datetime | None = None
    days_remaining: int | None = None
    current_period_end: datetime | None = None


class PaymentDetailRead(BaseModel):
    """Server-verified proof for the Payment Success page.

    The route that serves this is user-scoped (filters by current_user.id),
    so a learner can only ever read their own payment — no IDOR. Amounts are
    in the catalog's display unit (rupees), not paise. `method` is null until
    the webhook lands (the checkout `verify` fast-path does not set it), so the
    success page renders it defensively. `subscription_status` is the live,
    lazy-expiry-aware access state from `resolve_access`.
    """

    provider_payment_id: str | None = None
    provider_order_id: str | None = None
    amount: float
    currency: str
    status: str
    method: str | None = None
    paid_at: datetime | None = None
    plan_id: str | None = None
    plan_name: str | None = None
    subscription_status: str | None = None
    current_period_end: datetime | None = None


class PurchaseRead(BaseModel):
    id: int
    user_id: int
    plan_id: str
    plan_name: str
    amount_paid: float
    currency: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
