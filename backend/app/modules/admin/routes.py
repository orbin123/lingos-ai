"""Admin HTTP routes."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.admin.audit_service import client_ip_from_request
from app.modules.admin.schemas import (
    AIRequestLogRead,
    AdminAuditLogRead,
    AdminPermissionRead,
    AdminRoleRead,
    AdminSummary,
    AdminUserDetail,
    AdminUserListItem,
    PaymentRead,
    RolePermissionsUpdate,
    SubscriptionRead,
    SubscriptionUpdate,
    UserBillingRead,
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


# ── Task templates (Phase 8: disabled) ─────────────────────────────
#
# Backed by the deleted `tasks.Task` table. The admin team will rebuild
# against `task_archetypes` + `curriculum_days` in a follow-up. Until
# then every endpoint returns 501.


_TASK_TEMPLATES_DISABLED = (
    "Task templates were backed by the legacy `tasks` table, which was "
    "removed in the Phase 8 cutover. Admin task management will be "
    "re-implemented against `task_archetypes` in a follow-up."
)


@router.get("/task-templates", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def list_task_templates(
    _current_user: User = Depends(require_permission("task_templates.read")),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=_TASK_TEMPLATES_DISABLED,
    )


@router.post("/task-templates", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def create_task_template(
    _current_user: User = Depends(require_permission("task_templates.create")),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=_TASK_TEMPLATES_DISABLED,
    )


@router.patch(
    "/task-templates/{template_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED
)
def update_task_template(
    template_id: int,
    _current_user: User = Depends(require_permission("task_templates.update")),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=_TASK_TEMPLATES_DISABLED,
    )


@router.delete(
    "/task-templates/{template_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED
)
def archive_task_template(
    template_id: int,
    _current_user: User = Depends(require_permission("task_templates.archive")),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=_TASK_TEMPLATES_DISABLED,
    )


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
    "/subscriptions",
    response_model=list[SubscriptionRead],
    status_code=status.HTTP_200_OK,
)
def list_subscriptions(
    _current_user: User = Depends(require_permission("payments.read")),
    db: Session = Depends(get_db),
) -> list[SubscriptionRead]:
    return AdminService(db).list_subscriptions()


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
    "/subscriptions/{subscription_id}",
    response_model=SubscriptionRead,
    status_code=status.HTTP_200_OK,
)
def update_subscription(
    subscription_id: int,
    payload: SubscriptionUpdate,
    request: Request,
    _permission_user: User = Depends(require_permission("subscriptions.manage")),
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db),
) -> SubscriptionRead:
    try:
        subscription = AdminService(db).update_subscription(
            subscription_id=subscription_id,
            payload=payload,
            actor=current_user,
            ip_address=client_ip_from_request(request),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )
    return subscription


# ── Feedback review (Phase 8: disabled) ────────────────────────────
#
# Backed by the deleted `feedbacks` review queue. The new flow's
# `activity_feedback` rows don't yet carry a review status — that
# surface returns when the admin team re-implements.


_FEEDBACK_REVIEW_DISABLED = (
    "Feedback review was backed by the legacy `feedbacks` table, which "
    "was removed in the Phase 8 cutover. The admin review queue will "
    "land in a follow-up against `activity_feedback`."
)


@router.get("/feedback-review", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def list_feedback_review(
    _current_user: User = Depends(require_permission("feedback_logs.read")),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=_FEEDBACK_REVIEW_DISABLED,
    )


@router.patch(
    "/feedback-review/{feedback_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED
)
def update_feedback_review(
    feedback_id: int,
    _current_user: User = Depends(require_permission("feedback_quality.review")),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=_FEEDBACK_REVIEW_DISABLED,
    )
