"""HTTP endpoints for the A2Z Challenge game."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.challenges.a2z_game.schemas import (
    A2ZProgressRead,
    AudioChunkResponse,
    FinishRoundRequest,
    FinishRoundResponse,
    StartRoundRequest,
    StartRoundResponse,
)
from app.modules.challenges.a2z_game.service import (
    A2ZChallengeNotFound,
    A2ZGameCompleted,
    A2ZLetterNotAvailable,
    A2ZRestartNotAllowed,
    A2ZRoundNotFound,
    A2ZRoundNotInProgress,
    A2ZService,
)


router = APIRouter(prefix="/challenges/a2z", tags=["a2z-challenge"])


# ── Progress ─────────────────────────────────────────────────────────


@router.get(
    "/progress",
    response_model=A2ZProgressRead,
    status_code=status.HTTP_200_OK,
)
def get_a2z_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> A2ZProgressRead:
    """Return alphabet progress for the authenticated learner."""
    try:
        return A2ZService(db).get_progress(current_user.id)
    except A2ZChallengeNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Rounds ───────────────────────────────────────────────────────────


@router.post(
    "/rounds",
    response_model=StartRoundResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_a2z_round(
    payload: StartRoundRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StartRoundResponse:
    """Start one letter round (spin or pick)."""
    try:
        return A2ZService(db).start_round(
            user_id=current_user.id,
            mode=payload.mode,
            letter=payload.letter,
        )
    except A2ZChallengeNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except A2ZGameCompleted as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except A2ZLetterNotAvailable as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/rounds/{round_id}/audio-chunks",
    response_model=AudioChunkResponse,
    status_code=status.HTTP_200_OK,
)
async def ingest_a2z_audio_chunk(
    round_id: int,
    audio: UploadFile = File(...),
    chunk_index: int = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AudioChunkResponse:
    """Accept one audio chunk, transcribe it, and return newly found words."""
    audio_bytes = await audio.read()
    try:
        return await A2ZService(db).ingest_audio_chunk(
            user_id=current_user.id,
            round_id=round_id,
            audio_bytes=audio_bytes,
            chunk_index=chunk_index,
            content_type=audio.content_type,
        )
    except A2ZRoundNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except A2ZRoundNotInProgress as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/rounds/{round_id}/finish",
    response_model=FinishRoundResponse,
    status_code=status.HTTP_200_OK,
)
def finish_a2z_round(
    round_id: int,
    payload: FinishRoundRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> FinishRoundResponse:
    """Finalize a round: grade transcript and update progress."""
    try:
        return A2ZService(db).finish_round(
            user_id=current_user.id,
            round_id=round_id,
        )
    except A2ZRoundNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except A2ZRoundNotInProgress as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ── Restart ──────────────────────────────────────────────────────────


@router.post(
    "/restart",
    response_model=A2ZProgressRead,
    status_code=status.HTTP_200_OK,
)
def restart_a2z_game(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> A2ZProgressRead:
    """Reset all progress. Only allowed after full completion."""
    try:
        return A2ZService(db).restart_game(current_user.id)
    except A2ZChallengeNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except A2ZRestartNotAllowed as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
