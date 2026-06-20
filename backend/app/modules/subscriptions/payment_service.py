"""Payment flow: order creation, checkout verification, webhook handling.

Amounts are always taken from PLAN_CATALOG server-side — client-sent
amounts are never trusted. Activation happens only after a verified
signature (checkout callback) or a signature-verified webhook; both paths
are idempotent so the verify-vs-webhook race is harmless (§14).
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.auth.models import User
from app.modules.subscriptions.catalog import PLAN_CATALOG
from app.modules.subscriptions.exceptions import PlanNotFound, SubscriptionError
from app.modules.subscriptions.models import Payment, PaymentEvent
from app.modules.subscriptions.service import SubscriptionService
from app.payments import get_default_razorpay_client
from app.payments.signatures import (
    verify_checkout_signature,
    verify_webhook_signature,
)

logger = logging.getLogger(__name__)

PROVIDER = "razorpay"


class PaymentNotFound(SubscriptionError):
    """No payment row matches the given order for this user."""


class SignatureInvalid(SubscriptionError):
    """Checkout or webhook signature failed verification."""


class WebhookDuplicate(SubscriptionError):
    """Webhook event_id already processed — caller should no-op with 200."""


class PaymentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.subscriptions = SubscriptionService(db)
        self.client = get_default_razorpay_client()

    # ── order creation ────────────────────────────────────────────────

    def create_order(self, user: User, plan_id: str) -> dict:
        plan = PLAN_CATALOG.get(plan_id)
        if plan is None:
            raise PlanNotFound(plan_id)

        amount_paise = int(round(float(plan["amount_paid"]) * 100))  # type: ignore[arg-type]
        currency = str(plan["currency"])
        order = self.client.create_order(
            amount_paise=amount_paise,
            currency=currency,
            receipt=f"user_{user.id}_{plan_id}",
            notes={"user_id": str(user.id), "plan_id": plan_id},
        )

        payment = Payment(
            user_id=user.id,
            provider=PROVIDER,
            provider_order_id=order["id"],
            amount=float(plan["amount_paid"]),  # type: ignore[arg-type]
            currency=currency,
            status="created",
        )
        self.db.add(payment)
        self.db.commit()

        return {
            "order_id": order["id"],
            "amount": amount_paise,
            "currency": currency,
            "key_id": settings.RAZORPAY_KEY_ID,
            "plan_id": plan_id,
            "plan_name": str(plan["name"]),
        }

    # ── proof read (success page) ─────────────────────────────────────

    def get_payment_detail(self, user: User, order_id: str) -> dict:
        """User-scoped payment lookup backing the Payment Success page.

        Filters by ``user_id`` so a learner can never read another user's
        order (no IDOR — mirrors ``verify_checkout``'s lookup). ``plan_id`` /
        ``plan_name`` are recovered from the server-side amount via the catalog
        (cannot be spoofed); ``subscription_status`` reflects the live,
        lazy-expiry-aware entitlement. ``method`` is null until the webhook
        fills it (the verify fast-path does not set it).
        """
        payment = (
            self.db.query(Payment)
            .filter(
                Payment.provider_order_id == order_id,
                Payment.user_id == user.id,
            )
            .first()
        )
        if payment is None:
            raise PaymentNotFound(order_id)

        try:
            resolved_plan_id = self._plan_id_for(payment)
            plan_id: str | None = resolved_plan_id
            plan_name: str | None = str(PLAN_CATALOG[resolved_plan_id]["name"])
        except PlanNotFound:
            plan_id = None
            plan_name = None

        resolution = self.subscriptions.resolve_access(user)

        return {
            "provider_payment_id": payment.provider_payment_id,
            "provider_order_id": payment.provider_order_id,
            "amount": float(payment.amount),
            "currency": payment.currency,
            "status": payment.status,
            "method": payment.method,
            "paid_at": payment.paid_at,
            "plan_id": plan_id,
            "plan_name": plan_name,
            "subscription_status": resolution.state.value,
            "current_period_end": resolution.current_period_end,
        }

    # ── checkout verification (client callback) ──────────────────────

    def verify_checkout(
        self,
        user: User,
        *,
        order_id: str,
        payment_id: str,
        signature: str,
    ) -> None:
        payment = (
            self.db.query(Payment)
            .filter(
                Payment.provider_order_id == order_id,
                Payment.user_id == user.id,
            )
            .first()
        )
        if payment is None:
            raise PaymentNotFound(order_id)

        if payment.status == "paid":
            return  # already activated (double callback / webhook won race)

        if not verify_checkout_signature(
            order_id=order_id,
            payment_id=payment_id,
            signature=signature,
            key_secret=settings.RAZORPAY_KEY_SECRET,
        ):
            # Reject, log, leave state unchanged (§14) — never activate.
            logger.warning(
                "Razorpay checkout signature mismatch user_id=%s order=%s",
                user.id,
                order_id,
            )
            raise SignatureInvalid(order_id)

        self._mark_paid_and_activate(payment, payment_id=payment_id, user=user)

    # ── webhook (server-authoritative) ────────────────────────────────

    def handle_webhook(
        self,
        *,
        raw_body: bytes,
        signature: str,
        event_id_header: str | None,
    ) -> None:
        if not verify_webhook_signature(
            raw_body=raw_body,
            signature=signature,
            webhook_secret=settings.RAZORPAY_WEBHOOK_SECRET,
        ):
            logger.warning("Razorpay webhook signature mismatch — dropped")
            raise SignatureInvalid("webhook")

        payload = json.loads(raw_body)
        event_type = str(payload.get("event", ""))
        # Razorpay's delivery id arrives in the x-razorpay-event-id header;
        # bodies carry no stable id, so fall back to a body hash (§8.6 note).
        event_id = event_id_header or hashlib.sha256(raw_body).hexdigest()

        event = PaymentEvent(
            provider=PROVIDER,
            event_id=event_id,
            event_type=event_type,
            payload=payload,
        )
        self.db.add(event)
        try:
            self.db.flush()
        except IntegrityError:
            self.db.rollback()
            raise WebhookDuplicate(event_id)  # duplicate delivery → no-op

        if event_type in ("payment.captured", "order.paid"):
            self._handle_payment_captured(payload)
        elif event_type == "payment.failed":
            self._handle_payment_failed(payload)
        else:
            logger.info("Razorpay webhook %s ignored", event_type)

        event.processed_at = datetime.now(timezone.utc)
        self.db.commit()

    # ── internals ─────────────────────────────────────────────────────

    @staticmethod
    def _payment_entity(payload: dict) -> dict:
        return payload.get("payload", {}).get("payment", {}).get("entity", {})

    def _handle_payment_captured(self, payload: dict) -> None:
        entity = self._payment_entity(payload)
        order_id = entity.get("order_id")
        if not order_id:
            logger.warning("Razorpay captured event without order_id — skipped")
            return

        payment = (
            self.db.query(Payment).filter(Payment.provider_order_id == order_id).first()
        )
        if payment is None:
            logger.warning("Razorpay captured event for unknown order %s", order_id)
            return
        if payment.status == "paid":
            # The verify fast-path already activated, but it never sets `method`
            # (the checkout callback doesn't carry it). The webhook is the
            # authoritative source for the instrument and the gateway payment id,
            # so backfill them here — without re-activating — so the success page
            # and admin views show the real method instead of "Processing…". In
            # the common Pay-Now ordering verify wins the race, so this is the
            # only path that ever fills `method`.
            self._backfill_captured_fields(payment, entity)
            return

        user = self.db.get(User, payment.user_id)
        if user is None:
            logger.error("Payment %s has no user — skipped", payment.id)
            return
        notes = entity.get("notes") or {}
        self._mark_paid_and_activate(
            payment,
            payment_id=entity.get("id"),
            user=user,
            method=entity.get("method"),
            plan_id_hint=notes.get("plan_id") if isinstance(notes, dict) else None,
        )

    def _backfill_captured_fields(self, payment: Payment, entity: dict) -> None:
        """Fill `method`/`provider_payment_id` on an already-paid row.

        Only fills fields the verify fast-path left empty — never overwrites an
        existing value, so the `provider_payment_id` unique constraint can't be
        violated (verify and the webhook report the same payment id anyway).
        """
        changed = False
        method = entity.get("method")
        if method and not payment.method:
            payment.method = method
            changed = True
        payment_id = entity.get("id")
        if payment_id and not payment.provider_payment_id:
            payment.provider_payment_id = payment_id
            changed = True
        if changed:
            self.db.flush()

    def _handle_payment_failed(self, payload: dict) -> None:
        entity = self._payment_entity(payload)
        order_id = entity.get("order_id")
        payment = (
            self.db.query(Payment).filter(Payment.provider_order_id == order_id).first()
            if order_id
            else None
        )
        if payment is None or payment.status == "paid":
            return  # unknown order, or a later capture already succeeded
        payment.status = "failed"
        payment.failure_reason = (entity.get("error_description") or "")[:255] or None
        payment.method = entity.get("method")
        self.db.flush()

    def _mark_paid_and_activate(
        self,
        payment: Payment,
        *,
        payment_id: str | None,
        user: User,
        method: str | None = None,
        plan_id_hint: str | None = None,
    ) -> None:
        # Webhooks echo our order notes (which carry plan_id); the checkout
        # verify path falls back to the server-side amount mapping.
        if plan_id_hint and plan_id_hint in PLAN_CATALOG:
            plan_id = plan_id_hint
        else:
            plan_id = self._plan_id_for(payment)
        payment.provider_payment_id = payment_id or payment.provider_payment_id
        payment.status = "paid"
        payment.paid_at = datetime.now(timezone.utc)
        if method:
            payment.method = method
        self.db.flush()
        # activate_from_payment commits the whole unit (payment + subscription).
        self.subscriptions.activate_from_payment(
            user,
            plan_id=plan_id,
            provider=PROVIDER,
            provider_payment_id=payment.provider_payment_id,
        )

    @staticmethod
    def _plan_id_for(payment: Payment) -> str:
        """Recover the plan from the server-side amount (catalog is tiny).

        The amount was written from PLAN_CATALOG at create-order time, so
        this mapping cannot be spoofed by the client.
        """
        for plan_id, plan in PLAN_CATALOG.items():
            if float(plan["amount_paid"]) == float(payment.amount):  # type: ignore[arg-type]
                return plan_id
        raise PlanNotFound(f"no plan with amount {payment.amount}")
