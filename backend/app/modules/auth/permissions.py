"""Permission catalog and default role grants."""

from __future__ import annotations

from app.modules.auth.models import ROLE_ADMIN, ROLE_LEARNER, ROLE_SUPER_ADMIN


REQUIRED_PERMISSIONS: tuple[tuple[str, str], ...] = (
    ("users.read", "View user accounts in the admin console."),
    ("users.update_status", "Activate or deactivate user accounts."),
    ("users.view_progress", "View learner progress and task history."),
    ("task_templates.read", "View task templates."),
    ("task_templates.create", "Create task templates."),
    ("task_templates.update", "Update task templates."),
    ("task_templates.archive", "Archive task templates."),
    ("feedback_logs.read", "View feedback review queues and logs."),
    ("feedback_quality.review", "Review and annotate AI feedback quality."),
    ("ai_logs.read", "View AI request logs."),
    ("ai_costs.read", "View AI usage and cost information."),
    ("payments.read", "View limited payment and billing information."),
    ("subscriptions.manage", "Manage subscription status and periods."),
    ("audit_logs.read", "View admin audit logs."),
    ("admins.manage", "Assign or remove administrator roles."),
    ("roles.manage", "Update role permission grants."),
)

ALL_PERMISSION_KEYS = tuple(key for key, _description in REQUIRED_PERMISSIONS)

ADMIN_PERMISSION_KEYS = (
    "users.read",
    "users.update_status",
    "users.view_progress",
    "task_templates.read",
    "task_templates.create",
    "task_templates.update",
    "task_templates.archive",
    "feedback_logs.read",
    "feedback_quality.review",
    "ai_logs.read",
    "ai_costs.read",
    "payments.read",
    "audit_logs.read",
)

DEFAULT_ROLE_PERMISSIONS: dict[str, tuple[str, ...]] = {
    ROLE_LEARNER: (),
    ROLE_ADMIN: ADMIN_PERMISSION_KEYS,
    ROLE_SUPER_ADMIN: ALL_PERMISSION_KEYS,
}
