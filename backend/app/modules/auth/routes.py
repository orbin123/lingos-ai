"""Auth HTTP routes - translates between HTTP and AuthService"""

from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, decode_token, verify_password
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.exceptions import EmailAlreadyExists, InvalidCredentials
from app.modules.auth.models import ROLE_ADMIN, ROLE_LEARNER, ROLE_SUPER_ADMIN, OAuthAccount, User
from app.modules.auth.repository import UserProfileRepository
from app.modules.auth.schemas import TokenOut, UserCreate, UserLogin, UserOut, UserUpdate
from app.modules.auth.service import AuthService
from app.modules.curriculum.schemas import EnrollmentRead
from app.modules.curriculum.service import EnrollmentService
from app.modules.subscriptions.schemas import NotificationSettings

router = APIRouter()


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _profile_value(value: object) -> str | None:
    if value is None:
        return None
    return getattr(value, "value", str(value))


def _role_names(user: User) -> list[str]:
    return user.role_names()


def _primary_role(user: User) -> str:
    roles = set(_role_names(user))
    if ROLE_SUPER_ADMIN in roles:
        return ROLE_SUPER_ADMIN
    if ROLE_ADMIN in roles:
        return ROLE_ADMIN
    return ROLE_LEARNER


def _token_data(user: User) -> dict[str, object]:
    roles = _role_names(user)
    return {
        "sub": str(user.id),
        "roles": roles,
        "is_superuser": ROLE_SUPER_ADMIN in roles,
    }


def _build_user_out(
    *,
    user: User,
    profile: object | None,
    enrollment: object | None,
) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        display_name=getattr(profile, "display_name", None) or user.name,
        created_at=user.created_at,
        auth_provider="google" if user.password_hash is None else "password",
        is_superuser=ROLE_SUPER_ADMIN in set(_role_names(user)),
        is_active=user.is_active,
        roles=_role_names(user),
        role=_primary_role(user),
        diagnosis_completed=bool(profile and profile.diagnosis_completed),
        enrollment=(
            EnrollmentRead.model_validate(enrollment)
            if enrollment is not None
            else None
        ),
        phone_number=getattr(profile, "phone_number", None) if profile else None,
        country=getattr(profile, "country", None) if profile else None,
        native_language=getattr(profile, "native_language", None) if profile else None,
        primary_goals=_split_csv(getattr(profile, "primary_goals", "") if profile else ""),
        personalisation_context=(
            getattr(profile, "personalisation_context", "") if profile else ""
        ),
        self_assessed_level=(
            _profile_value(getattr(profile, "self_assessed_level", None))
            if profile
            else None
        ),
        goal=_profile_value(getattr(profile, "goal", None)) if profile else None,
        interests=_split_csv(getattr(profile, "interests", "") if profile else ""),
        notifications=NotificationSettings(
            daily_practice_reminder=(
                getattr(profile, "daily_practice_reminder", True) if profile else True
            ),
            streak_reminder=getattr(profile, "streak_reminder", True) if profile else True,
            weekly_progress_email=(
                getattr(profile, "weekly_progress_email", False) if profile else False
            ),
            feature_announcements=(
                getattr(profile, "feature_announcements", False) if profile else False
            ),
        ),
    )

# ---------------------------------------------------------------------------
# Standard email / password routes
# ---------------------------------------------------------------------------

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    """Register a new user"""
    try: 
        user = AuthService(db).signup(
            email=payload.email,
            password=payload.password,
            name=payload.name
        )
    except EmailAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered"
        )
    return UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        display_name=user.name,
        created_at=user.created_at,
        auth_provider="password",
        is_superuser=ROLE_SUPER_ADMIN in set(_role_names(user)),
        is_active=user.is_active,
        roles=_role_names(user),
        role=_primary_role(user),
        diagnosis_completed=False,
        enrollment=None,
        notifications=NotificationSettings(),
    )

@router.post("/login", response_model=TokenOut)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenOut:
    """Authenticate user and return a JWT access token"""
    try: 
        user = AuthService(db).authenticate(
            email=payload.email,
            password=payload.password,
        )
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(data=_token_data(user))
    return TokenOut(access_token=token)

@router.get("/me", response_model=UserOut)
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    """Return the currently logged-in user's profile + diagnosis status."""
    profile = UserProfileRepository(db).get_by_user_id(current_user.id)
    enrollment = EnrollmentService(db).get_for_user(current_user.id)
    return _build_user_out(user=current_user, profile=profile, enrollment=enrollment)


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    """Update editable account/profile fields for the current user."""
    profile_repo = UserProfileRepository(db)
    profile = profile_repo.get_by_user_id(current_user.id)
    if profile is None:
        profile = profile_repo.create_default(current_user.id)

    updates = payload.model_dump(exclude_unset=True)
    if "display_name" in updates and updates["display_name"] is not None:
        profile.display_name = updates["display_name"].strip()

    if "email" in updates and updates["email"] is not None:
        new_email = str(updates["email"]).lower().strip()
        if new_email != current_user.email:
            password = updates.get("password") or ""
            if current_user.password_hash is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Google accounts must re-authenticate with Google to change email.",
                )
            if not verify_password(password, current_user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Password is incorrect.",
                )
            existing = AuthService(db).users.get_by_email(new_email)
            if existing is not None and existing.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email is already registered.",
                )
            current_user.email = new_email

    for field in ("phone_number", "country", "native_language", "personalisation_context"):
        if field in updates:
            value = updates[field]
            setattr(profile, field, value.strip() if isinstance(value, str) else value)

    if "primary_goals" in updates:
        goals = updates["primary_goals"] or []
        profile.primary_goals = ",".join(goal.strip() for goal in goals if goal.strip())

    db.commit()
    db.refresh(current_user)
    db.refresh(profile)
    enrollment = EnrollmentService(db).get_for_user(current_user.id)
    return _build_user_out(user=current_user, profile=profile, enrollment=enrollment)


# ---------------------------------------------------------------------------
# Google OAuth routes
# ---------------------------------------------------------------------------

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

GOOGLE_SCOPES = "openid email profile"


def _google_auth_url(*, state: str | None = None) -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": GOOGLE_SCOPES,
        "access_type": "offline",
        "prompt": "select_account",
    }
    if state:
        params["state"] = state
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


@router.get("/google/login")
def google_login() -> RedirectResponse:
    """
    Step 1 — Redirect the user to Google's consent screen.

    The frontend calls this URL. The browser is redirected to Google.
    After consent, Google redirects back to /auth/google/callback.
    """
    return RedirectResponse(url=_google_auth_url())


@router.post("/google/relink-url")
def google_relink_url(
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Return a Google OAuth URL that relinks the current user's Google login."""
    state = create_access_token(
        data={
            "sub": str(current_user.id),
            "mode": "google_relink",
        }
    )
    return {"auth_url": _google_auth_url(state=state)}


@router.get("/google/callback")
def google_callback(
    code: str = Query(...),
    state: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """
    Step 2 — Google redirects here with a one-time `code`.

    We exchange the code for an access token, fetch the user's profile,
    then find-or-create a user in our DB, issue a JWT, and redirect
    the frontend to the right page (dashboard or diagnosis).
    """
    # --- Exchange code for access token ---
    token_response = httpx.post(
        GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        },
    )

    if token_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange Google code for token",
        )

    google_access_token = token_response.json().get("access_token")

    # --- Fetch user info from Google ---
    userinfo_response = httpx.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {google_access_token}"},
    )

    if userinfo_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch Google user info",
        )

    google_user = userinfo_response.json()
    google_user_id: str = google_user["sub"]        # Google's unique user ID
    email: str = google_user["email"]
    name: str = google_user.get("name", email.split("@")[0])
    frontend_base = settings.frontend_url

    state_payload = decode_token(state) if state else None
    if state_payload and state_payload.get("mode") == "google_relink":
        user_id = int(state_payload["sub"])
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        existing_link = AuthService(db).oauth_accounts.get_by_provider(
            provider="google",
            provider_user_id=google_user_id,
        )
        if existing_link is not None and existing_link.user_id != user.id:
            redirect_url = f"{frontend_base}/callback?error=google_account_in_use&next=profile"
            return RedirectResponse(url=redirect_url)

        existing_email_user = AuthService(db).users.get_by_email(email)
        if existing_email_user is not None and existing_email_user.id != user.id:
            redirect_url = f"{frontend_base}/callback?error=email_in_use&next=profile"
            return RedirectResponse(url=redirect_url)

        user_link = (
            db.query(OAuthAccount)
            .filter(OAuthAccount.user_id == user.id, OAuthAccount.provider == "google")
            .first()
        )
        if user_link is None:
            AuthService(db).oauth_accounts.create(
                user_id=user.id,
                provider="google",
                provider_user_id=google_user_id,
            )
        else:
            user_link.provider_user_id = google_user_id

        user.email = email.lower()
        db.commit()
        db.refresh(user)

        jwt_token = create_access_token(data=_token_data(user))
        redirect_url = f"{frontend_base}/callback?token={jwt_token}&next=profile"
        return RedirectResponse(url=redirect_url)

    # --- Find or create the user in our DB ---
    user, is_new = AuthService(db).get_or_create_google_user(
        google_user_id=google_user_id,
        email=email,
        name=name,
    )

    # --- Issue our own JWT ---
    jwt_token = create_access_token(data=_token_data(user))

    # --- Redirect frontend with token ---
    # We pass the token as a query param. The frontend reads it and stores it.
    destination = "diagnosis" if is_new else "dashboard"
    redirect_url = f"{frontend_base}/callback?token={jwt_token}&next={destination}"

    return RedirectResponse(url=redirect_url)
