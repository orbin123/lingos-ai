"""Auth HTTP routes - translates between HTTP and AuthService"""

import logging
from datetime import timedelta
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.email import get_default_email_client
from app.email.exceptions import EmailError
from app.email.templates import account_exists_email
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.exceptions import (
    EmailAlreadyExists,
    EmailDeliveryFailed,
    EmailNotVerified,
    InvalidCredentials,
    InvalidRefreshToken,
    OtpAttemptsExceeded,
    OtpCooldownActive,
    OtpMismatch,
    OtpNotFoundOrExpired,
    OtpSendLimitExceeded,
)
from app.modules.auth.models import (
    ROLE_ADMIN,
    ROLE_LEARNER,
    ROLE_SUPER_ADMIN,
    OAuthAccount,
    OtpPurpose,
    User,
)
from app.modules.auth.otp_service import OtpService
from app.modules.auth.repository import UserProfileRepository
from app.modules.auth.schemas import (
    MessageOut,
    PasswordResetConfirmIn,
    PasswordResetRequestIn,
    ResendOtpIn,
    SignupOut,
    TokenOut,
    UserCreate,
    UserLogin,
    UserOut,
    UserUpdate,
    VerifyEmailIn,
)
from app.modules.auth.service import AuthService
from app.modules.auth.session_service import (
    REFRESH_COOKIE_NAME,
    REFRESH_COOKIE_PATH,
    SessionService,
    _aware,
    _utcnow,
)
from app.modules.personalization.service import PersonalizationService
from app.modules.preferences.repository import UserCoursePreferenceRepository
from app.modules.preferences.schemas import UserCoursePreferenceRead
from app.modules.subscriptions.schemas import NotificationSettings

logger = logging.getLogger(__name__)


# Profile fields whose change should re-trigger the Personalization Engine.
# Keep this list narrow — fields like phone_number or display_name don't
# affect teaching context and shouldn't pay an LLM call.
_PERSONALIZATION_FIELDS: tuple[str, ...] = (
    "personalisation_context",
    "primary_goals",
    "interests",
    "goal",
    "country",
    "native_language",
    "self_assessed_level",
)

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
        # Verification state at mint time — a token minted pre-verification
        # can be told apart even before the DB row is consulted.
        "ver": bool(user.email_verified),
    }


def _set_refresh_cookie(response: Response, raw: str, *, max_age: int) -> None:
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        raw,
        max_age=max_age,
        httponly=True,
        secure=settings.AUTH_COOKIE_SECURE,
        samesite="lax",
        path=REFRESH_COOKIE_PATH,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)


def _issue_token_pair(
    response: Response,
    db: Session,
    user: User,
    *,
    remember: bool = False,
    request: Request | None = None,
) -> TokenOut:
    """Short access token in the body + rotated refresh token as an
    httpOnly cookie. Used by login, verify-email, and the OAuth callback."""
    raw, session = SessionService(db).create_session(
        user=user,
        remember=remember,
        user_agent=request.headers.get("user-agent") if request else None,
        ip=request.client.host if request and request.client else None,
    )
    max_age = int((_aware(session.expires_at) - _utcnow()).total_seconds())
    _set_refresh_cookie(response, raw, max_age=max_age)
    access = create_access_token(
        data=_token_data(user),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES),
    )
    return TokenOut(access_token=access)


def _build_user_out(
    *,
    user: User,
    profile: object | None,
    preference: object | None,
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
        email_verified=user.email_verified,
        roles=_role_names(user),
        role=_primary_role(user),
        diagnosis_completed=bool(profile and profile.diagnosis_completed),
        preference=(
            UserCoursePreferenceRead.model_validate(preference)
            if preference is not None
            else None
        ),
        phone_number=getattr(profile, "phone_number", None) if profile else None,
        country=getattr(profile, "country", None) if profile else None,
        native_language=getattr(profile, "native_language", None) if profile else None,
        primary_goals=_split_csv(getattr(profile, "primary_goals", "") if profile else ""),
        personalisation_context=(
            getattr(profile, "personalisation_context", "") if profile else ""
        ),
        structured_personalisation=(
            getattr(profile, "structured_personalisation", None) if profile else None
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

@router.post("/signup", response_model=SignupOut, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> SignupOut:
    """Register a new user (unverified) and email a verification code.

    The response is identical whether the email was new, already pending
    verification, or already registered — account enumeration is not
    possible through this endpoint. The already-registered owner is told
    by email instead.
    """
    service = AuthService(db)
    try:
        user = service.signup(
            email=payload.email,
            password=payload.password,
            name=payload.name,
        )
    except EmailAlreadyExists:
        existing = service.users.get_by_email(payload.email)
        if existing is not None:
            if existing.email_verified:
                try:
                    subject, html, text = account_exists_email()
                    get_default_email_client().send(
                        to=existing.email, subject=subject, html=html, text=text
                    )
                except EmailError:
                    logger.warning(
                        "account-exists notice failed for an existing email"
                    )
            else:
                # Unverified re-signup: re-issue the code to the existing
                # account; never create a duplicate user.
                try:
                    OtpService(db).issue(
                        user=existing, purpose=OtpPurpose.REGISTRATION
                    )
                except (
                    OtpCooldownActive,
                    OtpSendLimitExceeded,
                    EmailDeliveryFailed,
                ):
                    pass  # response must stay generic
        return SignupOut(email=payload.email)

    try:
        OtpService(db).issue(user=user, purpose=OtpPurpose.REGISTRATION)
    except EmailDeliveryFailed:
        # Account exists but the code never went out — tell the user to hit
        # resend rather than silently stranding them.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "email_send_failed",
                "message": "We couldn't send the verification email. "
                "Please try resending the code.",
            },
        )
    except (OtpCooldownActive, OtpSendLimitExceeded):
        pass  # impossible for a brand-new account, but harmless
    return SignupOut(email=payload.email)


@router.post("/login", response_model=TokenOut)
def login(
    payload: UserLogin,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenOut:
    """Authenticate user; returns a short access token and sets the
    httpOnly refresh cookie."""
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
    except EmailNotVerified:
        # Structured contract the frontend branches on to route the user to
        # the verify-email screen.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "email_unverified",
                "message": "Please verify your email to continue.",
                "email": payload.email,
            },
        )

    return _issue_token_pair(
        response, db, user, remember=payload.remember_me, request=request
    )


@router.post("/verify-email", response_model=TokenOut)
def verify_email(
    payload: VerifyEmailIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenOut:
    """Confirm the registration OTP; on success the user is verified and
    logged in (token returned + refresh cookie set)."""
    try:
        user = OtpService(db).verify(
            email=payload.email,
            purpose=OtpPurpose.REGISTRATION,
            code=payload.code,
        )
    except OtpNotFoundOrExpired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "otp_expired",
                "message": "Code expired or not found — request a new one.",
            },
        )
    except OtpAttemptsExceeded:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "otp_attempts_exceeded",
                "message": "Too many incorrect attempts — request a new code.",
            },
        )
    except OtpMismatch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "otp_invalid", "message": "Incorrect code."},
        )

    return _issue_token_pair(response, db, user, request=request)


@router.post("/refresh", response_model=TokenOut)
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> TokenOut:
    """Rotate the refresh cookie and mint a fresh access token."""
    raw = request.cookies.get(REFRESH_COOKIE_NAME)
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
    )
    if not raw:
        raise invalid

    try:
        new_raw, session = SessionService(db).rotate(raw_token=raw)
    except InvalidRefreshToken:
        _clear_refresh_cookie(response)
        raise invalid

    user = db.get(User, session.user_id)
    if user is None or not user.is_active:
        _clear_refresh_cookie(response)
        raise invalid

    max_age = int((_aware(session.expires_at) - _utcnow()).total_seconds())
    _set_refresh_cookie(response, new_raw, max_age=max_age)
    access = create_access_token(
        data=_token_data(user),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES),
    )
    return TokenOut(access_token=access)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> None:
    """Revoke the presented refresh session and clear the cookie.
    Best-effort — no bearer auth required, never fails."""
    raw = request.cookies.get(REFRESH_COOKIE_NAME)
    if raw:
        SessionService(db).revoke(raw_token=raw)
    _clear_refresh_cookie(response)


@router.post("/resend-otp", response_model=MessageOut)
def resend_otp(
    payload: ResendOtpIn,
    response: Response,
    db: Session = Depends(get_db),
) -> MessageOut:
    """Re-send the registration code. Generic response for unknown or
    already-verified emails (anti-enumeration); rate-limit errors only fire
    for accounts that really received a code."""
    generic = MessageOut(
        message="If an account exists for this email, a new code has been sent."
    )
    user = AuthService(db).users.get_by_email(payload.email)
    if user is None or user.email_verified:
        return generic

    try:
        OtpService(db).issue(user=user, purpose=OtpPurpose.REGISTRATION)
    except OtpCooldownActive as exc:
        response.headers["Retry-After"] = str(exc.retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "otp_cooldown",
                "message": f"Please wait {exc.retry_after}s before requesting "
                "another code.",
                "retry_after": exc.retry_after,
            },
            headers={"Retry-After": str(exc.retry_after)},
        )
    except OtpSendLimitExceeded:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "otp_send_limit",
                "message": "Too many codes requested — try again later.",
            },
        )
    except EmailDeliveryFailed:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "email_send_failed",
                "message": "We couldn't send the email. Please try again.",
            },
        )
    return generic


@router.post("/password-reset/request", response_model=MessageOut)
def password_reset_request(
    payload: PasswordResetRequestIn,
    db: Session = Depends(get_db),
) -> MessageOut:
    """Send a password-reset code. Always generic — never reveals whether
    the account exists. OAuth-only accounts (no password) get no code."""
    user = AuthService(db).users.get_by_email(payload.email)
    if user is not None and user.is_active and user.password_hash is not None:
        try:
            OtpService(db).issue(user=user, purpose=OtpPurpose.PASSWORD_RESET)
        except (OtpCooldownActive, OtpSendLimitExceeded, EmailDeliveryFailed):
            pass  # response must stay generic
    return MessageOut(
        message="If an account exists for this email, a reset code has been sent."
    )


@router.post("/password-reset/confirm", response_model=MessageOut)
def password_reset_confirm(
    payload: PasswordResetConfirmIn,
    db: Session = Depends(get_db),
) -> MessageOut:
    """Set a new password after OTP proof. No auto-login."""
    try:
        user = OtpService(db).verify(
            email=payload.email,
            purpose=OtpPurpose.PASSWORD_RESET,
            code=payload.code,
        )
    except OtpNotFoundOrExpired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "otp_expired",
                "message": "Code expired or not found — request a new one.",
            },
        )
    except OtpAttemptsExceeded:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "otp_attempts_exceeded",
                "message": "Too many incorrect attempts — request a new code.",
            },
        )
    except OtpMismatch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "otp_invalid", "message": "Incorrect code."},
        )

    user.password_hash = hash_password(payload.new_password)
    db.commit()
    # A password reset is a possible account-recovery-from-compromise:
    # kill every existing session so a stolen refresh token dies too.
    SessionService(db).revoke_all_for_user(user_id=user.id)
    return MessageOut(message="Password updated. Please log in.")

@router.get("/me", response_model=UserOut)
def me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserOut:
    """Return the currently logged-in user's profile + diagnosis status."""
    profile = UserProfileRepository(db).get_by_user_id(current_user.id)
    preference = UserCoursePreferenceRepository(db).get_for_user(current_user.id)
    return _build_user_out(user=current_user, profile=profile, preference=preference)


@router.patch("/me", response_model=UserOut)
async def update_me(
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

    # Snapshot the personalization-relevant fields before mutation so we can
    # tell whether a refresh is needed.
    before = {
        field: getattr(profile, field, None) for field in _PERSONALIZATION_FIELDS
    }

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

    personalization_changed = any(
        before[field] != getattr(profile, field, None)
        for field in _PERSONALIZATION_FIELDS
    )
    if personalization_changed:
        await PersonalizationService(db).refresh_for_user(current_user.id)
        db.commit()
        db.refresh(profile)

    preference = UserCoursePreferenceRepository(db).get_for_user(current_user.id)
    return _build_user_out(user=current_user, profile=profile, preference=preference)


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

    # --- Issue our own JWT (short) ---
    jwt_token = create_access_token(
        data=_token_data(user),
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_TTL_MINUTES),
    )

    # --- Redirect frontend with token ---
    # We pass the token as a query param. The frontend reads it and stores it.
    # The refresh token rides as an httpOnly cookie on this redirect response
    # (backend origin), so OAuth logins get silent refresh like password ones.
    destination = "diagnosis" if is_new else "dashboard"
    redirect_url = f"{frontend_base}/callback?token={jwt_token}&next={destination}"

    redirect = RedirectResponse(url=redirect_url)
    raw, session = SessionService(db).create_session(user=user)
    max_age = int((_aware(session.expires_at) - _utcnow()).total_seconds())
    _set_refresh_cookie(redirect, raw, max_age=max_age)
    return redirect
