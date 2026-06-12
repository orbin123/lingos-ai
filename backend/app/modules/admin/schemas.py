"""Pydantic schemas for admin API contracts."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


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
    # Estimated AI spend and mean latency over the last 24h (derived from logs).
    ai_cost_24h: float = 0.0
    ai_avg_latency_ms_24h: int | None = None
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


class UserProgressItem(BaseModel):
    """A learner's at-a-glance progress for the admin User Progress list."""

    user_id: int
    name: str
    email: str
    plan_id: str | None = None
    plan_name: str | None = None
    purchase_complete: bool = False
    access_expires_at: datetime | None = None
    activities_completed: int = 0
    # Mean of the learner's per-sub-skill display scores (0–10), or None if
    # the learner has no scored skills yet.
    dashboard_score: float | None = None
    subskill_scores: list[AdminSkillScore] = Field(default_factory=list)


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
    # Estimated USD cost, derived from model + tokens at read time (None when
    # the model isn't in the pricing table or tokens are missing).
    cost_usd: float | None = None
    latency_ms: int | None = None
    status: str
    error_message: str | None = None
    prompt_version: str | None = None
    created_at: datetime


class AIQualityRow(BaseModel):
    """Rolling mean quality scores for one judged target type."""

    target_type: str
    judged_count: int
    mean_accuracy: float | None = None
    mean_relevance: float | None = None
    mean_helpfulness: float | None = None
    mean_correctness: float | None = None
    mean_faithfulness: float | None = None


class AIQualityWorst(BaseModel):
    """A low-scoring judged output, surfaced for human review."""

    id: int
    trace_id: str | None = None
    target_type: str
    target_id: str | None = None
    judge_model: str
    accuracy: float | None = None
    relevance: float | None = None
    helpfulness: float | None = None
    correctness: float | None = None
    faithfulness: float | None = None
    rationale: str | None = None
    created_at: datetime


class AIQualityTimeSeriesPoint(BaseModel):
    """Mean quality scores for one (day, target_type) bucket (Part B Phase 3)."""

    date: str  # YYYY-MM-DD (UTC)
    target_type: str
    judged_count: int
    mean_accuracy: float | None = None
    mean_relevance: float | None = None
    mean_helpfulness: float | None = None
    mean_correctness: float | None = None
    mean_faithfulness: float | None = None


class AIQualityReport(BaseModel):
    """Aggregated LLM-as-judge quality over a rolling window (Part B Phase 2)."""

    days: int
    judged_count: int
    means: list[AIQualityRow]
    worst: list[AIQualityWorst]
    # Per-day means per target_type, oldest → newest (Part B Phase 3).
    series: list[AIQualityTimeSeriesPoint] = []


class FeedbackReviewItem(BaseModel):
    """One reviewable piece of feedback — either a per-activity "specific"
    feedback row or a session-level "rag" Coach's Note."""

    feedback_type: Literal["specific", "rag"]
    feedback_id: int
    user: AdminLogUser | None = None
    # archetype id (specific) or day_id (rag) — context for the reviewer.
    context_label: str

    # Specific-feedback fields.
    score: float | None = None
    summary: str | None = None
    did_well: list[str] = Field(default_factory=list)
    mistakes: list[dict] = Field(default_factory=list)
    next_tip: str | None = None

    # RAG-feedback fields.
    mentor_note: str | None = None
    # Learner's thumbs on the Coach's Note, if they rated it.
    rating: Literal["like", "dislike"] | None = None

    # Review annotation (defaults represent the lazy "not yet reviewed" state).
    review_status: str = "pending"
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
    provider_order_id: str | None = None
    amount: float
    currency: str
    status: str
    method: str | None = None
    failure_reason: str | None = None
    paid_at: datetime | None = None
    created_at: datetime


class SubscriptionRead(BaseModel):
    id: int
    user_id: int
    user: AdminLogUser | None = None
    provider: str
    provider_customer_id: str | None = None
    provider_subscription_id: str | None = None
    plan_id: str | None = None
    plan_name: str
    status: str
    trial_started_at: datetime | None = None
    trial_ends_at: datetime | None = None
    cancelled_at: datetime | None = None
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


class SubscriberItem(BaseModel):
    """A paying learner — a paid `Subscription` row or legacy `Purchase`."""

    user_id: int
    name: str
    email: str
    plan_id: str | None = None
    plan_name: str | None = None
    amount_paid: float | None = None
    currency: str | None = None
    # "active" | "expired" | "cancelled" | "paused" (legacy Purchase only)
    status: str
    purchased_at: datetime | None = None
    access_expires_at: datetime | None = None


class TrialUserItem(BaseModel):
    """A non-paying learner — trial state read from the stored subscription."""

    user_id: int
    name: str
    email: str
    # "unverified" | "not_started" | "trial" | "expired"
    status: str
    email_verified: bool = True
    signed_up_at: datetime
    trial_started_at: datetime | None = None
    trial_ends_at: datetime | None = None


class SubscribersOverview(BaseModel):
    """Paying subscribers and trial users kept as distinct groups."""

    subscribers: list[SubscriberItem]
    trials: list[TrialUserItem]


class SubscriberAccessUpdate(BaseModel):
    """Admin extends or expires a subscriber's 2-year access window."""

    access_expires_at: datetime


class SubscriptionAdminUpdate(BaseModel):
    """Admin edits a user's subscription row (extend/grant trial, set
    expiry, fix a stuck state). All fields optional — only provided fields
    are applied. Creating a row for a user without one supports
    "grant trial"."""

    status: str | None = Field(default=None, min_length=1, max_length=40)
    plan_id: str | None = Field(default=None, min_length=1, max_length=50)
    trial_started_at: datetime | None = None
    trial_ends_at: datetime | None = None
    current_period_end: datetime | None = None


class ExpireTrialsResult(BaseModel):
    expired: int


class AppReviewItem(BaseModel):
    """A user's review of the application, for the admin User Reviews list."""

    id: int
    user: AdminLogUser | None = None
    rating: int
    title: str | None = None
    body: str | None = None
    status: str
    created_at: datetime
