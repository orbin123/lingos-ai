"""Data access for production admin screens.

Phase 8: the admin views that read the legacy `tasks`/`responses`/
`feedbacks` tables are temporarily disabled — routes return 501. The
new daily-sessions tables (`activity_attempts`, `activity_feedback`)
will be wired in by the admin team in a follow-up.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, NamedTuple

from sqlalchemy import case, func, or_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.ai.llm.usage import estimate_cost
from app.modules.admin.models import (
    AIEvaluation,
    AIRequestLog,
    AdminAuditLog,
)
from app.modules.admin.sanitization import mask_sensitive_text, sanitize_for_admin
from app.modules.admin.schemas import (
    AICostByCapability,
    AICostByModel,
    AICostDailyPoint,
    AICostReport,
    AIQualityReport,
    AIQualityRow,
    AIQualityTimeSeriesPoint,
    AIQualityWorst,
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
    AppReviewItem,
    FeedbackAnalyticsItem,
    FeedbackReactionStats,
    PaymentRead,
    SubscriberItem,
    SubscribersOverview,
    SubscriptionRead,
    TrialUserItem,
    UserBillingRead,
    UserProgressItem,
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
    DailySession,
    FeedbackReaction,
    FeedbackType,
    ReactionValue,
    SessionScorecard,
)
from app.modules.reviews.repository import AppReviewRepository
from app.modules.skills.models import Skill
from app.modules.subscriptions.catalog import PLAN_CATALOG
from app.modules.subscriptions.models import (
    Payment,
    Purchase,
    Subscription,
    SubscriptionStatus,
)
from app.modules.subscriptions.service import resolve_effective_status


class _ProgressBilling(NamedTuple):
    """Resolved plan + access window for one row of the User-Progress list."""

    plan_id: str | None
    plan_name: str | None
    purchase_complete: bool
    access_expires_at: datetime | None


def _enum_value(value: object) -> str:
    return getattr(value, "value", str(value))


def _as_aware(value: datetime | None) -> datetime | None:
    """Treat a naive datetime as UTC so comparisons never crash.

    Postgres returns tz-aware datetimes for `timestamptz`; SQLite (tests)
    returns naive ones. Normalising here keeps the access-window math safe
    regardless of backend.
    """
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


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
        avg_latency_raw = (
            self.db.query(func.avg(AIRequestLog.latency_ms))
            .filter(AIRequestLog.created_at >= since)
            .scalar()
        )
        ai_avg_latency_ms_24h = (
            int(avg_latency_raw) if avg_latency_raw is not None else None
        )
        # Cost isn't stored — derive it from (model, tokens) per row via the
        # pricing table. The 24h window keeps this row count bounded.
        cost_rows = (
            self.db.query(
                AIRequestLog.model,
                AIRequestLog.input_tokens,
                AIRequestLog.output_tokens,
            )
            .filter(AIRequestLog.created_at >= since)
            .all()
        )
        ai_cost_24h = round(
            sum(
                estimate_cost(model, in_tok or 0, out_tok or 0) or 0.0
                for model, in_tok, out_tok in cost_rows
            ),
            6,
        )
        disliked_feedback = (
            self.db.query(func.count(FeedbackReaction.id))
            .filter(FeedbackReaction.reaction == ReactionValue.DISLIKE.value)
            .scalar()
            or 0
        )
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
            ai_cost_24h=ai_cost_24h,
            ai_avg_latency_ms_24h=ai_avg_latency_ms_24h,
            disliked_feedback=disliked_feedback,
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
        profile = (
            self.db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        )
        return AdminUserDetail(
            **base.model_dump(),
            profile=self._profile_out(profile),
            skill_scores=self._skill_scores(user.id),
            recent_tasks=self._recent_tasks(user.id),
            recent_feedback=self._recent_feedback(user.id),
        )

    def list_user_progress(self) -> list[UserProgressItem]:
        """Per-learner progress: course bought, activities done, how well."""
        users = (
            self._base_user_query()
            .order_by(User.created_at.desc(), User.id.desc())
            .all()
        )

        # Completed (evaluated) activity counts, grouped by learner.
        count_rows = (
            self.db.query(DailySession.user_id, func.count(ActivityAttempt.id))
            .join(ActivityAttempt, ActivityAttempt.session_id == DailySession.id)
            .filter(ActivityAttempt.status == AttemptStatus.EVALUATED)
            .group_by(DailySession.user_id)
            .all()
        )
        counts = {user_id: int(count) for user_id, count in count_rows}

        # Per-sub-skill display scores, grouped by learner (one query).
        skills_by_user: dict[int, list[AdminSkillScore]] = {}
        for points, skill in (
            self.db.query(SkillPoints, Skill)
            .join(Skill, Skill.id == SkillPoints.skill_id)
            .order_by(Skill.name.asc())
            .all()
        ):
            skills_by_user.setdefault(points.user_id, []).append(
                AdminSkillScore(
                    skill_id=points.skill_id,
                    skill_name=skill.name,
                    score=float(points.display_score),
                    source="points",
                )
            )

        purchases = {
            purchase.user_id: purchase for purchase in self.db.query(Purchase).all()
        }
        # Newest subscription per user wins (matches SubscriptionRepository
        # .get_for_user and list_subscribers). The Pay-Now redesign activates
        # via Subscription and never writes a Purchase, so plan/access must be
        # read from here too — not from the legacy Purchase table alone.
        subscriptions: dict[int, Subscription] = {}
        for subscription in (
            self.db.query(Subscription).order_by(Subscription.id.desc()).all()
        ):
            subscriptions.setdefault(subscription.user_id, subscription)

        items: list[UserProgressItem] = []
        for user in users:
            skills = skills_by_user.get(user.id, [])
            dashboard_score = (
                round(sum(s.score for s in skills) / len(skills), 1) if skills else None
            )
            billing = self._progress_billing(
                subscriptions.get(user.id), purchases.get(user.id)
            )
            items.append(
                UserProgressItem(
                    user_id=user.id,
                    name=user.name,
                    email=user.email,
                    plan_id=billing.plan_id,
                    plan_name=billing.plan_name,
                    purchase_complete=billing.purchase_complete,
                    access_expires_at=billing.access_expires_at,
                    activities_completed=counts.get(user.id, 0),
                    dashboard_score=dashboard_score,
                    subskill_scores=skills,
                )
            )
        return items

    @staticmethod
    def _progress_billing(
        subscription: Subscription | None,
        purchase: Purchase | None,
    ) -> _ProgressBilling:
        """Resolve a learner's plan + access window for the progress list.

        Prefers a paid `Subscription` (the new Pay-Now / activation flow,
        identified by a started paid period) and falls back to the legacy
        one-time `Purchase`. Plan name is resolved from `PLAN_CATALOG` and
        `current_period_end` is the access window — mirroring `list_subscribers`.
        """
        # A started paid period == a completed purchase; an expired one stays
        # "complete" (access_expires_at carries the expiry), exactly like a
        # legacy paid Purchase past its window. Trial-only rows
        # (current_period_start is None) are not a purchase here.
        if subscription is not None and subscription.current_period_start is not None:
            plan = (
                PLAN_CATALOG.get(subscription.plan_id)
                if subscription.plan_id
                else None
            )
            plan_name = str(plan["name"]) if plan else subscription.plan_name
            return _ProgressBilling(
                plan_id=subscription.plan_id,
                plan_name=plan_name,
                purchase_complete=True,
                access_expires_at=subscription.current_period_end,
            )
        if purchase is not None:
            return _ProgressBilling(
                plan_id=purchase.plan_id,
                plan_name=purchase.plan_name,
                purchase_complete=purchase.status == "paid",
                access_expires_at=purchase.access_expires_at,
            )
        return _ProgressBilling(None, None, False, None)

    def set_user_active(self, user: User, *, is_active: bool) -> User:
        user.is_active = is_active
        self.db.flush()
        return user

    def list_roles(self) -> list[AdminRoleRead]:
        rows = (
            self.db.query(Role)
            .options(
                selectinload(Role.permission_links).joinedload(
                    RolePermission.permission
                )
            )
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
            .options(
                selectinload(Role.permission_links).joinedload(
                    RolePermission.permission
                )
            )
            .filter(Role.id == role_id)
            .first()
        )

    def list_app_reviews(
        self, *, rating: int | None = None, limit: int = 200
    ) -> list[AppReviewItem]:
        rows = AppReviewRepository(self.db).list_for_admin(rating=rating, limit=limit)
        return [
            AppReviewItem(
                id=review.id,
                user=_log_user(review.user),
                rating=review.rating,
                title=review.title,
                body=review.body,
                positive_feedback=review.positive_feedback,
                improvement_feedback=review.improvement_feedback,
                bug_report=review.bug_report,
                status=review.status,
                created_at=review.created_at,
            )
            for review in rows
        ]

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
        return [
            self._ai_log_out(row, include_sensitive=include_sensitive) for row in rows
        ]

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

    def ai_quality(self, *, days: int = 7, worst_limit: int = 20) -> AIQualityReport:
        """Rolling LLM-as-judge quality over the last ``days`` (Part B Phase 2).

        Returns per-``target_type`` mean scores + the worst-scoring outputs
        (any axis < 6) for human review. Scores are stored as ``Numeric`` —
        coerced to float here for the JSON response.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        def _f(value: Any) -> float | None:
            return float(value) if value is not None else None

        def _round(value: float | None) -> float | None:
            return round(value, 2) if value is not None else None

        mean_rows = (
            self.db.query(
                AIEvaluation.target_type,
                func.count(AIEvaluation.id),
                func.avg(AIEvaluation.accuracy),
                func.avg(AIEvaluation.relevance),
                func.avg(AIEvaluation.helpfulness),
                func.avg(AIEvaluation.correctness),
                func.avg(AIEvaluation.faithfulness),
            )
            .filter(AIEvaluation.created_at >= since)
            .group_by(AIEvaluation.target_type)
            .all()
        )
        means = [
            AIQualityRow(
                target_type=target_type,
                judged_count=int(count or 0),
                mean_accuracy=_round(_f(acc)),
                mean_relevance=_round(_f(rel)),
                mean_helpfulness=_round(_f(helps)),
                mean_correctness=_round(_f(corr)),
                mean_faithfulness=_round(_f(faith)),
            )
            for target_type, count, acc, rel, helps, corr, faith in mean_rows
        ]
        judged_count = sum(row.judged_count for row in means)

        # Worst-N: any non-null axis below 6 (portable across Postgres/SQLite).
        worst_rows = (
            self.db.query(AIEvaluation)
            .filter(AIEvaluation.created_at >= since)
            .filter(
                or_(
                    AIEvaluation.accuracy < 6,
                    AIEvaluation.relevance < 6,
                    AIEvaluation.helpfulness < 6,
                    AIEvaluation.correctness < 6,
                    AIEvaluation.faithfulness < 6,
                )
            )
            .order_by(AIEvaluation.created_at.desc())
            .limit(worst_limit)
            .all()
        )
        worst = [
            AIQualityWorst(
                id=row.id,
                trace_id=row.trace_id,
                target_type=row.target_type,
                target_id=row.target_id,
                judge_model=row.judge_model,
                accuracy=_f(row.accuracy),
                relevance=_f(row.relevance),
                helpfulness=_f(row.helpfulness),
                correctness=_f(row.correctness),
                faithfulness=_f(row.faithfulness),
                rationale=row.rationale,
                created_at=row.created_at,
            )
            for row in worst_rows
        ]

        # Per-day means per target_type (Part B Phase 3). ``func.date`` is
        # portable across SQLite and Postgres and buckets by UTC calendar day.
        day_col = func.date(AIEvaluation.created_at)
        series_rows = (
            self.db.query(
                day_col.label("day"),
                AIEvaluation.target_type,
                func.count(AIEvaluation.id),
                func.avg(AIEvaluation.accuracy),
                func.avg(AIEvaluation.relevance),
                func.avg(AIEvaluation.helpfulness),
                func.avg(AIEvaluation.correctness),
                func.avg(AIEvaluation.faithfulness),
            )
            .filter(AIEvaluation.created_at >= since)
            .group_by(day_col, AIEvaluation.target_type)
            .order_by(day_col.asc())
            .all()
        )
        series = [
            AIQualityTimeSeriesPoint(
                date=str(day),
                target_type=target_type,
                judged_count=int(count or 0),
                mean_accuracy=_round(_f(acc)),
                mean_relevance=_round(_f(rel)),
                mean_helpfulness=_round(_f(helps)),
                mean_correctness=_round(_f(corr)),
                mean_faithfulness=_round(_f(faith)),
            )
            for day, target_type, count, acc, rel, helps, corr, faith in series_rows
        ]

        return AIQualityReport(
            days=days,
            judged_count=judged_count,
            means=means,
            worst=worst,
            series=series,
        )

    def ai_costs(self, *, days: int = 30) -> AICostReport:
        """AI spend over a rolling window, derived from ai_request_logs.

        Cost isn't stored — it's computed per (model, tokens) group via the LLM
        pricing table. We aggregate in SQL by (agent_name, model) and (day,
        model) so row counts stay bounded, then roll up cost in Python.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        grouped = (
            self.db.query(
                AIRequestLog.agent_name,
                AIRequestLog.model,
                func.count(AIRequestLog.id),
                func.sum(case((AIRequestLog.status != "success", 1), else_=0)),
                func.coalesce(func.sum(AIRequestLog.input_tokens), 0),
                func.coalesce(func.sum(AIRequestLog.output_tokens), 0),
            )
            .filter(AIRequestLog.created_at >= since)
            .group_by(AIRequestLog.agent_name, AIRequestLog.model)
            .all()
        )

        by_model: dict[str, AICostByModel] = {}
        by_cap: dict[str, AICostByCapability] = {}
        total_cost = 0.0
        total_requests = 0
        total_in = 0
        total_out = 0
        unpriced = 0

        for agent_name, model, count, errors, in_tok, out_tok in grouped:
            count = int(count or 0)
            errors = int(errors or 0)
            in_tok = int(in_tok or 0)
            out_tok = int(out_tok or 0)
            cost = estimate_cost(model, in_tok, out_tok)
            priced = cost is not None
            cost_val = cost or 0.0

            total_requests += count
            total_in += in_tok
            total_out += out_tok
            total_cost += cost_val
            if not priced:
                unpriced += count

            m = by_model.get(model)
            if m is None:
                by_model[model] = AICostByModel(
                    model=model,
                    requests=count,
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                    cost_usd=cost_val if priced else None,
                )
            else:
                m.requests += count
                m.input_tokens += in_tok
                m.output_tokens += out_tok
                if priced:
                    m.cost_usd = round((m.cost_usd or 0.0) + cost_val, 6)

            c = by_cap.get(agent_name)
            if c is None:
                by_cap[agent_name] = AICostByCapability(
                    agent_name=agent_name,
                    requests=count,
                    errors=errors,
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                    cost_usd=round(cost_val, 6),
                )
            else:
                c.requests += count
                c.errors += errors
                c.input_tokens += in_tok
                c.output_tokens += out_tok
                c.cost_usd = round(c.cost_usd + cost_val, 6)

        day_col = func.date(AIRequestLog.created_at)
        daily_rows = (
            self.db.query(
                day_col,
                AIRequestLog.model,
                func.count(AIRequestLog.id),
                func.coalesce(func.sum(AIRequestLog.input_tokens), 0),
                func.coalesce(func.sum(AIRequestLog.output_tokens), 0),
            )
            .filter(AIRequestLog.created_at >= since)
            .group_by(day_col, AIRequestLog.model)
            .all()
        )
        daily_map: dict[str, AICostDailyPoint] = {}
        for day, model, count, in_tok, out_tok in daily_rows:
            key = str(day)[:10]
            cost = estimate_cost(model, int(in_tok or 0), int(out_tok or 0)) or 0.0
            point = daily_map.get(key)
            if point is None:
                daily_map[key] = AICostDailyPoint(
                    date=key, cost_usd=round(cost, 6), requests=int(count or 0)
                )
            else:
                point.cost_usd = round(point.cost_usd + cost, 6)
                point.requests += int(count or 0)

        return AICostReport(
            days=days,
            total_cost_usd=round(total_cost, 6),
            total_requests=total_requests,
            total_input_tokens=total_in,
            total_output_tokens=total_out,
            unpriced_requests=unpriced,
            by_model=sorted(
                by_model.values(), key=lambda x: x.cost_usd or 0.0, reverse=True
            ),
            by_capability=sorted(
                by_cap.values(), key=lambda x: x.cost_usd, reverse=True
            ),
            daily=sorted(daily_map.values(), key=lambda x: x.date),
        )

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

    def list_subscribers(self, *, status: str | None = None) -> SubscribersOverview:
        """Paying subscribers + trial users, read from stored billing rows.

        Paying group: paid-lifecycle `Subscription` rows (entered via
        payment) plus legacy `Purchase` rows. Trial group: everyone else,
        with trial state read from the stored subscription row — never
        derived from signup date.

        `status` filters both groups by their displayed (effective) status:
        subscribers — active|expired|cancelled|paused; trials —
        unverified|not_started|trial|expired.
        """
        now = datetime.now(timezone.utc)

        purchase_rows = (
            self.db.query(Purchase, User)
            .join(User, User.id == Purchase.user_id)
            .order_by(
                Purchase.access_expires_at.desc().nullslast(),
                Purchase.id.desc(),
            )
            .all()
        )

        paying_ids: set[int] = set()
        subscribers: list[SubscriberItem] = []
        for purchase, user in purchase_rows:
            paying_ids.add(user.id)
            expires = _as_aware(purchase.access_expires_at)
            if purchase.status == "paused":
                item_status = "paused"
            elif expires is None or expires > now:
                item_status = "active"
            else:
                item_status = "expired"
            subscribers.append(
                SubscriberItem(
                    user_id=user.id,
                    name=user.name,
                    email=user.email,
                    plan_id=purchase.plan_id,
                    plan_name=purchase.plan_name,
                    amount_paid=float(purchase.amount_paid),
                    currency=purchase.currency,
                    status=item_status,
                    purchased_at=purchase.created_at,
                    access_expires_at=purchase.access_expires_at,
                )
            )

        # Stored subscription rows, newest first; first row per user wins
        # (matches SubscriptionRepository.get_for_user).
        subscription_by_user: dict[int, Subscription] = {}
        subscription_rows = (
            self.db.query(Subscription, User)
            .join(User, User.id == Subscription.user_id)
            .order_by(Subscription.id.desc())
            .all()
        )
        for subscription, user in subscription_rows:
            if subscription.user_id in subscription_by_user:
                continue
            subscription_by_user[subscription.user_id] = subscription
            # Paid lifecycle = a paid period was ever started. Trial-only
            # rows (verified/trial/expired-trial) belong in the trial group.
            if subscription.current_period_start is None or user.id in paying_ids:
                continue
            paying_ids.add(user.id)
            effective = resolve_effective_status(subscription, now)
            if subscription.status == SubscriptionStatus.CANCELLED.value:
                item_status = "cancelled"
            else:
                item_status = effective.value
            plan = (
                PLAN_CATALOG.get(subscription.plan_id) if subscription.plan_id else None
            )
            subscribers.append(
                SubscriberItem(
                    user_id=user.id,
                    name=user.name,
                    email=user.email,
                    plan_id=subscription.plan_id,
                    plan_name=subscription.plan_name,
                    amount_paid=float(plan["amount_paid"]) if plan else None,  # type: ignore[arg-type]
                    currency=str(plan["currency"]) if plan else None,
                    status=item_status,
                    purchased_at=subscription.current_period_start,
                    access_expires_at=subscription.current_period_end,
                )
            )

        trials: list[TrialUserItem] = []
        for user in (
            self._base_user_query()
            .order_by(User.created_at.desc(), User.id.desc())
            .all()
        ):
            if user.id in paying_ids:
                continue
            subscription = subscription_by_user.get(user.id)
            if not user.email_verified:
                item_status = "unverified"
            elif subscription is None or subscription.trial_started_at is None:
                item_status = "not_started"
            else:
                ends = _as_aware(subscription.trial_ends_at)
                item_status = "trial" if ends is not None and ends > now else "expired"
            trials.append(
                TrialUserItem(
                    user_id=user.id,
                    name=user.name,
                    email=user.email,
                    status=item_status,
                    email_verified=user.email_verified,
                    signed_up_at=user.created_at,
                    trial_started_at=(
                        subscription.trial_started_at if subscription else None
                    ),
                    trial_ends_at=(
                        subscription.trial_ends_at if subscription else None
                    ),
                )
            )

        if status:
            subscribers = [item for item in subscribers if item.status == status]
            trials = [item for item in trials if item.status == status]

        return SubscribersOverview(subscribers=subscribers, trials=trials)

    def get_purchase_for_user(self, user_id: int) -> Purchase | None:
        return self.db.query(Purchase).filter(Purchase.user_id == user_id).first()

    # ── Feedback analytics (learner reactions) ───────────────────────

    @staticmethod
    def _apply_reaction_filter(query, reaction: str | None):
        """Constrain an outerjoined-FeedbackReaction query by reaction filter.

        ``LIKE``/``DISLIKE`` → that reaction; ``NONE`` → no reaction row;
        None/``ALL`` → no constraint.
        """
        if reaction in (None, "ALL"):
            return query
        if reaction == "NONE":
            return query.filter(FeedbackReaction.id.is_(None))
        return query.filter(FeedbackReaction.reaction == reaction)

    def list_feedback_analytics(
        self,
        *,
        feedback_type: str | None = None,
        reaction: str | None = None,
        limit: int = 200,
    ) -> list[FeedbackAnalyticsItem]:
        """AI feedback items joined to the learner's reaction (read-only).

        ``feedback_type`` filters to ACTIVITY_FEEDBACK / COACH_NOTE (None=both);
        ``reaction`` filters to LIKE / DISLIKE / NONE (None=all). Each feedback
        belongs to one learner, so the only possible reaction is theirs.
        """
        items: list[FeedbackAnalyticsItem] = []
        want_activity = feedback_type in (None, FeedbackType.ACTIVITY_FEEDBACK.value)
        want_coach = feedback_type in (None, FeedbackType.COACH_NOTE.value)

        if want_activity:
            activity_query = (
                self.db.query(ActivityFeedback, ActivityAttempt, User, FeedbackReaction)
                .join(
                    ActivityAttempt, ActivityAttempt.id == ActivityFeedback.attempt_id
                )
                .join(DailySession, DailySession.id == ActivityAttempt.session_id)
                .join(User, User.id == DailySession.user_id)
                .outerjoin(
                    FeedbackReaction,
                    (
                        FeedbackReaction.feedback_type
                        == FeedbackType.ACTIVITY_FEEDBACK.value
                    )
                    & (FeedbackReaction.feedback_id == ActivityFeedback.id),
                )
            )
            activity_query = self._apply_reaction_filter(activity_query, reaction)
            for feedback, attempt, user, reaction_row in (
                activity_query.order_by(ActivityFeedback.created_at.desc())
                .limit(limit)
                .all()
            ):
                items.append(
                    FeedbackAnalyticsItem(
                        feedback_type=FeedbackType.ACTIVITY_FEEDBACK.value,
                        feedback_id=feedback.id,
                        user=_log_user(user),
                        context_label=attempt.archetype_id,
                        score=float(feedback.score),
                        summary=feedback.summary,
                        did_well=feedback.did_well,
                        mistakes=feedback.mistakes,
                        next_tip=feedback.next_tip,
                        user_reaction=reaction_row.reaction if reaction_row else None,
                        created_at=feedback.created_at,
                    )
                )

        if want_coach:
            coach_query = (
                self.db.query(SessionScorecard, DailySession, User, FeedbackReaction)
                .join(DailySession, DailySession.id == SessionScorecard.session_id)
                .join(User, User.id == DailySession.user_id)
                .outerjoin(
                    FeedbackReaction,
                    (FeedbackReaction.feedback_type == FeedbackType.COACH_NOTE.value)
                    & (FeedbackReaction.feedback_id == SessionScorecard.id),
                )
                .filter(SessionScorecard.mentor_note.isnot(None))
            )
            coach_query = self._apply_reaction_filter(coach_query, reaction)
            for scorecard, session, user, reaction_row in (
                coach_query.order_by(SessionScorecard.created_at.desc())
                .limit(limit)
                .all()
            ):
                items.append(
                    FeedbackAnalyticsItem(
                        feedback_type=FeedbackType.COACH_NOTE.value,
                        feedback_id=scorecard.id,
                        user=_log_user(user),
                        context_label=session.day_id,
                        mentor_note=scorecard.mentor_note,
                        user_reaction=reaction_row.reaction if reaction_row else None,
                        created_at=scorecard.created_at,
                    )
                )

        # Disliked first (the quality signal that needs attention), newest within.
        def _priority(item: FeedbackAnalyticsItem) -> int:
            return 0 if item.user_reaction == ReactionValue.DISLIKE.value else 1

        items.sort(key=lambda i: (_priority(i), -i.created_at.timestamp()))
        return items[:limit]

    def feedback_reaction_stats(self) -> FeedbackReactionStats:
        """KPI roll-up: how many feedback items were liked / disliked / ignored."""
        activity_total = self.db.query(func.count(ActivityFeedback.id)).scalar() or 0
        coach_total = (
            self.db.query(func.count(SessionScorecard.id))
            .filter(SessionScorecard.mentor_note.isnot(None))
            .scalar()
            or 0
        )
        total_items = activity_total + coach_total

        types = (FeedbackType.ACTIVITY_FEEDBACK.value, FeedbackType.COACH_NOTE.value)

        def _count(*conditions) -> int:
            return (
                self.db.query(func.count(FeedbackReaction.id))
                .filter(FeedbackReaction.feedback_type.in_(types), *conditions)
                .scalar()
                or 0
            )

        liked = _count(FeedbackReaction.reaction == ReactionValue.LIKE.value)
        disliked = _count(FeedbackReaction.reaction == ReactionValue.DISLIKE.value)
        reacted = _count()
        no_reaction = max(0, total_items - reacted)
        total_reacted = liked + disliked
        positive_rate = round(liked / total_reacted, 3) if total_reacted else None

        return FeedbackReactionStats(
            total_items=total_items,
            liked=liked,
            disliked=disliked,
            no_reaction=no_reaction,
            positive_rate=positive_rate,
        )

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
                self._subscription_out(subscription)
                if subscription is not None
                else None
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
            provider_order_id=_mask_provider_id(payment.provider_order_id),
            amount=float(payment.amount),
            currency=payment.currency,
            status=payment.status,
            method=payment.method,
            failure_reason=payment.failure_reason,
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
            plan_id=subscription.plan_id,
            plan_name=subscription.plan_name,
            status=subscription.status,
            trial_started_at=subscription.trial_started_at,
            trial_ends_at=subscription.trial_ends_at,
            cancelled_at=subscription.cancelled_at,
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
        cost_usd = estimate_cost(
            log.model, log.input_tokens or 0, log.output_tokens or 0
        )
        return AIRequestLogRead(
            id=log.id,
            user_id=log.user_id,
            user=_log_user(log.user),
            trace_id=log.trace_id,
            agent_name=log.agent_name,
            model=log.model,
            input_tokens=log.input_tokens,
            output_tokens=log.output_tokens,
            cost_usd=cost_usd,
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

    def _recent_tasks(self, user_id: int, *, limit: int = 10) -> list[AdminRecentTask]:
        rows = (
            self.db.query(ActivityAttempt)
            .join(DailySession, DailySession.id == ActivityAttempt.session_id)
            .filter(DailySession.user_id == user_id)
            .order_by(ActivityAttempt.created_at.desc(), ActivityAttempt.id.desc())
            .limit(limit)
            .all()
        )
        return [
            AdminRecentTask(
                id=attempt.id,
                task_id=attempt.id,
                title=attempt.archetype_id,
                task_type=attempt.archetype_id,
                status=_enum_value(attempt.status),
                completed_at=attempt.submitted_at,
                created_at=attempt.created_at,
            )
            for attempt in rows
        ]

    def _recent_feedback(
        self, user_id: int, *, limit: int = 10
    ) -> list[AdminRecentFeedback]:
        rows = (
            self.db.query(ActivityFeedback, ActivityAttempt)
            .join(
                ActivityAttempt,
                ActivityAttempt.id == ActivityFeedback.attempt_id,
            )
            .join(DailySession, DailySession.id == ActivityAttempt.session_id)
            .filter(DailySession.user_id == user_id)
            .order_by(ActivityFeedback.created_at.desc(), ActivityFeedback.id.desc())
            .limit(limit)
            .all()
        )
        return [
            AdminRecentFeedback(
                id=feedback.id,
                task_title=attempt.archetype_id,
                task_type=attempt.archetype_id,
                score=float(feedback.score),
                body={
                    "summary": feedback.summary,
                    "did_well": feedback.did_well,
                    "mistakes": feedback.mistakes,
                    "next_tip": feedback.next_tip,
                },
                created_at=feedback.created_at,
            )
            for feedback, attempt in rows
        ]
