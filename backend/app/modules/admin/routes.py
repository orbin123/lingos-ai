"""Admin HTTP routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.admin.audit_service import client_ip_from_request
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
    FeedbackReviewItem,
    FeedbackReviewUpdate,
    PaymentRead,
    RolePermissionsUpdate,
    ExpireTrialsResult,
    SubscriberAccessUpdate,
    SubscriberItem,
    SubscribersOverview,
    SubscriptionAdminUpdate,
    SubscriptionRead,
    UserBillingRead,
    UserProgressItem,
    UserRolesUpdate,
    UserStatusUpdate,
)
from app.modules.admin.service import AdminService
from app.modules.auth.dependencies import (
    require_permission,
    require_role,
    require_super_admin,
)
from app.modules.auth.models import ROLE_ADMIN, ROLE_SUPER_ADMIN, User
from app.modules.feedback.schemas import ReviewStats

require_admin = require_role([ROLE_ADMIN, ROLE_SUPER_ADMIN])

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/summary", response_model=AdminSummary, status_code=status.HTTP_200_OK)
def get_summary(
    _current_user: User = Depends(require_permission("users.read")),
    db: Session = Depends(get_db),
) -> AdminSummary:
    return AdminService(db).summary()


@router.get("/users", response_model=list[AdminUserListItem], status_code=status.HTTP_200_OK)
def list_users(
    _current_user: User = Depends(require_permission("users.read")),
    db: Session = Depends(get_db),
) -> list[AdminUserListItem]:
    return AdminService(db).list_users()


@router.get(
    "/users/{user_id}",
    response_model=AdminUserDetail,
    status_code=status.HTTP_200_OK,
)
def get_user(
    user_id: int,
    _current_user: User = Depends(require_permission("users.read")),
    _progress_user: User = Depends(require_permission("users.view_progress")),
    db: Session = Depends(get_db),
) -> AdminUserDetail:
    detail = AdminService(db).get_user_detail(user_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return detail


@router.get(
    "/user-progress",
    response_model=list[UserProgressItem],
    status_code=status.HTTP_200_OK,
)
def list_user_progress(
    _current_user: User = Depends(require_permission("users.view_progress")),
    db: Session = Depends(get_db),
) -> list[UserProgressItem]:
    return AdminService(db).list_user_progress()


@router.patch(
    "/users/{user_id}/status",
    response_model=AdminUserListItem,
    status_code=status.HTTP_200_OK,
)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    request: Request,
    current_user: User = Depends(require_permission("users.update_status")),
    db: Session = Depends(get_db),
) -> AdminUserListItem:
    try:
        user = AdminService(db).set_user_active(
            actor=current_user,
            user_id=user_id,
            is_active=payload.is_active,
            ip_address=client_ip_from_request(request),
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/roles", response_model=list[AdminRoleRead], status_code=status.HTTP_200_OK)
def list_roles(
    _current_user: User = Depends(require_permission("roles.manage")),
    _super_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> list[AdminRoleRead]:
    return AdminService(db).list_roles()


@router.get(
    "/permissions",
    response_model=list[AdminPermissionRead],
    status_code=status.HTTP_200_OK,
)
def list_permissions(
    _current_user: User = Depends(require_permission("roles.manage")),
    _super_admin: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> list[AdminPermissionRead]:
    return AdminService(db).list_permissions()


@router.patch(
    "/users/{user_id}/roles",
    response_model=AdminUserListItem,
    status_code=status.HTTP_200_OK,
)
def update_user_roles(
    user_id: int,
    payload: UserRolesUpdate,
    request: Request,
    _permission_user: User = Depends(require_permission("admins.manage")),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> AdminUserListItem:
    try:
        user = AdminService(db).update_user_roles(
            actor=current_user,
            user_id=user_id,
            payload=payload,
            ip_address=client_ip_from_request(request),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch(
    "/roles/{role_id}/permissions",
    response_model=AdminRoleRead,
    status_code=status.HTTP_200_OK,
)
def update_role_permissions(
    role_id: int,
    payload: RolePermissionsUpdate,
    request: Request,
    _permission_user: User = Depends(require_permission("roles.manage")),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> AdminRoleRead:
    try:
        role = AdminService(db).update_role_permissions(
            actor=current_user,
            role_id=role_id,
            payload=payload,
            ip_address=client_ip_from_request(request),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.get(
    "/app-reviews",
    response_model=list[AppReviewItem],
    status_code=status.HTTP_200_OK,
)
def list_app_reviews(
    rating: int | None = Query(default=None, ge=1, le=5),
    _current_user: User = Depends(require_permission("reviews.read")),
    db: Session = Depends(get_db),
) -> list[AppReviewItem]:
    return AdminService(db).list_app_reviews(rating=rating)


@router.get(
    "/reviews/stats",
    response_model=ReviewStats,
    status_code=status.HTTP_200_OK,
)
def review_stats(
    _current_user: User = Depends(require_permission("reviews.read")),
    db: Session = Depends(get_db),
) -> ReviewStats:
    return AdminService(db).review_stats()


@router.get(
    "/audit-logs",
    response_model=list[AdminAuditLogRead],
    status_code=status.HTTP_200_OK,
)
def list_audit_logs(
    _current_user: User = Depends(require_permission("audit_logs.read")),
    db: Session = Depends(get_db),
) -> list[AdminAuditLogRead]:
    return AdminService(db).list_audit_logs()


@router.get(
    "/ai-logs",
    response_model=list[AIRequestLogRead],
    status_code=status.HTTP_200_OK,
)
def list_ai_logs(
    current_user: User = Depends(require_permission("ai_logs.read")),
    db: Session = Depends(get_db),
) -> list[AIRequestLogRead]:
    return AdminService(db).list_ai_logs(actor=current_user)


@router.get(
    "/ai-logs/{log_id}",
    response_model=AIRequestLogRead,
    status_code=status.HTTP_200_OK,
)
def get_ai_log(
    log_id: int,
    current_user: User = Depends(require_permission("ai_logs.read")),
    db: Session = Depends(get_db),
) -> AIRequestLogRead:
    log = AdminService(db).get_ai_log(log_id, actor=current_user)
    if log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI log not found")
    return log


@router.get(
    "/ai-quality",
    response_model=AIQualityReport,
    status_code=status.HTTP_200_OK,
)
def get_ai_quality(
    days: int = 7,
    _current_user: User = Depends(require_permission("ai_quality.read")),
    db: Session = Depends(get_db),
) -> AIQualityReport:
    return AdminService(db).ai_quality(days=days)


@router.get(
    "/payments",
    response_model=list[PaymentRead],
    status_code=status.HTTP_200_OK,
)
def list_payments(
    _current_user: User = Depends(require_permission("payments.read")),
    db: Session = Depends(get_db),
) -> list[PaymentRead]:
    return AdminService(db).list_payments()


@router.get(
    "/subscribers",
    response_model=SubscribersOverview,
    status_code=status.HTTP_200_OK,
)
def list_subscribers(
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description=(
            "Filter by displayed status: active|expired|cancelled|paused "
            "(subscribers) or unverified|not_started|trial|expired (trials)."
        ),
    ),
    _current_user: User = Depends(require_permission("payments.read")),
    db: Session = Depends(get_db),
) -> SubscribersOverview:
    return AdminService(db).list_subscribers(status=status_filter)


@router.get(
    "/users/{user_id}/billing",
    response_model=UserBillingRead,
    status_code=status.HTTP_200_OK,
)
def get_user_billing(
    user_id: int,
    _current_user: User = Depends(require_permission("payments.read")),
    db: Session = Depends(get_db),
) -> UserBillingRead:
    billing = AdminService(db).get_user_billing(user_id)
    if billing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return billing


@router.patch(
    "/subscribers/{user_id}/access",
    response_model=SubscriberItem,
    status_code=status.HTTP_200_OK,
)
def update_subscriber_access(
    user_id: int,
    payload: SubscriberAccessUpdate,
    request: Request,
    _permission_user: User = Depends(require_permission("subscriptions.manage")),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> SubscriberItem:
    """Deprecated: edits the legacy `Purchase` access window only.

    Subscription-backed users are managed via
    PATCH /admin/subscribers/{user_id}/subscription.
    """
    subscriber = AdminService(db).update_subscriber_access(
        user_id=user_id,
        access_expires_at=payload.access_expires_at,
        actor=current_user,
        ip_address=client_ip_from_request(request),
    )
    if subscriber is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No purchase found for this user",
        )
    return subscriber


@router.patch(
    "/subscribers/{user_id}/subscription",
    response_model=SubscriptionRead,
    status_code=status.HTTP_200_OK,
)
def update_subscriber_subscription(
    user_id: int,
    payload: SubscriptionAdminUpdate,
    request: Request,
    _permission_user: User = Depends(require_permission("subscriptions.manage")),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> SubscriptionRead:
    """Edit a user's subscription row: grant/extend trial, set expiry,
    fix a stuck status. Creates the row if the user has none."""
    try:
        subscription = AdminService(db).update_subscriber_subscription(
            user_id=user_id,
            update=payload,
            actor=current_user,
            ip_address=client_ip_from_request(request),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        )
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return subscription


@router.post(
    "/subscriptions/expire-due-trials",
    response_model=ExpireTrialsResult,
    status_code=status.HTTP_200_OK,
)
def expire_due_trials(
    request: Request,
    _permission_user: User = Depends(require_permission("subscriptions.manage")),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> ExpireTrialsResult:
    """Flip stored status on trials past their end (reporting hygiene —
    access is already blocked lazily). Also runnable via
    `backend/scripts/expire_trials.py` from cron."""
    flipped = AdminService(db).expire_due_trials(
        actor=current_user,
        ip_address=client_ip_from_request(request),
    )
    return ExpireTrialsResult(expired=flipped)


# ── Feedback review (specific + rag) ───────────────────────────────


@router.get(
    "/feedback-review",
    response_model=list[FeedbackReviewItem],
    status_code=status.HTTP_200_OK,
)
def list_feedback_review(
    _current_user: User = Depends(require_permission("feedback_logs.read")),
    db: Session = Depends(get_db),
) -> list[FeedbackReviewItem]:
    return AdminService(db).list_feedback_review()


@router.patch(
    "/feedback-review/{feedback_type}/{feedback_id}",
    response_model=FeedbackReviewItem,
    status_code=status.HTTP_200_OK,
)
def update_feedback_review(
    feedback_type: str,
    feedback_id: int,
    payload: FeedbackReviewUpdate,
    request: Request,
    current_user: User = Depends(require_permission("feedback_quality.review")),
    db: Session = Depends(get_db),
) -> FeedbackReviewItem:
    if feedback_type not in ("specific", "rag"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="feedback_type must be 'specific' or 'rag'",
        )
    item = AdminService(db).review_feedback(
        feedback_type=feedback_type,
        feedback_id=feedback_id,
        payload=payload,
        actor=current_user,
        ip_address=client_ip_from_request(request),
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )
    return item
