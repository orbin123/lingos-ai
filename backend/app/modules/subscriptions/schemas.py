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


class PlanPurchase(BaseModel):
    plan_id: str = Field(..., min_length=1, max_length=50)


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
