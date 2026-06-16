"""Pure signature math for Razorpay checkout + webhooks."""

from __future__ import annotations

import hashlib
import hmac

from app.payments.signatures import (
    verify_checkout_signature,
    verify_webhook_signature,
)

KEY_SECRET = "test_key_secret"
WEBHOOK_SECRET = "test_webhook_secret"


def _sign_checkout(order_id: str, payment_id: str, secret: str) -> str:
    return hmac.new(
        secret.encode(), f"{order_id}|{payment_id}".encode(), hashlib.sha256
    ).hexdigest()


def _sign_webhook(body: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


class TestCheckoutSignature:
    def test_valid(self):
        sig = _sign_checkout("order_1", "pay_1", KEY_SECRET)
        assert verify_checkout_signature(
            order_id="order_1",
            payment_id="pay_1",
            signature=sig,
            key_secret=KEY_SECRET,
        )

    def test_tampered_payment_id(self):
        sig = _sign_checkout("order_1", "pay_1", KEY_SECRET)
        assert not verify_checkout_signature(
            order_id="order_1",
            payment_id="pay_2",
            signature=sig,
            key_secret=KEY_SECRET,
        )

    def test_wrong_secret(self):
        sig = _sign_checkout("order_1", "pay_1", "other_secret")
        assert not verify_checkout_signature(
            order_id="order_1",
            payment_id="pay_1",
            signature=sig,
            key_secret=KEY_SECRET,
        )


class TestWebhookSignature:
    def test_valid(self):
        body = b'{"event": "payment.captured"}'
        sig = _sign_webhook(body, WEBHOOK_SECRET)
        assert verify_webhook_signature(
            raw_body=body, signature=sig, webhook_secret=WEBHOOK_SECRET
        )

    def test_invalid(self):
        body = b'{"event": "payment.captured"}'
        sig = _sign_webhook(body, WEBHOOK_SECRET)
        assert not verify_webhook_signature(
            raw_body=body + b" ", signature=sig, webhook_secret=WEBHOOK_SECRET
        )
