"""Small helpers for masking secrets in admin monitoring surfaces."""

from __future__ import annotations

import re
from typing import Any


MASK = "[REDACTED]"

_SENSITIVE_KEY_PARTS = (
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "password",
    "provider_customer_id",
    "provider_payment_id",
    "provider_subscription_id",
    "secret",
    "token",
)
_OPENAI_KEY_RE = re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b")
_BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]+", re.IGNORECASE)
_ASSIGNMENT_RE = re.compile(
    r"\b(api[_-]?key|authorization|cookie|password|secret|token)\b"
    r"\s*[:=]\s*([^\s,;]+)",
    re.IGNORECASE,
)


def is_sensitive_key(key: str) -> bool:
    normalized = key.strip().lower().replace("-", "_")
    return any(part in normalized for part in _SENSITIVE_KEY_PARTS)


def mask_sensitive_text(value: str | None) -> str | None:
    if value is None:
        return None
    masked = _OPENAI_KEY_RE.sub(MASK, value)
    masked = _BEARER_RE.sub(f"Bearer {MASK}", masked)
    return _ASSIGNMENT_RE.sub(lambda match: f"{match.group(1)}={MASK}", masked)


def sanitize_for_admin(value: Any) -> Any:
    """Recursively mask obvious secrets in JSON-like values."""
    if isinstance(value, dict):
        clean: dict[str, Any] = {}
        for key, item in value.items():
            key_str = str(key)
            clean[key_str] = MASK if is_sensitive_key(key_str) else sanitize_for_admin(item)
        return clean
    if isinstance(value, list):
        return [sanitize_for_admin(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize_for_admin(item) for item in value]
    if isinstance(value, str):
        return mask_sensitive_text(value)
    return value
