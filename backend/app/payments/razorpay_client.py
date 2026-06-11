"""Razorpay Orders API client via httpx (no SDK, mirrors the Resend client)."""

from __future__ import annotations

import logging

import httpx

from app.core.config import settings
from app.payments.exceptions import PaymentProviderError

logger = logging.getLogger(__name__)

RAZORPAY_API_BASE = "https://api.razorpay.com/v1"
_TIMEOUT_SECONDS = 15.0


class RazorpayHttpClient:
    """Creates orders against the live (test-mode) Razorpay API."""

    def create_order(
        self,
        *,
        amount_paise: int,
        currency: str,
        receipt: str,
        notes: dict[str, str],
    ) -> dict:
        try:
            response = httpx.post(
                f"{RAZORPAY_API_BASE}/orders",
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
                json={
                    "amount": amount_paise,
                    "currency": currency,
                    "receipt": receipt,
                    "notes": notes,
                },
                timeout=_TIMEOUT_SECONDS,
            )
        except httpx.HTTPError as exc:
            raise PaymentProviderError(f"Razorpay request failed: {exc}") from exc

        if response.status_code >= 400:
            # Never log the body verbatim at error level beyond a summary —
            # provider errors can echo notes.
            logger.error(
                "Razorpay order creation failed: status=%s", response.status_code
            )
            raise PaymentProviderError(
                f"Razorpay order creation failed (HTTP {response.status_code})"
            )
        return response.json()
