"""HTTP endpoints for challenge catalog and learner progress reads."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.challenges.schemas import (
    ChallengeAttemptRead,
    ChallengeAttemptSubmitRequest,
    ChallengeDetailRead,
    ChallengeHistoryRead,
    ChallengeListItem,
)
from app.modules.challenges.service import (
    ChallengeAttemptNotFound,
    ChallengeDailyAttemptLimitExceeded,
    ChallengeLevelLocked,
    ChallengeLevelNotFound,
    ChallengeNotFound,
    ChallengeReadService,
)


router = APIRouter(prefix="/v1", tags=["challenges"])


@router.get(
    "/challenges",
    response_model=list[ChallengeListItem],
    status_code=status.HTTP_200_OK,
)
def list_challenges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChallengeListItem]:
    """Return active challenges for the authenticated learner."""
    _ = current_user
    return ChallengeReadService(db).list_challenges()


@router.get(
    "/challenges/{slug}",
    response_model=ChallengeDetailRead,
    status_code=status.HTTP_200_OK,
)
def get_challenge_detail(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChallengeDetailRead:
    """Return challenge details plus this learner's level progress."""
    try:
        return ChallengeReadService(db).get_detail(slug=slug, user_id=current_user.id)
    except ChallengeNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/challenges/{slug}/history",
    response_model=ChallengeHistoryRead,
    status_code=status.HTTP_200_OK,
)
def get_challenge_history(
    slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChallengeHistoryRead:
    """Return the authenticated learner's personal history for a challenge."""
    try:
        return ChallengeReadService(db).get_history(slug=slug, user_id=current_user.id)
    except ChallengeNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/challenge-attempts/{attempt_id}",
    response_model=ChallengeAttemptRead,
    status_code=status.HTTP_200_OK,
)
def get_challenge_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChallengeAttemptRead:
    """Return one challenge attempt if it belongs to the authenticated learner."""
    try:
        attempt = ChallengeReadService(db).get_attempt(
            attempt_id=attempt_id,
            user_id=current_user.id,
        )
    except ChallengeAttemptNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ChallengeAttemptRead.model_validate(attempt)


@router.post(
    "/challenges/{slug}/levels/{level_number}/attempts",
    response_model=ChallengeAttemptRead,
    status_code=status.HTTP_201_CREATED,
)
async def start_challenge_attempt(
    slug: str,
    level_number: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChallengeAttemptRead:
    """Create a timed attempt for one unlocked challenge level."""
    service = ChallengeReadService(db)
    try:
        attempt = await service.start_attempt(
            slug=slug,
            level_number=level_number,
            user_id=current_user.id,
        )
    except ChallengeNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ChallengeLevelNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ChallengeLevelLocked as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ChallengeDailyAttemptLimitExceeded as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    return ChallengeAttemptRead.model_validate(attempt)


@router.post(
    "/challenge-attempts/{attempt_id}/submit",
    response_model=ChallengeAttemptRead,
    status_code=status.HTTP_200_OK,
)
async def submit_challenge_attempt(
    attempt_id: int,
    payload: ChallengeAttemptSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChallengeAttemptRead:
    """Persist raw section responses and return Phase 4 evaluation/feedback."""
    service = ChallengeReadService(db)
    try:
        attempt = await service.submit_attempt(
            attempt_id=attempt_id,
            user_id=current_user.id,
            response_payload=payload.response_payload,
        )
    except ChallengeAttemptNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ChallengeAttemptRead.model_validate(attempt)
