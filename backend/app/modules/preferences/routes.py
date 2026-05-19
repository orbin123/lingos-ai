"""HTTP routes for per-user course preferences."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.preferences.schemas import (
    UserCoursePreferenceRead,
    UserCoursePreferenceUpdate,
)
from app.modules.preferences.service import PreferenceService


router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("", response_model=UserCoursePreferenceRead)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserCoursePreferenceRead:
    pref = PreferenceService(db).get(user_id=current_user.id)
    return UserCoursePreferenceRead.model_validate(pref)


@router.patch("", response_model=UserCoursePreferenceRead)
def update_preferences(
    payload: UserCoursePreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserCoursePreferenceRead:
    pref = PreferenceService(db).update_settings(
        user_id=current_user.id,
        **payload.model_dump(exclude_unset=True),
    )
    return UserCoursePreferenceRead.model_validate(pref)
