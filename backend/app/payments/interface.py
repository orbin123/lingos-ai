"""Abstract contract for the payment-provider client (Razorpay-shaped)."""

from __future__ import annotations

from typing import Protocol


class IRazorpayClient(Protocol):
    """Order creation against the payment provider.

    Signature verification is NOT part of this interface — it is pure HMAC
    math (see signatures.py) and identical for mock and real providers.
    """

    def create_order(
        self,
        *,
        amount_paise: int,
        currency: str,
        receipt: str,
        notes: dict[str, str],
    ) -> dict:
        """Create a provider order; return at least {"id", "amount", "currency"}.

        Raises PaymentProviderError on provider failure.
        """
        ...
