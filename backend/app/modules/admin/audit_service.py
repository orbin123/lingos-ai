"""Reusable audit logging for admin actions."""

from __future__ import annotations

from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.modules.admin.models import AdminAuditLog
from app.modules.admin.sanitization import sanitize_for_admin
from app.modules.auth.models import User


class AdminAuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def record(
        self,
        *,
        admin: User,
        action: str,
        resource_type: str,
        resource_id: int | str | None,
        old_value: dict[str, Any] | None = None,
        new_value: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AdminAuditLog:
        log = AdminAuditLog(
            admin_user_id=admin.id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            old_value=sanitize_for_admin(old_value),
            new_value=sanitize_for_admin(new_value),
            ip_address=ip_address,
        )
        self.db.add(log)
        self.db.flush()
        return log


def client_ip_from_request(request: Request | None) -> str | None:
    if request is None:
        return None
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        first_ip = forwarded_for.split(",", 1)[0].strip()
        if first_ip:
            return first_ip
    return request.client.host if request.client else None
