"""Premium-access guard — backend enforcement of the entitlement state.

Lives here (not in auth/dependencies.py) so auth doesn't import the
subscription service. Applied per-route on the AI-spending surface only;
read-only routes stay open to expired users.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.subscriptions.service import (
    PREMIUM_STATES,
    AccessState,
    SubscriptionService,
)

_DENIALS: dict[AccessState, tuple[int, str, str]] = {
    AccessState.UNVERIFIED: (
        status.HTTP_403_FORBIDDEN,
        "email_unverified",
        "Verify your email to continue.",
    ),
    AccessState.VERIFIED: (
        status.HTTP_403_FORBIDDEN,
        "trial_not_started",
        "Start your free trial to continue.",
    ),
    AccessState.EXPIRED: (
        status.HTTP_402_PAYMENT_REQUIRED,
        "subscription_expired",
        "Your access has expired — upgrade to continue.",
    ),
    AccessState.CANCELLED: (
        status.HTTP_402_PAYMENT_REQUIRED,
        "subscription_cancelled",
        "Your subscription is cancelled — resubscribe to continue.",
    ),
}

# WebSocket close code for "entitlement required" (mirrors HTTP 402; the
# 4401/4403/4404 codes are already used for auth/role/not-found).
WS_PAYMENT_REQUIRED = 4402


def require_active_access(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Allow only TRIAL/ACTIVE users through to premium (AI-spending) routes."""
    state = SubscriptionService(db).resolve_access(current_user).state
    if state in PREMIUM_STATES:
        return current_user

    status_code, code, message = _DENIALS[state]
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message},
    )


def check_ws_access(user: User, db: Session) -> bool:
    """Same resolution as require_active_access, for WebSocket handlers.

    Callers close with WS_PAYMENT_REQUIRED (4402) when this returns False.
    """
    return SubscriptionService(db).resolve_access(user).state in PREMIUM_STATES
