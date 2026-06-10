"""Auth Dependencies - reusable across all protected routes."""

from collections.abc import Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.modules.auth.models import ROLE_LEARNER, ROLE_SUPER_ADMIN, User
from app.modules.auth.repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the currently logged-in user from the JWT in the request.

    Raises:
        HTTPException 401: token missing, invalid, expired, or user not found.
    """

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_error

    token = credentials.credentials

    payload = decode_token(token)
    
    if payload is None:
        raise credentials_error

    user_id_raw = payload.get("sub")
    
    if user_id_raw is None:
        raise credentials_error

    # JWT 'sub' is always a string by spec, so we cast back to int
    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        raise credentials_error

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise credentials_error

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


def require_auth(current_user: User = Depends(get_current_user)) -> User:
    """Dependency alias for authenticated endpoints."""
    return current_user


def require_role(required_roles: Iterable[str]):
    """Dependency factory for role-protected endpoints."""
    required = set(required_roles)

    def _dependency(current_user: User = Depends(require_auth)) -> User:
        if not current_user.has_any_role(required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return current_user

    return _dependency


# Learner-surface guard. Inclusive by design: User.role_names() defaults to
# "learner" when no role rows exist, and admins typically also hold the
# learner role. Super admins are allowed through (owner accounts predate the
# role tables and may hold only admin roles); a token scoped exclusively to
# the plain "admin" role is rejected.
require_learner = require_role([ROLE_LEARNER, ROLE_SUPER_ADMIN])


def require_permission(permission_key: str):
    """Dependency factory for permission-protected endpoints."""

    def _dependency(current_user: User = Depends(require_auth)) -> User:
        if not current_user.has_permission(permission_key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission_key}",
            )
        return current_user

    return _dependency


def require_super_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency for super-admin-only endpoints."""
    if not current_user.has_any_role({ROLE_SUPER_ADMIN}):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )
    return current_user


def require_superuser(current_user: User = Depends(require_super_admin)) -> User:
    """Backward-compatible alias for existing superuser-only endpoints."""
    return current_user
