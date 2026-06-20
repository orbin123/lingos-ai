"""Razorpay payment endpoints: create-order, verify, webhook."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import require_verified
from app.modules.auth.models import User
from app.modules.subscriptions.exceptions import PlanNotFound
from app.modules.subscriptions.payment_service import (
    PaymentNotFound,
    PaymentService,
    SignatureInvalid,
    WebhookDuplicate,
)
from app.modules.subscriptions.routes import _entitlement_out
from app.modules.subscriptions.schemas import (
    CreateOrderIn,
    CreateOrderOut,
    EntitlementRead,
    PaymentDetailRead,
    PaymentVerifyIn,
)
from app.payments.exceptions import PaymentProviderError

logger = logging.getLogger(__name__)

payments_router = APIRouter(prefix="/api/payments", tags=["payments"])


@payments_router.post("/create-order", response_model=CreateOrderOut)
def create_order(
    payload: CreateOrderIn,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
) -> CreateOrderOut:
    """Create a Razorpay order for a catalog plan (server-side amount)."""
    try:
        order = PaymentService(db).create_order(current_user, payload.plan_id)
    except PlanNotFound:
        raise HTTPException(status_code=404, detail="Unknown plan.")
    except PaymentProviderError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "payment_provider_error",
                "message": "Could not reach the payment provider. Try again.",
            },
        )
    return CreateOrderOut(**order)


@payments_router.post("/verify", response_model=EntitlementRead)
def verify_payment(
    payload: PaymentVerifyIn,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
) -> EntitlementRead:
    """Checkout success callback: verify the signature, then activate."""
    service = PaymentService(db)
    try:
        service.verify_checkout(
            current_user,
            order_id=payload.razorpay_order_id,
            payment_id=payload.razorpay_payment_id,
            signature=payload.razorpay_signature,
        )
    except PaymentNotFound:
        raise HTTPException(status_code=404, detail="Order not found.")
    except SignatureInvalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "signature_invalid",
                "message": "Payment verification failed.",
            },
        )
    return _entitlement_out(service.subscriptions.resolve_access(current_user))


@payments_router.get("/by-order/{order_id}", response_model=PaymentDetailRead)
def get_payment_by_order(
    order_id: str,
    current_user: User = Depends(require_verified),
    db: Session = Depends(get_db),
) -> PaymentDetailRead:
    """Server-verified proof for the Payment Success page.

    User-scoped: the lookup filters by ``current_user.id``, so requesting
    another user's order returns 404 (no IDOR).
    """
    try:
        detail = PaymentService(db).get_payment_detail(current_user, order_id)
    except PaymentNotFound:
        raise HTTPException(status_code=404, detail="Order not found.")
    return PaymentDetailRead(**detail)


@payments_router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_razorpay_signature: str | None = Header(default=None),
    x_razorpay_event_id: str | None = Header(default=None),
) -> dict[str, bool]:
    """Razorpay webhook — no JWT; authenticated by the webhook signature."""
    if not x_razorpay_signature:
        raise HTTPException(status_code=400, detail="Missing signature.")

    raw_body = await request.body()
    try:
        PaymentService(db).handle_webhook(
            raw_body=raw_body,
            signature=x_razorpay_signature,
            event_id_header=x_razorpay_event_id,
        )
    except SignatureInvalid:
        raise HTTPException(status_code=400, detail="Invalid signature.")
    except WebhookDuplicate:
        return {"ok": True}  # duplicate delivery — acknowledged, not reprocessed
    return {"ok": True}
