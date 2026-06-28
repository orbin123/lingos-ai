"""Purchase, notification, and account-action endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_verified
from app.modules.auth.models import User
from app.modules.subscriptions.catalog import PLAN_CATALOG
from app.modules.subscriptions.exceptions import (
    AccountNotDeletable,
    NoPlanSelected,
    NotCancellable,
    PlanLocked,
    PlanNotFound,
    PurchaseNotFound,
    TrialAlreadyUsed,
)
from app.modules.subscriptions.schemas import (
    EntitlementRead,
    NotificationSettings,
    NotificationSettingsUpdate,
    PlanSelect,
    PurchaseRead,
)
from app.modules.subscriptions.service import (
    AccessResolution,
    SubscriptionService,
)

subscription_router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])
users_router = APIRouter(prefix="/api/users", tags=["users"])


def _entitlement_out(access: AccessResolution) -> EntitlementRead:
    plan = PLAN_CATALOG.get(access.plan_id) if access.plan_id else None
    return EntitlementRead(
        access_state=access.state.value,
        subscription_status=access.subscription_status,
        plan_id=access.plan_id,
        plan_name=access.plan_name,
        amount=float(plan["amount_paid"]) if plan else None,  # type: ignore[arg-type]
        currency=str(plan["currency"]) if plan else None,
        trial_started_at=access.trial_started_at,
        trial_ends_at=access.trial_ends_at,
        days_remaining=access.days_remaining,
        current_period_end=access.current_period_end,
    )


def _settings_from_profile(profile: object) -> NotificationSettings:
    return NotificationSettings(
        daily_practice_reminder=bool(getattr(profile, "daily_practice_reminder", True)),
        streak_reminder=bool(getattr(profile, "streak_reminder", True)),
        weekly_progress_email=bool(getattr(profile, "weekly_progress_email", False)),
        feature_announcements=bool(getattr(profile, "feature_announcements", False)),
    )


@subscription_router.get("/me", response_model=EntitlementRead)
def get_entitlement(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EntitlementRead:
    """Return the current user's entitlement (access state, plan, trial)."""
    access = SubscriptionService(db).resolve_access(current_user)
    return _entitlement_out(access)


@subscription_router.post("/select-plan", response_model=EntitlementRead)
def select_plan(
    payload: PlanSelect,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
) -> EntitlementRead:
    """Store the chosen plan (pre-trial). Locked once a trial has started."""
    service = SubscriptionService(db)
    try:
        service.select_plan(current_user, payload.plan_id)
    except PlanNotFound:
        raise HTTPException(status_code=404, detail="Unknown plan.")
    except PlanLocked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "plan_locked",
                "message": "Your plan can no longer be changed.",
            },
        )
    return _entitlement_out(service.resolve_access(current_user))


@subscription_router.post("/start-trial", response_model=EntitlementRead)
def start_trial(
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
) -> EntitlementRead:
    """One-click free trial. Idempotent while a trial/subscription runs."""
    service = SubscriptionService(db)
    try:
        service.start_trial(current_user)
    except NoPlanSelected:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "plan_not_selected",
                "message": "Choose a plan before starting your trial.",
            },
        )
    except TrialAlreadyUsed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "trial_already_used",
                "message": "Your free trial has already been used.",
            },
        )
    return _entitlement_out(service.resolve_access(current_user))


@subscription_router.post("/cancel", response_model=EntitlementRead)
def cancel_subscription(
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
) -> EntitlementRead:
    """Cancel the running trial/subscription."""
    service = SubscriptionService(db)
    try:
        service.cancel(current_user)
    except NotCancellable:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "not_cancellable",
                "message": "There is no active subscription to cancel.",
            },
        )
    return _entitlement_out(service.resolve_access(current_user))


@subscription_router.patch("/me/pause", response_model=PurchaseRead)
def pause_course_access(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PurchaseRead:
    """Pause the user's learning plan without changing purchase history.

    The status flip lives on `Purchase` only — `UserCoursePreference`
    does not carry a status field today. If we need to gate session
    access on `purchase.status == "paused"`, that lookup happens at the
    sessions route.
    """
    try:
        return PurchaseRead.model_validate(
            SubscriptionService(db).pause_course(current_user)
        )
    except PurchaseNotFound:
        raise HTTPException(status_code=404, detail="No purchase found.")


@users_router.patch("/me/notifications", response_model=NotificationSettings)
def update_notifications(
    payload: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationSettings:
    """Patch notification preferences immediately after a toggle change."""
    profile = SubscriptionService(db).update_notifications(
        current_user, payload.model_dump(exclude_unset=True)
    )
    return _settings_from_profile(profile)


@users_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Permanently delete the current account."""
    try:
        SubscriptionService(db).delete_account(current_user)
    except AccountNotDeletable:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "account_not_deletable",
                "message": "Admin accounts can't be deleted.",
            },
        )
