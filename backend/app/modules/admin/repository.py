"""Data access for production admin screens.

Phase 8: the admin views that read the legacy `tasks`/`responses`/
`feedbacks` tables are temporarily disabled — routes return 501. The
new daily-sessions tables (`activity_attempts`, `activity_feedback`)
will be wired in by the admin team in a follow-up.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.modules.admin.models import AIRequestLog, AdminAuditLog
from app.modules.admin.sanitization import mask_sensitive_text, sanitize_for_admin
from app.modules.admin.schemas import (
    AIRequestLogRead,
    AdminAuditLogRead,
    AdminLogUser,
    AdminPermissionRead,
    AdminRecentFeedback,
    AdminRecentTask,
    AdminRecentUser,
    AdminRoleRead,
    AdminSkillScore,
    AdminSummary,
    AdminUserDetail,
    AdminUserListItem,
    AdminUserProfile,
    PaymentRead,
    SubscriptionRead,
    UserBillingRead,
)
from app.modules.auth.models import (
    ROLE_ADMIN,
    ROLE_LEARNER,
    ROLE_SUPER_ADMIN,
    Permission,
    Role,
    RolePermission,
    User,
    UserProfile,
    UserRole,
)
from app.modules.auth.permissions import ALL_PERMISSION_KEYS
from app.modules.progress.models import SkillPoints
from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityFeedback,
    AttemptStatus,
)
from app.modules.skills.models import Skill
from app.modules.subscriptions.models import Payment, Subscription


def _enum_value(value: object) -> str:
    return getattr(value, "value", str(value))


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _primary_role(user: User) -> str:
    roles = set(user.role_names())
    if ROLE_SUPER_ADMIN in roles:
        return ROLE_SUPER_ADMIN
    if ROLE_ADMIN in roles:
        return ROLE_ADMIN
    return ROLE_LEARNER


def _user_list_item(user: User) -> AdminUserListItem:
    return AdminUserListItem(
        id=user.id,
        name=user.name,
        email=user.email,
        role=_primary_role(user),
        roles=user.role_names(),
        is_active=user.is_active,
        created_at=user.created_at,
    )


def _log_user(user: User | None) -> AdminLogUser | None:
    if user is None:
        return None
    return AdminLogUser(id=user.id, name=user.name, email=user.email)


def _mask_provider_id(value: str | None) -> str | None:
    if value is None:
        return None
    clean = value.strip()
    if len(clean) <= 8:
        return "*" * len(clean)
    return f"{clean[:4]}...{clean[-4:]}"


class AdminRepository:
    """Read/write helpers for admin endpoints."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def summary(self) -> AdminSummary:
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        total_users = self.db.query(func.count(User.id)).scalar() or 0
        active_users = (
            self.db.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar()
            or 0
        )
        tasks_completed = (
            self.db.query(func.count(ActivityAttempt.id))
            .filter(ActivityAttempt.status == AttemptStatus.EVALUATED)
            .scalar()
            or 0
        )
        feedback_generated = (
            self.db.query(func.count(ActivityFeedback.id)).scalar() or 0
        )
        ai_requests_24h = (
            self.db.query(func.count(AIRequestLog.id))
            .filter(AIRequestLog.created_at >= since)
            .scalar()
            or 0
        )
        ai_errors_24h = (
            self.db.query(func.count(AIRequestLog.id))
            .filter(AIRequestLog.created_at >= since, AIRequestLog.status != "success")
            .scalar()
            or 0
        )
        # The new flow has no per-row review queue. Pending count is zero
        # until an explicit review surface lands.
        pending_feedback_reviews = 0
        recent_users = [
            AdminRecentUser(
                id=user.id,
                name=user.name,
                email=user.email,
                role=_primary_role(user),
                roles=user.role_names(),
                is_active=user.is_active,
                created_at=user.created_at,
            )
            for user in self._base_user_query()
            .order_by(User.created_at.desc(), User.id.desc())
            .limit(5)
            .all()
        ]
        return AdminSummary(
            total_users=total_users,
            active_users=active_users,
            tasks_completed=tasks_completed,
            feedback_generated=feedback_generated,
            ai_requests_24h=ai_requests_24h,
            ai_errors_24h=ai_errors_24h,
            pending_feedback_reviews=pending_feedback_reviews,
            recent_users=recent_users,
        )

    def list_users(self) -> list[AdminUserListItem]:
        return [
            _user_list_item(user)
            for user in self._base_user_query()
            .order_by(User.created_at.desc(), User.id.desc())
            .all()
        ]

    def get_user_detail(self, user_id: int) -> AdminUserDetail | None:
        user = self._base_user_query().filter(User.id == user_id).first()
        if user is None:
            return None

        base = _user_list_item(user)
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        return AdminUserDetail(
            **base.model_dump(),
            profile=self._profile_out(profile),
            skill_scores=self._skill_scores(user.id),
            recent_tasks=self._recent_tasks(user.id),
            recent_feedback=self._recent_feedback(user.id),
        )

    def set_user_active(self, user: User, *, is_active: bool) -> User:
        user.is_active = is_active
        self.db.flush()
        return user

    def list_roles(self) -> list[AdminRoleRead]:
        rows = (
            self.db.query(Role)
            .options(selectinload(Role.permission_links).joinedload(RolePermission.permission))
            .order_by(Role.name.asc())
            .all()
        )
        counts = {
            role_id: count
            for role_id, count in (
                self.db.query(UserRole.role_id, func.count(UserRole.user_id))
                .group_by(UserRole.role_id)
                .all()
            )
        }
        return [
            AdminRoleRead(
                id=role.id,
                name=role.name,
                permissions=(
                    list(ALL_PERMISSION_KEYS)
                    if role.name == ROLE_SUPER_ADMIN and not role.permission_links
                    else role.permission_keys()
                ),
                user_count=int(counts.get(role.id, 0)),
                created_at=role.created_at,
            )
            for role in rows
        ]

    def list_permissions(self) -> list[AdminPermissionRead]:
        rows = self.db.query(Permission).order_by(Permission.key.asc()).all()
        return [
            AdminPermissionRead(
                id=permission.id,
                key=permission.key,
                description=permission.description,
                created_at=permission.created_at,
            )
            for permission in rows
        ]

    def get_role(self, role_id: int) -> Role | None:
        return (
            self.db.query(Role)
            .options(selectinload(Role.permission_links).joinedload(RolePermission.permission))
            .filter(Role.id == role_id)
            .first()
        )

    def list_audit_logs(self, *, limit: int = 100) -> list[AdminAuditLogRead]:
        rows = (
            self.db.query(AdminAuditLog)
            .options(joinedload(AdminAuditLog.admin_user))
            .order_by(AdminAuditLog.created_at.desc(), AdminAuditLog.id.desc())
            .limit(limit)
            .all()
        )
        return [self._audit_log_out(row) for row in rows]

    def list_ai_logs(
        self,
        *,
        include_sensitive: bool,
        limit: int = 100,
    ) -> list[AIRequestLogRead]:
        rows = (
            self.db.query(AIRequestLog)
            .options(joinedload(AIRequestLog.user))
            .order_by(AIRequestLog.created_at.desc(), AIRequestLog.id.desc())
            .limit(limit)
            .all()
        )
        return [self._ai_log_out(row, include_sensitive=include_sensitive) for row in rows]

    def get_ai_log(
        self,
        log_id: int,
        *,
        include_sensitive: bool,
    ) -> AIRequestLogRead | None:
        log = (
            self.db.query(AIRequestLog)
            .options(joinedload(AIRequestLog.user))
            .filter(AIRequestLog.id == log_id)
            .first()
        )
        if log is None:
            return None
        return self._ai_log_out(log, include_sensitive=include_sensitive)

    def list_payments(self, *, limit: int = 100) -> list[PaymentRead]:
        rows = (
            self.db.query(Payment)
            .options(joinedload(Payment.user))
            .order_by(
                Payment.paid_at.desc().nullslast(),
                Payment.created_at.desc(),
                Payment.id.desc(),
            )
            .limit(limit)
            .all()
        )
        return [self._payment_out(payment) for payment in rows]

    def list_subscriptions(self, *, limit: int = 100) -> list[SubscriptionRead]:
        rows = (
            self.db.query(Subscription)
            .options(joinedload(Subscription.user))
            .order_by(
                Subscription.current_period_end.desc().nullslast(),
                Subscription.updated_at.desc(),
                Subscription.id.desc(),
            )
            .limit(limit)
            .all()
        )
        return [self._subscription_out(subscription) for subscription in rows]

    def get_user_billing(self, user_id: int) -> UserBillingRead | None:
        user = self.db.get(User, user_id)
        if user is None:
            return None
        subscription = (
            self.db.query(Subscription)
            .options(joinedload(Subscription.user))
            .filter(Subscription.user_id == user_id)
            .order_by(
                Subscription.current_period_end.desc().nullslast(),
                Subscription.updated_at.desc(),
                Subscription.id.desc(),
            )
            .first()
        )
        payments = (
            self.db.query(Payment)
            .options(joinedload(Payment.user))
            .filter(Payment.user_id == user_id)
            .order_by(
                Payment.paid_at.desc().nullslast(),
                Payment.created_at.desc(),
                Payment.id.desc(),
            )
            .limit(25)
            .all()
        )
        return UserBillingRead(
            user=AdminLogUser(id=user.id, name=user.name, email=user.email),
            subscription=(
                self._subscription_out(subscription) if subscription is not None else None
            ),
            payments=[self._payment_out(payment) for payment in payments],
        )

    def get_subscription(self, subscription_id: int) -> Subscription | None:
        return (
            self.db.query(Subscription)
            .options(joinedload(Subscription.user))
            .filter(Subscription.id == subscription_id)
            .first()
        )

    def _base_user_query(self):
        return self.db.query(User).options(
            selectinload(User.role_links).joinedload(UserRole.role),
        )

    def _audit_log_out(self, log: AdminAuditLog) -> AdminAuditLogRead:
        return AdminAuditLogRead(
            id=log.id,
            admin_user_id=log.admin_user_id,
            admin=_log_user(log.admin_user),
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            old_value=sanitize_for_admin(log.old_value),
            new_value=sanitize_for_admin(log.new_value),
            ip_address=log.ip_address,
            created_at=log.created_at,
        )

    def _payment_out(self, payment: Payment) -> PaymentRead:
        return PaymentRead(
            id=payment.id,
            user_id=payment.user_id,
            user=_log_user(payment.user),
            provider=payment.provider,
            provider_payment_id=_mask_provider_id(payment.provider_payment_id),
            amount=float(payment.amount),
            currency=payment.currency,
            status=payment.status,
            paid_at=payment.paid_at,
            created_at=payment.created_at,
        )

    def _subscription_out(self, subscription: Subscription) -> SubscriptionRead:
        return SubscriptionRead(
            id=subscription.id,
            user_id=subscription.user_id,
            user=_log_user(subscription.user),
            provider=subscription.provider,
            provider_customer_id=_mask_provider_id(subscription.provider_customer_id),
            provider_subscription_id=_mask_provider_id(
                subscription.provider_subscription_id
            ),
            plan_name=subscription.plan_name,
            status=subscription.status,
            trial_ends_at=subscription.trial_ends_at,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at,
        )

    def _ai_log_out(
        self,
        log: AIRequestLog,
        *,
        include_sensitive: bool,
    ) -> AIRequestLogRead:
        raw_error = log.error_message
        safe_error = mask_sensitive_text(raw_error)
        if include_sensitive:
            error_message = safe_error
        elif raw_error and safe_error != raw_error:
            error_message = "Sensitive technical details hidden."
        else:
            error_message = safe_error
        return AIRequestLogRead(
            id=log.id,
            user_id=log.user_id,
            user=_log_user(log.user),
            trace_id=log.trace_id,
            agent_name=log.agent_name,
            model=log.model,
            input_tokens=log.input_tokens,
            output_tokens=log.output_tokens,
            latency_ms=log.latency_ms,
            status=log.status,
            error_message=error_message,
            prompt_version=log.prompt_version,
            created_at=log.created_at,
        )

    def _profile_out(self, profile: UserProfile | None) -> AdminUserProfile | None:
        if profile is None:
            return None
        return AdminUserProfile(
            display_name=profile.display_name,
            phone_number=profile.phone_number,
            country=profile.country,
            native_language=profile.native_language,
            self_assessed_level=_enum_value(profile.self_assessed_level),
            goal=_enum_value(profile.goal),
            interests=_split_csv(profile.interests),
            diagnosis_completed=profile.diagnosis_completed,
        )

    def _skill_scores(self, user_id: int) -> list[AdminSkillScore]:
        points_rows = (
            self.db.query(SkillPoints, Skill)
            .join(Skill, Skill.id == SkillPoints.skill_id)
            .filter(SkillPoints.user_id == user_id)
            .order_by(Skill.name.asc())
            .all()
        )
        return [
            AdminSkillScore(
                skill_id=row.skill_id,
                skill_name=skill.name,
                score=float(row.display_score),
                source="points",
            )
            for row, skill in points_rows
        ]

    def _recent_tasks(self, user_id: int) -> list[AdminRecentTask]:
        # Disabled in Phase 8 — reads the legacy `user_tasks` table.
        # Will be rewired against `activity_attempts` in a follow-up.
        return []

    def _recent_feedback(self, user_id: int) -> list[AdminRecentFeedback]:
        # Disabled in Phase 8 — reads the legacy `feedbacks` table. Will
        # be rewired against `activity_feedback` in a follow-up.
        return []
