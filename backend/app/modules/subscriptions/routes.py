"""Purchase, notification, and account-action endpoints."""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.admin.audit_service import AdminAuditService
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.repository import UserProfileRepository
from app.modules.preferences.repository import UserCoursePreferenceRepository
from app.modules.subscriptions.models import Payment, Purchase
from app.modules.subscriptions.schemas import (
    NotificationSettings,
    NotificationSettingsUpdate,
    PlanPurchase,
    PurchaseRead,
)

subscription_router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])
users_router = APIRouter(prefix="/api/users", tags=["users"])


# Course length is the only per-plan piece of state the daily-sessions flow
# cares about — the rest (title, level) is presentational and rendered by the
# frontend from the plan_id directly.
PLAN_CATALOG: dict[str, dict[str, object]] = {
    "beginner-24w": {
        "course_length": "24w",
        "name": "24-Week Foundation",
        "amount_paid": 999.0,
        "currency": "INR",
    },
    "beginner-48w": {
        "course_length": "48w",
        "name": "48-Week Plan",
        "amount_paid": 1999.0,
        "currency": "INR",
    },
}


def _settings_from_profile(profile: object) -> NotificationSettings:
    return NotificationSettings(
        daily_practice_reminder=bool(getattr(profile, "daily_practice_reminder", True)),
        streak_reminder=bool(getattr(profile, "streak_reminder", True)),
        weekly_progress_email=bool(getattr(profile, "weekly_progress_email", False)),
        feature_announcements=bool(getattr(profile, "feature_announcements", False)),
    )


@subscription_router.get("/me", response_model=PurchaseRead | None)
def get_purchase(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PurchaseRead | None:
    """Return the current user's one-time purchase, if one exists."""
    return db.query(Purchase).filter(Purchase.user_id == current_user.id).first()


@subscription_router.post("/purchase", response_model=PurchaseRead)
def purchase_plan(
    payload: PlanPurchase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PurchaseRead:
    """Mock a purchase and seed/update the user's course preference."""
    plan = PLAN_CATALOG.get(payload.plan_id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown purchase plan.",
        )

    # Upsert the user's course preference with the plan's course_length.
    # Lazy-create covers the common case where this is the user's first plan;
    # an existing row gets its course_length bumped to match the new plan.
    pref_repo = UserCoursePreferenceRepository(db)
    preference = pref_repo.get_or_create_for_user(current_user.id)
    preference.course_length = str(plan["course_length"])

    purchase = db.query(Purchase).filter(Purchase.user_id == current_user.id).first()
    if purchase is None:
        purchase = Purchase(user_id=current_user.id)
        db.add(purchase)

    purchase.plan_id = payload.plan_id
    purchase.plan_name = str(plan["name"])
    purchase.amount_paid = float(plan["amount_paid"])
    purchase.currency = str(plan["currency"])
    purchase.status = "paid"
    db.flush()

    payment = Payment(
        user_id=current_user.id,
        provider="mock",
        provider_payment_id=f"mock_{purchase.id}_{uuid4().hex}",
        amount=purchase.amount_paid,
        currency=purchase.currency,
        status="paid",
        paid_at=datetime.now(timezone.utc),
    )
    db.add(payment)
    db.flush()
    AdminAuditService(db).record(
        admin=current_user,
        action="payment.recorded",
        resource_type="payment",
        resource_id=payment.id,
        old_value=None,
        new_value={
            "id": payment.id,
            "user_id": payment.user_id,
            "provider": payment.provider,
            "provider_payment_id": payment.provider_payment_id,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status,
        },
    )

    db.commit()
    db.refresh(purchase)
    return purchase


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
    purchase = db.query(Purchase).filter(Purchase.user_id == current_user.id).first()
    if purchase is None:
        raise HTTPException(status_code=404, detail="No purchase found.")

    purchase.status = "paused"

    db.commit()
    db.refresh(purchase)
    return purchase


@users_router.patch("/me/notifications", response_model=NotificationSettings)
def update_notifications(
    payload: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationSettings:
    """Patch notification preferences immediately after a toggle change."""
    profile_repo = UserProfileRepository(db)
    profile = profile_repo.get_by_user_id(current_user.id)
    if profile is None:
        profile = profile_repo.create_default(current_user.id)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if value is not None:
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return _settings_from_profile(profile)


@users_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Permanently delete the current account."""
    db.delete(current_user)
    db.commit()
