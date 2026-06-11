"""Payment-provider exceptions."""


class PaymentProviderError(Exception):
    """The provider rejected or failed the request (non-2xx, network, …)."""
