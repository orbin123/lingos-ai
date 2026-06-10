"""Permission catalog and default role grants."""

from __future__ import annotations

from app.modules.auth.models import ROLE_ADMIN, ROLE_LEARNER, ROLE_SUPER_ADMIN


REQUIRED_PERMISSIONS: tuple[tuple[str, str], ...] = (
    ("users.read", "View user accounts in the admin console."),
    ("users.update_status", "Activate or deactivate user accounts."),
    ("users.view_progress", "View learner progress and task history."),
    ("feedback_logs.read", "View feedback review queues and logs."),
    ("feedback_quality.review", "Review and annotate AI feedback quality."),
    ("reviews.read", "View app reviews submitted by users."),
    ("ai_logs.read", "View AI request logs."),
    ("ai_costs.read", "View AI usage and cost information."),
    ("ai_quality.read", "View AI evaluation quality metrics."),
    ("payments.read", "View limited payment and billing information."),
    ("subscriptions.manage", "Manage subscription access and periods."),
    ("audit_logs.read", "View admin audit logs."),
    ("admins.manage", "Assign or remove administrator roles."),
    ("roles.manage", "Update role permission grants."),
)

ALL_PERMISSION_KEYS = tuple(key for key, _description in REQUIRED_PERMISSIONS)

ADMIN_PERMISSION_KEYS = (
    "users.read",
    "users.update_status",
    "users.view_progress",
    "feedback_logs.read",
    "feedback_quality.review",
    "reviews.read",
    "ai_logs.read",
    "ai_costs.read",
    "ai_quality.read",
    "payments.read",
    "audit_logs.read",
)

DEFAULT_ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    ROLE_LEARNER: (),
    ROLE_ADMIN: ADMIN_PERMISSION_KEYS,
    ROLE_SUPER_ADMIN: ALL_PERMISSION_KEYS,
}
