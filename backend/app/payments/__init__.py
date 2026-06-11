"""Payment-provider package (Razorpay Test Mode).

Public surface:

    from app.payments import get_default_razorpay_client
    from app.payments.signatures import (
        verify_checkout_signature, verify_webhook_signature,
    )

Provider selection mirrors app/email: the real httpx client is used iff
both Razorpay keys are configured, otherwise the mock client (orders are
fabricated locally) with a warning — a missing key degrades visibly
instead of crashing dev.
"""

import logging

from app.core.config import settings
from app.payments.exceptions import PaymentProviderError
from app.payments.interface import IRazorpayClient
from app.payments.mock_client import MockRazorpayClient
from app.payments.razorpay_client import RazorpayHttpClient

__all__ = [
    "IRazorpayClient",
    "MockRazorpayClient",
    "PaymentProviderError",
    "RazorpayHttpClient",
    "get_default_razorpay_client",
]

logger = logging.getLogger(__name__)

_default_client: IRazorpayClient | None = None


def get_default_razorpay_client() -> IRazorpayClient:
    """Build (once) and return the configured payment client."""
    global _default_client
    if _default_client is None:
        if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
            _default_client = RazorpayHttpClient()
        else:
            logger.warning(
                "RAZORPAY_KEY_ID/RAZORPAY_KEY_SECRET not configured — "
                "using the mock Razorpay client (orders are not real)"
            )
            _default_client = MockRazorpayClient()
    return _default_client


def _reset_default_razorpay_client() -> None:
    """Test hook: drop the singleton so settings changes take effect."""
    global _default_client
    _default_client = None
