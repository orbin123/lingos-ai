"""Small in-memory rate limiter for sensitive admin/auth surfaces."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Any

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class AdminRateLimitMiddleware:
    """Limit repeated admin API and login requests per client IP.

    This intentionally stays dependency-free. In production with multiple
    workers, replace the in-memory buckets with Redis using the same path
    grouping.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        window_seconds: int = 60,
        login_limit: int = 20,
        admin_limit: int = 300,
    ) -> None:
        self.app = app
        self.window_seconds = window_seconds
        self.login_limit = login_limit
        self.admin_limit = admin_limit
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        route_group = self._route_group(scope)
        if route_group is None:
            await self.app(scope, receive, send)
            return

        limit = self.login_limit if route_group == "auth-login" else self.admin_limit
        key = f"{route_group}:{self._client_ip(scope)}"
        now = time.monotonic()
        allowed = self._allow(key=key, now=now, limit=limit)
        if not allowed:
            response = JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again shortly."},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)

    def _allow(self, *, key: str, now: float, limit: int) -> bool:
        with self._lock:
            bucket = self._hits[key]
            cutoff = now - self.window_seconds
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                return False
            bucket.append(now)
            return True

    def _route_group(self, scope: Scope) -> str | None:
        path = str(scope.get("path") or "")
        method = str(scope.get("method") or "").upper()
        if path == "/auth/login" and method == "POST":
            return "auth-login"
        if path.startswith("/admin"):
            return "admin-api"
        return None

    def _client_ip(self, scope: Scope) -> str:
        headers = {
            key.decode("latin1").lower(): value.decode("latin1")
            for key, value in scope.get("headers", [])
        }
        forwarded_for = headers.get("x-forwarded-for")
        if forwarded_for:
            first_ip = forwarded_for.split(",", 1)[0].strip()
            if first_ip:
                return first_ip
        client: Any = scope.get("client")
        return str(client[0]) if client else "unknown"
