"""Razorpay signature verification — pure functions, no I/O.

Checkout: HMAC-SHA256 over "order_id|payment_id" with the key secret.
Webhook:  HMAC-SHA256 over the raw request body with the webhook secret.
Both compare with hmac.compare_digest; signatures are verified then
discarded, never persisted (§13).
"""

from __future__ import annotations

import hashlib
import hmac


def verify_checkout_signature(
    *,
    order_id: str,
    payment_id: str,
    signature: str,
    key_secret: str,
) -> bool:
    expected = hmac.new(
        key_secret.encode("utf-8"),
        f"{order_id}|{payment_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_webhook_signature(
    *,
    raw_body: bytes,
    signature: str,
    webhook_secret: str,
) -> bool:
    expected = hmac.new(
        webhook_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
