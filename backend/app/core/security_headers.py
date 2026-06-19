"""Security response headers (G7 — security close-out).

Adds HSTS + a couple of cheap, standard hardening headers to every HTTP
response. HSTS is only meaningful (and only safe) behind real TLS, so the
headers are emitted **only when ENVIRONMENT=production** — local http dev and
tests stay untouched, mirroring the production-only posture of the config guard
in :mod:`app.core.config`.

Pure-ASGI middleware in the same shape as the logging middlewares
(:mod:`app.core.logging`): wrap ``http.response.start`` and append our headers
without overwriting anything an endpoint set explicitly.
"""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import settings

# Short max-age to start (1 day), per the production plan's "start with a short
# max-age" guidance. includeSubDomains covers api/www and siblings under
# lingosai.com (all HTTPS). No `preload` — preload submission is hard to reverse
# and should only follow a long, proven max-age.
_HSTS_VALUE = "max-age=86400; includeSubDomains"

# Header name/value pairs, lower-cased names per the ASGI spec.
_SECURITY_HEADERS: tuple[tuple[bytes, bytes], ...] = (
    (b"strict-transport-security", _HSTS_VALUE.encode("latin-1")),
    (b"x-content-type-options", b"nosniff"),
)


class SecurityHeadersMiddleware:
    """Append HSTS + ``X-Content-Type-Options`` to production HTTP responses.

    No-op outside ``ENVIRONMENT=production`` and for non-http scopes. Never
    overwrites a header an endpoint already set (checked case-insensitively).
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self._enabled = settings.environment == "production"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self._enabled or scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: MutableMapping[str, Any]) -> None:
            if message["type"] == "http.response.start":
                headers: list[tuple[bytes, bytes]] = list(message.get("headers") or [])
                existing = {name.lower() for name, _ in headers}
                for name, value in _SECURITY_HEADERS:
                    if name not in existing:
                        headers.append((name, value))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)
