"""Pydantic schemas for admin API contracts."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AdminUserListItem(BaseModel):
    id: int
    name: str
    email: str
    role: str
    roles: list[str]
    is_active: bool
    created_at: datetime


class AdminRecentUser(BaseModel):
    id: int
    name: str
    email: str
    role: str
    roles: list[str]
    is_active: bool
    created_at: datetime


class AdminSummary(BaseModel):
    total_users: int
    active_users: int
    tasks_completed: int
    feedback_generated: int
    ai_requests_24h: int = 0
    ai_errors_24h: int = 0
    pending_feedback_reviews: int = 0
    recent_users: list[AdminRecentUser]


class AdminUserProfile(BaseModel):
    display_name: str | None = None
    phone_number: str | None = None
    country: str | None = None
    native_language: str | None = None
    self_assessed_level: str | None = None
    goal: str | None = None
    interests: list[str] = Field(default_factory=list)
    diagnosis_completed: bool = False


class AdminSkillScore(BaseModel):
    skill_id: int
    skill_name: str
    score: float
    source: str


class AdminRecentTask(BaseModel):
    id: int
    task_id: int
    title: str
    task_type: str
    status: str
    completed_at: datetime | None
    created_at: datetime


class AdminRecentFeedback(BaseModel):
    id: int
    task_title: str
    task_type: str
    score: float
    body: dict
    created_at: datetime


class AdminUserDetail(AdminUserListItem):
    profile: AdminUserProfile | None = None
    skill_scores: list[AdminSkillScore]
    recent_tasks: list[AdminRecentTask]
    recent_feedback: list[AdminRecentFeedback]


class UserStatusUpdate(BaseModel):
    is_active: bool


class AdminPermissionRead(BaseModel):
    id: int
    key: str
    description: str
    created_at: datetime


class AdminRoleRead(BaseModel):
    id: int
    name: str
    permissions: list[str]
    user_count: int
    created_at: datetime


class UserRolesUpdate(BaseModel):
    roles: list[str] = Field(min_length=1, max_length=3)


class RolePermissionsUpdate(BaseModel):
    permission_keys: list[str] = Field(max_length=32)


class TaskTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    task_type: str
    difficulty: int
    status: str
    content: dict
    created_at: datetime
    updated_at: datetime


class TaskTemplateCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    task_type: str = Field(min_length=1, max_length=80)
    difficulty: int = Field(default=1, ge=1, le=10)
    status: str = Field(default="draft")
    content: dict = Field(default_factory=dict)


class TaskTemplateUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    task_type: str | None = Field(default=None, min_length=1, max_length=80)
    difficulty: int | None = Field(default=None, ge=1, le=10)
    status: str | None = None
    content: dict | None = None


class AdminLogUser(BaseModel):
    id: int
    name: str
    email: str


class AdminAuditLogRead(BaseModel):
    id: int
    admin_user_id: int | None
    admin: AdminLogUser | None = None
    action: str
    resource_type: str
    resource_id: str
    old_value: dict | None = None
    new_value: dict | None = None
    ip_address: str | None = None
    created_at: datetime


class AIRequestLogRead(BaseModel):
    id: int
    user_id: int | None
    user: AdminLogUser | None = None
    trace_id: str | None = None
    agent_name: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    latency_ms: int | None = None
    status: str
    error_message: str | None = None
    prompt_version: str | None = None
    created_at: datetime


class FeedbackReviewItem(BaseModel):
    id: int
    user: AdminLogUser | None = None
    task_title: str
    user_response: dict
    user_response_raw_text: str | None = None
    ai_feedback: dict
    score: float
    review_status: str
    reviewed_by: AdminLogUser | None = None
    reviewed_at: datetime | None = None
    admin_note: str | None = None
    created_at: datetime


class FeedbackReviewUpdate(BaseModel):
    review_status: Literal["pending", "approved", "flagged", "fixed"]
    admin_note: str | None = Field(default=None, max_length=2000)


class PaymentRead(BaseModel):
    id: int
    user_id: int
    user: AdminLogUser | None = None
    provider: str
    provider_payment_id: str | None = None
    amount: float
    currency: str
    status: str
    paid_at: datetime | None = None
    created_at: datetime


class SubscriptionRead(BaseModel):
    id: int
    user_id: int
    user: AdminLogUser | None = None
    provider: str
    provider_customer_id: str | None = None
    provider_subscription_id: str | None = None
    plan_name: str
    status: str
    trial_ends_at: datetime | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserBillingRead(BaseModel):
    user: AdminLogUser
    subscription: SubscriptionRead | None = None
    payments: list[PaymentRead]


class SubscriptionUpdate(BaseModel):
    plan_name: str | None = Field(default=None, min_length=1, max_length=120)
    status: str | None = Field(default=None, min_length=1, max_length=40)
    trial_ends_at: datetime | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
