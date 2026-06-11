"""Mock provider for dev/CI — no keys, no network."""

from __future__ import annotations

import logging
from uuid import uuid4

logger = logging.getLogger(__name__)


class MockRazorpayClient:
    """Returns Razorpay-shaped orders without calling the provider.

    Checkout can't complete against a mock order; this exists so order
    creation and the verify/webhook paths are exercisable in dev and tests.
    """

    def create_order(
        self,
        *,
        amount_paise: int,
        currency: str,
        receipt: str,
        notes: dict[str, str],
    ) -> dict:
        order_id = f"order_mock_{uuid4().hex}"
        logger.info("Mock Razorpay order %s (%s %s)", order_id, amount_paise, currency)
        return {
            "id": order_id,
            "entity": "order",
            "amount": amount_paise,
            "currency": currency,
            "receipt": receipt,
            "notes": notes,
            "status": "created",
        }
