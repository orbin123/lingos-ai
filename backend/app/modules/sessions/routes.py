"""REST endpoints for the new daily-session lifecycle.

All endpoints require auth (the caller's `user_id` is taken from the JWT).
Gated by `settings.use_new_session_flow` — when off, every route returns 404
so the legacy flow remains the canonical surface.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.sessions.exceptions import (
    AttemptAlreadySubmitted,
    AttemptNotFound,
    DayNotFound,
    InvalidTasksPerDay,
    NoActivitiesPlanned,
    SessionAbandoned,
    SessionAlreadyCompleted,
    SessionAlreadyOpen,
    SessionNotFound,
)
from app.modules.sessions.schemas import (
    AttemptSkeleton,
    EvaluationRead,
    FeedbackRead,
    MistakeRead,
    NextActivityResponse,
    SessionScorecardRead,
    SessionStartRequest,
    SessionStartResponse,
    SubmitActivityRequest,
    SubmitActivityResponse,
)
from app.modules.sessions.service import SessionService
from app.modules.skills.repository import SkillRepository
from app.scoring import CourseLength, get_archetype


logger = logging.getLogger(__name__)


def _ensure_flag_on() -> None:
    """Router-level dependency — short-circuits with 404 when the flag is off.

    Declared at router level (not inside each route function) so it resolves
    BEFORE `get_current_user`. That way an unauthenticated request to a
    flag-off endpoint gets 404 rather than 401, matching the contract that
    the endpoint "doesn't exist" when the flag is off.
    """
    if not settings.use_new_session_flow:
        raise HTTPException(
            status_code=404,
            detail="USE_NEW_SESSION_FLOW is off — new sessions API is disabled",
        )


router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
    dependencies=[Depends(_ensure_flag_on)],
)


# ── POST /sessions/start ───────────────────────────────────────────


@router.post(
    "/start",
    response_model=SessionStartResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_session(
    payload: SessionStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionStartResponse:
    try:
        service = SessionService(db)
        course_length = CourseLength(payload.course_length)
        session = service.start_session(
            user_id=current_user.id,
            day_id=payload.day_id,
            course_length=course_length,
            tasks_per_day=payload.tasks_per_day,
            allowed_activities=payload.preferences.allowed_activities(),
        )
        return _serialize_start(session)
    except DayNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SessionAlreadyOpen as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except InvalidTasksPerDay as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except NoActivitiesPlanned as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# ── GET /sessions/{id}/next-activity ───────────────────────────────


@router.get(
    "/{session_id}/next-activity",
    response_model=NextActivityResponse,
)
def next_activity(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NextActivityResponse:
    try:
        service = SessionService(db)
        attempt = service.next_activity(session_id=session_id, user_id=current_user.id)
        spec = get_archetype(attempt.archetype_id)
        return NextActivityResponse(
            sequence=attempt.sequence,
            archetype_id=attempt.archetype_id,
            is_mandatory=attempt.is_mandatory,
            status=attempt.status,
            ui_widget=spec.ui_widget,
            task_content=attempt.task_content,
        )
    except SessionNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SessionAlreadyCompleted as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SessionAbandoned as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


# ── POST /sessions/{id}/activities/{seq}/submit ────────────────────


@router.post(
    "/{session_id}/activities/{sequence}/submit",
    response_model=SubmitActivityResponse,
)
def submit_activity(
    session_id: str,
    sequence: int,
    payload: SubmitActivityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmitActivityResponse:
    try:
        service = SessionService(db)
        attempt, evaluation, feedback = service.submit_activity(
            session_id=session_id,
            user_id=current_user.id,
            sequence=sequence,
            user_response=payload.user_response,
        )
        return SubmitActivityResponse(
            sequence=attempt.sequence,
            status=attempt.status,
            evaluation=EvaluationRead(
                raw_score=float(evaluation.raw_score),
                rubric_scores=dict(evaluation.rubric_scores),
                base_reward=evaluation.base_reward,
                weighted_points=dict(evaluation.weighted_points),
                evaluator_notes=evaluation.evaluator_notes,
            ),
            feedback=FeedbackRead(
                score=feedback.score,
                summary=feedback.summary,
                did_well=list(feedback.did_well),
                mistakes=[MistakeRead(**m) for m in (feedback.mistakes or [])],
                next_tip=feedback.next_tip,
                sub_skill_breakdown=dict(feedback.sub_skill_breakdown),
            ),
        )
    except SessionNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SessionAlreadyCompleted as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SessionAbandoned as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except AttemptNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AttemptAlreadySubmitted as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


# ── POST /sessions/{id}/complete ───────────────────────────────────


@router.post(
    "/{session_id}/complete",
    response_model=SessionScorecardRead,
)
def complete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionScorecardRead:
    try:
        service = SessionService(db)
        scorecard, report = service.complete_session(
            session_id=session_id, user_id=current_user.id
        )
        logger.info(
            "session %s completed: %s",
            session_id, {"applied": report.applied, "reason": report.reason},
        )
        return _serialize_scorecard(session_id, scorecard, db=db)
    except SessionNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SessionAbandoned as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


# ── GET /sessions/{id}/scorecard ───────────────────────────────────


@router.get(
    "/{session_id}/scorecard",
    response_model=SessionScorecardRead,
)
def get_scorecard(
    session_id: str,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionScorecardRead | None:
    try:
        service = SessionService(db)
        scorecard = service.get_scorecard(session_id=session_id, user_id=current_user.id)
        if scorecard is None:
            raise HTTPException(
                status_code=404,
                detail=f"session {session_id!r} has no scorecard yet",
            )
        return _serialize_scorecard(session_id, scorecard, db=db)
    except SessionNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


# ── Serializers ────────────────────────────────────────────────────


def _serialize_start(session) -> SessionStartResponse:
    return SessionStartResponse(
        session_id=session.session_id,
        day_id=session.day_id,
        course_length=session.course_length,
        status=session.status,
        is_first_attempt=session.is_first_attempt,
        started_at=session.started_at,
        attempts=[
            AttemptSkeleton(
                sequence=a.sequence,
                archetype_id=a.archetype_id,
                is_mandatory=a.is_mandatory,
                status=a.status,
            )
            for a in session.attempts
        ],
    )


def _serialize_scorecard(
    session_id: str,
    scorecard,
    *,
    db: Session,
) -> SessionScorecardRead:
    skill_labels = SkillRepository(db).display_label_map()
    return SessionScorecardRead(
        session_id=session_id,
        points_earned=dict(scorecard.points_earned),
        subskill_totals_after=dict(scorecard.subskill_totals_after),
        dashboard_after=dict(scorecard.dashboard_after),
        skill_labels=skill_labels,
        completed_at=scorecard.completed_at,
        points_applied=scorecard.points_applied,
    )
