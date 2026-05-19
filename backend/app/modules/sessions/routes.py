"""REST endpoints for the daily-session lifecycle.

All endpoints require auth (the caller's `user_id` is taken from the JWT).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.curriculum.v2_repository import (
    CurriculumDayRepository,
    CurriculumWeekRepository,
)
from app.modules.preferences.service import PreferenceService
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


def _make_session_service(db: Session) -> SessionService:
    """Construct the production-wired SessionService.

    Imports the LLM factory lazily so test environments that don't load
    OpenAI credentials don't pay the import cost. The factory itself can
    still be patched in tests via dependency injection on the service.
    """
    from app.ai.sessions import build_default_agents

    evaluator, feedback_generator, task_generator = build_default_agents()
    return SessionService(
        db,
        evaluator=evaluator,
        feedback_generator=feedback_generator,
        task_generator=task_generator,
    )


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/sessions", tags=["sessions"])


# ── POST /sessions/start ───────────────────────────────────────────


@router.post(
    "/start",
    response_model=SessionStartResponse,
    status_code=status.HTTP_201_CREATED,
)
async def start_session(
    payload: SessionStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionStartResponse:
    try:
        service = _make_session_service(db)
        course_length = CourseLength(payload.course_length)
        session = await service.start_session(
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


# ── POST /sessions/start-today ─────────────────────────────────────


@router.post(
    "/start-today",
    response_model=SessionStartResponse,
)
async def start_today_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionStartResponse:
    """Find-or-create the user's session for today.

    Reads `UserCoursePreference` to resolve today's `day_id`. Returns:
      - the in-progress session if one already exists (user resumes)
      - the most recent completed/abandoned session for today, if one
        exists (frontend renders "come back tomorrow" / retry as needed)
      - a freshly started session otherwise

    The lower-level `POST /sessions/start` remains available for tests and
    admin tooling that need to pick a specific `day_id` or course length.
    """
    pref = PreferenceService(db).get(user_id=current_user.id)

    week = CurriculumWeekRepository(db).get_by_number(
        course_length=pref.course_length,
        week_number=pref.current_week,
    )
    if week is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No curriculum week for course_length={pref.course_length!r} "
                f"week={pref.current_week}"
            ),
        )
    day = CurriculumDayRepository(db).get_for_week(
        week_pk=week.id, day_number=pref.current_day_in_week,
    )
    if day is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No curriculum day for week_id={week.week_id!r} "
                f"day={pref.current_day_in_week}"
            ),
        )

    service = _make_session_service(db)

    # Resume an existing session for today if one exists. Abandoned sessions
    # are skipped so the user can start a fresh attempt.
    existing = service.sessions_repo.get_latest_for_day(
        user_id=current_user.id, day_id=day.day_id,
    )
    if existing is not None and existing.status.value != "abandoned":
        # Re-fetch with attempts eagerly loaded for serialization.
        full = service.sessions_repo.get_with_attempts(existing.session_id)
        return _serialize_start(full)

    course_length = CourseLength(pref.course_length)
    allowed = {
        activity
        for activity, on in {
            "read": pref.allow_read,
            "write": pref.allow_write,
            "listen": pref.allow_listen,
            "speak": pref.allow_speak,
        }.items()
        if on
    }

    try:
        session = await service.start_session(
            user_id=current_user.id,
            day_id=day.day_id,
            course_length=course_length,
            tasks_per_day=pref.tasks_per_day,
            allowed_activities=allowed,
        )
        return _serialize_start(session)
    except NoActivitiesPlanned as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except InvalidTasksPerDay as exc:
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
        service = _make_session_service(db)
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
async def submit_activity(
    session_id: str,
    sequence: int,
    payload: SubmitActivityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmitActivityResponse:
    try:
        service = _make_session_service(db)
        attempt, evaluation, feedback = await service.submit_activity(
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
async def complete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SessionScorecardRead:
    try:
        service = _make_session_service(db)
        scorecard, report = await service.complete_session(
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
        service = _make_session_service(db)
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
                # Resolved from the in-process registry — no DB round-trip;
                # the DB `task_archetypes` table is seeded from the same
                # source so the values are guaranteed to agree.
                archetype_name=get_archetype(a.archetype_id).name,
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
