"""Streak HTTP endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.streaks.schemas import StreakDataResponse
from app.modules.streaks.service import StreakService

router = APIRouter(prefix="/streak", tags=["streak"])


@router.get("/me", response_model=StreakDataResponse)
def get_my_streak(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreakDataResponse:
    return StreakService(db).get_streak_data(user_id=current_user.id)


@router.patch("/animation-seen", response_model=StreakDataResponse)
def mark_animation_seen(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StreakDataResponse:
    return StreakService(db).mark_animation_seen(user_id=current_user.id)
