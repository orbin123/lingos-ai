"""Business logic for admin APIs."""

from typing import Any

from sqlalchemy.orm import Session

from app.modules.admin.audit_service import AdminAuditService
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import (
    AIRequestLogRead,
    AdminAuditLogRead,
    AdminPermissionRead,
    AdminRoleRead,
    AdminSummary,
    AdminUserDetail,
    AdminUserListItem,
    FeedbackReviewItem,
    FeedbackReviewUpdate,
    PaymentRead,
    RolePermissionsUpdate,
    SubscriptionRead,
    SubscriptionUpdate,
    TaskTemplateCreate,
    TaskTemplateRead,
    TaskTemplateUpdate,
    UserBillingRead,
    UserRolesUpdate,
)
from app.modules.auth.models import DEFAULT_ROLE_NAMES, ROLE_SUPER_ADMIN, User
from app.modules.auth.permissions import ALL_PERMISSION_KEYS
from app.modules.auth.repository import RoleRepository
from app.modules.subscriptions.models import Subscription
from app.modules.tasks.models import Task, TaskStatus, TaskType


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AdminRepository(db)
        self.audit = AdminAuditService(db)
        self.roles = RoleRepository(db)

    def summary(self) -> AdminSummary:
        return self.repo.summary()

    def list_users(self) -> list[AdminUserListItem]:
        return self.repo.list_users()

    def get_user_detail(self, user_id: int) -> AdminUserDetail | None:
        return self.repo.get_user_detail(user_id)

    def list_roles(self) -> list[AdminRoleRead]:
        self.roles.ensure_defaults()
        return self.repo.list_roles()

    def list_permissions(self) -> list[AdminPermissionRead]:
        self.roles.ensure_defaults()
        return self.repo.list_permissions()

    def update_user_roles(
        self,
        *,
        actor: User,
        user_id: int,
        payload: UserRolesUpdate,
        ip_address: str | None = None,
    ) -> AdminUserListItem | None:
        target = self.db.get(User, user_id)
        if target is None:
            return None

        requested = set(payload.roles)
        unknown = requested - set(DEFAULT_ROLE_NAMES)
        if unknown:
            raise ValueError(f"Unknown role: {sorted(unknown)[0]}")
        if target.id == actor.id and ROLE_SUPER_ADMIN not in requested:
            raise ValueError("Super admins cannot remove their own super admin role")

        old_value = self._user_roles_snapshot(target)
        self.roles.replace_user_roles(user=target, role_names=requested)
        self.audit.record(
            admin=actor,
            action="user.roles_update",
            resource_type="user",
            resource_id=target.id,
            old_value=old_value,
            new_value=self._user_roles_snapshot(target, roles=sorted(requested)),
            ip_address=ip_address,
        )
        self.db.commit()
        detail = self.repo.get_user_detail(target.id)
        if detail is None:
            return None
        return AdminUserListItem(
            id=detail.id,
            name=detail.name,
            email=detail.email,
            role=detail.role,
            roles=detail.roles,
            is_active=detail.is_active,
            created_at=detail.created_at,
        )

    def update_role_permissions(
        self,
        *,
        actor: User,
        role_id: int,
        payload: RolePermissionsUpdate,
        ip_address: str | None = None,
    ) -> AdminRoleRead | None:
        role = self.roles.get_role(role_id)
        if role is None:
            return None

        requested = set(payload.permission_keys)
        unknown = requested - set(ALL_PERMISSION_KEYS)
        if unknown:
            raise ValueError(f"Unknown permission: {sorted(unknown)[0]}")

        old_value = self._role_permissions_snapshot(role)
        self.roles.replace_role_permissions(role=role, permission_keys=requested)
        self.audit.record(
            admin=actor,
            action="role.permissions_update",
            resource_type="role",
            resource_id=role.id,
            old_value=old_value,
            new_value={"id": role.id, "name": role.name, "permissions": sorted(requested)},
            ip_address=ip_address,
        )
        self.db.commit()
        return next(
            (item for item in self.repo.list_roles() if item.id == role.id),
            None,
        )

    def set_user_active(
        self,
        *,
        actor: User,
        user_id: int,
        is_active: bool,
        ip_address: str | None = None,
    ) -> AdminUserListItem | None:
        target = self.db.get(User, user_id)
        if target is None:
            return None
        if target.id == actor.id and not is_active:
            raise ValueError("Admins cannot deactivate their own account")
        if target.has_any_role({ROLE_SUPER_ADMIN}) and not actor.has_any_role({ROLE_SUPER_ADMIN}):
            raise PermissionError("Only super admins can update a super admin")

        old_value = self._user_status_snapshot(target)
        self.repo.set_user_active(target, is_active=is_active)
        self.audit.record(
            admin=actor,
            action="user.status_change",
            resource_type="user",
            resource_id=target.id,
            old_value=old_value,
            new_value=self._user_status_snapshot(target),
            ip_address=ip_address,
        )
        self.db.commit()
        self.db.refresh(target)
        detail = self.repo.get_user_detail(target.id)
        if detail is None:
            return None
        return AdminUserListItem(
            id=detail.id,
            name=detail.name,
            email=detail.email,
            role=detail.role,
            roles=detail.roles,
            is_active=detail.is_active,
            created_at=detail.created_at,
        )

    def list_task_templates(self) -> list[TaskTemplateRead]:
        return [self._task_out(task) for task in self.repo.list_task_templates()]

    def create_task_template(
        self,
        payload: TaskTemplateCreate,
        *,
        actor: User,
        ip_address: str | None = None,
    ) -> TaskTemplateRead:
        task = self.repo.create_task_template(
            title=payload.title.strip(),
            task_type=self._task_type(payload.task_type),
            difficulty=payload.difficulty,
            status=self._task_status(payload.status),
            content=payload.content,
        )
        self.audit.record(
            admin=actor,
            action="task_template.create",
            resource_type="task_template",
            resource_id=task.id,
            old_value=None,
            new_value=self._task_snapshot(task),
            ip_address=ip_address,
        )
        self.db.commit()
        self.db.refresh(task)
        return self._task_out(task)

    def update_task_template(
        self,
        *,
        template_id: int,
        payload: TaskTemplateUpdate,
        actor: User,
        ip_address: str | None = None,
    ) -> TaskTemplateRead | None:
        task = self.repo.get_task_template(template_id)
        if task is None:
            return None

        old_value = self._task_snapshot(task)
        updates = payload.model_dump(exclude_unset=True)
        if "title" in updates and updates["title"] is not None:
            task.title = updates["title"].strip()
        if "task_type" in updates and updates["task_type"] is not None:
            task.task_type = self._task_type(updates["task_type"])
        if "difficulty" in updates and updates["difficulty"] is not None:
            task.difficulty = updates["difficulty"]
        if "status" in updates and updates["status"] is not None:
            task.status = self._task_status(updates["status"])
        if "content" in updates and updates["content"] is not None:
            task.content = updates["content"]

        self.db.flush()
        self.audit.record(
            admin=actor,
            action="task_template.update",
            resource_type="task_template",
            resource_id=task.id,
            old_value=old_value,
            new_value=self._task_snapshot(task),
            ip_address=ip_address,
        )
        self.db.commit()
        self.db.refresh(task)
        return self._task_out(task)

    def archive_task_template(
        self,
        template_id: int,
        *,
        actor: User,
        ip_address: str | None = None,
    ) -> TaskTemplateRead | None:
        task = self.repo.get_task_template(template_id)
        if task is None:
            return None
        old_value = self._task_snapshot(task)
        self.repo.archive_task_template(task)
        self.audit.record(
            admin=actor,
            action="task_template.archive",
            resource_type="task_template",
            resource_id=task.id,
            old_value=old_value,
            new_value=self._task_snapshot(task),
            ip_address=ip_address,
        )
        self.db.commit()
        self.db.refresh(task)
        return self._task_out(task)

    def list_audit_logs(self) -> list[AdminAuditLogRead]:
        return self.repo.list_audit_logs()

    def list_ai_logs(self, *, actor: User) -> list[AIRequestLogRead]:
        return self.repo.list_ai_logs(include_sensitive=self._can_see_sensitive_ai(actor))

    def get_ai_log(self, log_id: int, *, actor: User) -> AIRequestLogRead | None:
        return self.repo.get_ai_log(
            log_id,
            include_sensitive=self._can_see_sensitive_ai(actor),
        )

    def list_feedback_review(self) -> list[FeedbackReviewItem]:
        return self.repo.list_feedback_review()

    def update_feedback_review(
        self,
        *,
        feedback_id: int,
        payload: FeedbackReviewUpdate,
        actor: User,
        ip_address: str | None = None,
    ) -> FeedbackReviewItem | None:
        feedback = self.repo.get_feedback(feedback_id)
        if feedback is None:
            return None
        old_value = self._feedback_review_snapshot(feedback)
        self.repo.update_feedback_review(
            feedback,
            review_status=payload.review_status,
            admin_note=payload.admin_note,
            reviewer=actor,
        )
        self.audit.record(
            admin=actor,
            action="feedback.review",
            resource_type="feedback",
            resource_id=feedback.id,
            old_value=old_value,
            new_value=self._feedback_review_snapshot(feedback),
            ip_address=ip_address,
        )
        self.db.commit()
        return self.repo.get_feedback_review_item(feedback_id)

    def list_payments(self) -> list[PaymentRead]:
        return self.repo.list_payments()

    def list_subscriptions(self) -> list[SubscriptionRead]:
        return self.repo.list_subscriptions()

    def get_user_billing(self, user_id: int) -> UserBillingRead | None:
        return self.repo.get_user_billing(user_id)

    def update_subscription(
        self,
        *,
        subscription_id: int,
        payload: SubscriptionUpdate,
        actor: User,
        ip_address: str | None = None,
    ) -> SubscriptionRead | None:
        subscription = self.repo.get_subscription(subscription_id)
        if subscription is None:
            return None

        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise ValueError("At least one subscription field must be provided")

        old_value = self._subscription_snapshot(subscription)
        for field, value in updates.items():
            if field == "plan_name" and isinstance(value, str):
                value = value.strip()
            setattr(subscription, field, value)

        self.db.flush()
        self.audit.record(
            admin=actor,
            action="subscription.update",
            resource_type="subscription",
            resource_id=subscription.id,
            old_value=old_value,
            new_value=self._subscription_snapshot(subscription),
            ip_address=ip_address,
        )
        self.db.commit()
        self.db.refresh(subscription)
        return self.repo._subscription_out(subscription)

    def _task_type(self, value: str) -> TaskType:
        try:
            return TaskType(value)
        except ValueError as exc:
            raise ValueError(f"Unknown task_type: {value}") from exc

    def _task_status(self, value: str) -> TaskStatus:
        try:
            return TaskStatus(value)
        except ValueError as exc:
            raise ValueError(f"Unknown status: {value}") from exc

    def _task_out(self, task: Task) -> TaskTemplateRead:
        return TaskTemplateRead(
            id=task.id,
            title=task.title,
            task_type=task.task_type.value,
            difficulty=task.difficulty,
            status=task.status.value,
            content=task.content,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    def _user_status_snapshot(self, user: User) -> dict[str, Any]:
        return {
            "id": user.id,
            "email": user.email,
            "roles": user.role_names(),
            "is_active": user.is_active,
        }

    def _user_roles_snapshot(
        self,
        user: User,
        *,
        roles: list[str] | None = None,
    ) -> dict[str, Any]:
        role_names = roles if roles is not None else user.role_names()
        return {
            "id": user.id,
            "email": user.email,
            "roles": role_names,
            "is_superuser": ROLE_SUPER_ADMIN in set(role_names),
        }

    def _role_permissions_snapshot(self, role) -> dict[str, Any]:
        return {
            "id": role.id,
            "name": role.name,
            "permissions": role.permission_keys(),
        }

    def _task_snapshot(self, task: Task) -> dict[str, Any]:
        return {
            "id": task.id,
            "title": task.title,
            "task_type": task.task_type.value,
            "difficulty": task.difficulty,
            "status": task.status.value,
            "content": task.content,
        }

    def _feedback_review_snapshot(self, feedback) -> dict[str, Any]:
        return {
            "id": feedback.id,
            "review_status": feedback.review_status,
            "reviewed_by": feedback.reviewed_by,
            "reviewed_at": (
                feedback.reviewed_at.isoformat() if feedback.reviewed_at else None
            ),
            "admin_note": feedback.admin_note,
        }

    def _subscription_snapshot(self, subscription: Subscription) -> dict[str, Any]:
        return {
            "id": subscription.id,
            "user_id": subscription.user_id,
            "provider": subscription.provider,
            "provider_customer_id": subscription.provider_customer_id,
            "provider_subscription_id": subscription.provider_subscription_id,
            "plan_name": subscription.plan_name,
            "status": subscription.status,
            "trial_ends_at": (
                subscription.trial_ends_at.isoformat()
                if subscription.trial_ends_at
                else None
            ),
            "current_period_start": (
                subscription.current_period_start.isoformat()
                if subscription.current_period_start
                else None
            ),
            "current_period_end": (
                subscription.current_period_end.isoformat()
                if subscription.current_period_end
                else None
            ),
        }

    def _can_see_sensitive_ai(self, actor: User) -> bool:
        return actor.has_any_role({ROLE_SUPER_ADMIN})
