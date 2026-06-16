"""Business logic for admin APIs.

Phase 8: task-template and feedback-review endpoints route to legacy
tables and return 501 at the route layer. Their service methods are
gone here too.
"""

from typing import Any

from sqlalchemy.orm import Session

from app.modules.admin.audit_service import AdminAuditService
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import (
    AIQualityReport,
    AIRequestLogRead,
    AdminAuditLogRead,
    AdminPermissionRead,
    AdminRoleRead,
    AdminSummary,
    AdminUserDetail,
    AdminUserListItem,
    AppReviewItem,
    FeedbackAnalyticsItem,
    FeedbackReactionStats,
    PaymentRead,
    RolePermissionsUpdate,
    SubscriberItem,
    SubscribersOverview,
    SubscriptionAdminUpdate,
    SubscriptionRead,
    UserBillingRead,
    UserProgressItem,
    UserRolesUpdate,
)
from app.modules.auth.models import DEFAULT_ROLE_NAMES, ROLE_SUPER_ADMIN, User
from app.modules.auth.permissions import ALL_PERMISSION_KEYS
from app.modules.auth.repository import RoleRepository
from app.modules.feedback.schemas import ReviewStats
from app.modules.feedback.service import FeedbackAnalyticsService
from app.modules.subscriptions.models import Purchase


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

    def list_user_progress(self) -> list[UserProgressItem]:
        return self.repo.list_user_progress()

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
            new_value={
                "id": role.id,
                "name": role.name,
                "permissions": sorted(requested),
            },
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
        if target.has_any_role({ROLE_SUPER_ADMIN}) and not actor.has_any_role(
            {ROLE_SUPER_ADMIN}
        ):
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

    def list_feedback_analytics(
        self,
        *,
        feedback_type: str | None = None,
        reaction: str | None = None,
    ) -> list[FeedbackAnalyticsItem]:
        return self.repo.list_feedback_analytics(
            feedback_type=feedback_type, reaction=reaction
        )

    def feedback_reaction_stats(self) -> FeedbackReactionStats:
        return self.repo.feedback_reaction_stats()

    def list_app_reviews(self, *, rating: int | None = None) -> list[AppReviewItem]:
        return self.repo.list_app_reviews(rating=rating)

    def review_stats(self) -> ReviewStats:
        return FeedbackAnalyticsService(self.db).stats()

    def list_audit_logs(self) -> list[AdminAuditLogRead]:
        return self.repo.list_audit_logs()

    def list_ai_logs(self, *, actor: User) -> list[AIRequestLogRead]:
        return self.repo.list_ai_logs(
            include_sensitive=self._can_see_sensitive_ai(actor)
        )

    def get_ai_log(self, log_id: int, *, actor: User) -> AIRequestLogRead | None:
        return self.repo.get_ai_log(
            log_id,
            include_sensitive=self._can_see_sensitive_ai(actor),
        )

    def ai_quality(self, *, days: int = 7) -> AIQualityReport:
        return self.repo.ai_quality(days=days)

    def list_payments(self) -> list[PaymentRead]:
        return self.repo.list_payments()

    def list_subscribers(self, *, status: str | None = None) -> SubscribersOverview:
        return self.repo.list_subscribers(status=status)

    def get_user_billing(self, user_id: int) -> UserBillingRead | None:
        return self.repo.get_user_billing(user_id)

    def update_subscriber_access(
        self,
        *,
        user_id: int,
        access_expires_at,
        actor: User,
        ip_address: str | None = None,
    ) -> SubscriberItem | None:
        """Extend or expire a subscriber's 2-year access window."""
        purchase = self.repo.get_purchase_for_user(user_id)
        if purchase is None:
            return None

        old_value = self._purchase_snapshot(purchase)
        purchase.access_expires_at = access_expires_at
        self.db.flush()
        self.audit.record(
            admin=actor,
            action="purchase.access_update",
            resource_type="purchase",
            resource_id=purchase.id,
            old_value=old_value,
            new_value=self._purchase_snapshot(purchase),
            ip_address=ip_address,
        )
        self.db.commit()
        # Return the refreshed subscriber row from the unified view.
        overview = self.repo.list_subscribers()
        return next(
            (item for item in overview.subscribers if item.user_id == user_id),
            None,
        )

    def update_subscriber_subscription(
        self,
        *,
        user_id: int,
        update: SubscriptionAdminUpdate,
        actor: User,
        ip_address: str | None = None,
    ) -> SubscriptionRead | None:
        """Admin edit of a user's subscription row (grant/extend trial,
        set expiry, fix a stuck status). Creates the row if the user has
        none. Returns None if the user doesn't exist; raises ValueError on
        an invalid status/plan_id."""
        from app.modules.subscriptions.catalog import PLAN_CATALOG
        from app.modules.subscriptions.models import Subscription, SubscriptionStatus
        from app.modules.subscriptions.repository import SubscriptionRepository

        user = self.db.get(User, user_id)
        if user is None:
            return None

        if update.status is not None and update.status not in {
            s.value for s in SubscriptionStatus
        }:
            raise ValueError(f"Invalid subscription status {update.status!r}")
        if update.plan_id is not None and update.plan_id not in PLAN_CATALOG:
            raise ValueError(f"Unknown plan {update.plan_id!r}")

        subscription = SubscriptionRepository(self.db).get_for_user(user_id)
        if subscription is None:
            plan_id = update.plan_id or next(iter(PLAN_CATALOG))
            plan = PLAN_CATALOG[plan_id]
            subscription = Subscription(
                user_id=user_id,
                provider="admin",
                plan_id=plan_id,
                plan_name=str(plan["name"]),
                status=update.status or SubscriptionStatus.VERIFIED.value,
            )
            self.db.add(subscription)
            self.db.flush()
            old_value = None
        else:
            old_value = self._subscription_snapshot(subscription)

        for field in (
            "status",
            "trial_started_at",
            "trial_ends_at",
            "current_period_end",
        ):
            value = getattr(update, field)
            if value is not None:
                setattr(subscription, field, value)
        if update.plan_id is not None:
            subscription.plan_id = update.plan_id
            subscription.plan_name = str(PLAN_CATALOG[update.plan_id]["name"])

        self.db.flush()
        self.audit.record(
            admin=actor,
            action="subscription.admin_update",
            resource_type="subscription",
            resource_id=subscription.id,
            old_value=old_value,
            new_value=self._subscription_snapshot(subscription),
            ip_address=ip_address,
        )
        self.db.commit()
        return self.repo._subscription_out(subscription)

    def expire_due_trials(
        self,
        *,
        actor: User,
        ip_address: str | None = None,
    ) -> int:
        """Flip stored status on trials past their end (lazy resolution
        already blocks access; this cleans up admin reporting). Audited."""
        from app.modules.subscriptions.service import SubscriptionService

        flipped = SubscriptionService(self.db).expire_due_trials()
        self.audit.record(
            admin=actor,
            action="subscription.expire_due_trials",
            resource_type="subscription",
            resource_id=None,
            old_value=None,
            new_value={"expired": flipped},
            ip_address=ip_address,
        )
        self.db.commit()
        return flipped

    def _subscription_snapshot(self, subscription) -> dict[str, Any]:
        return {
            "id": subscription.id,
            "user_id": subscription.user_id,
            "provider": subscription.provider,
            "plan_id": subscription.plan_id,
            "status": subscription.status,
            "trial_started_at": (
                subscription.trial_started_at.isoformat()
                if subscription.trial_started_at
                else None
            ),
            "trial_ends_at": (
                subscription.trial_ends_at.isoformat()
                if subscription.trial_ends_at
                else None
            ),
            "current_period_end": (
                subscription.current_period_end.isoformat()
                if subscription.current_period_end
                else None
            ),
        }

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

    def _purchase_snapshot(self, purchase: Purchase) -> dict[str, Any]:
        return {
            "id": purchase.id,
            "user_id": purchase.user_id,
            "plan_id": purchase.plan_id,
            "plan_name": purchase.plan_name,
            "status": purchase.status,
            "access_expires_at": (
                purchase.access_expires_at.isoformat()
                if purchase.access_expires_at
                else None
            ),
        }

    def _can_see_sensitive_ai(self, actor: User) -> bool:
        return actor.has_any_role({ROLE_SUPER_ADMIN})
