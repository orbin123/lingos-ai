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
from app.modules.curriculum.exceptions import EnrollmentNotActive, NotEnrolled
from app.modules.curriculum.models import CurriculumDay, EnrollmentStatus, UserEnrollment
from app.modules.curriculum.repository import (
    CurriculumDayRepository,
    CurriculumWeekRepository,
    UserEnrollmentRepository,
)
from app.modules.preferences.models import UserCoursePreference
from app.modules.preferences.service import PreferenceService
from app.modules.sessions.exceptions import (
    AttemptAlreadySubmitted,
    AttemptNotFound,
    DayNotFound,
    InvalidTasksPerDay,
    NoActivitiesPlanned,
    SessionAdvanceBlocked,
    SessionAbandoned,
    SessionAlreadyCompleted,
    SessionAlreadyOpen,
    SessionNotFound,
)
from app.modules.sessions.schemas import (
    AdvanceDayResponse,
    AttemptSkeleton,
    DashboardPlanActivity,
    DashboardStartResponse,
    DashboardTodayPlanResponse,
    EvaluationRead,
    FeedbackRead,
    MistakeRead,
    NextActivityResponse,
    ActivityBreakdown,
    SessionScorecardRead,
    SessionStartRequest,
    SessionStartResponse,
    SubmitActivityRequest,
    SubmitActivityResponse,
)
from app.modules.sessions.service import SessionService
from app.modules.sessions.models import AttemptStatus, DailySession, SessionStatus
from app.modules.sessions.planner import plan_session
from app.modules.sessions.repository import DailySessionRepository
from app.modules.skills.repository import SkillRepository
from app.scoring import CourseLength, get_archetype


def _get_user_interests(db: Session, user_id: int) -> list[str] | None:
    """Return the learner's free-text interests as a single-item list, or None."""
    from app.modules.auth.repository import UserProfileRepository
    profile = UserProfileRepository(db).get_by_user_id(user_id)
    if profile is None or not profile.interests:
        return None
    return [profile.interests.strip()]


def _make_session_service(db: Session) -> SessionService:
    """Construct the production-wired SessionService.

    Imports the LLM factory lazily so test environments that don't load
    OpenAI credentials don't pay the import cost. The factory itself can
    still be patched in tests via dependency injection on the service.
    """
    from app.ai.sessions import build_default_agents
    from app.ai.sessions.factory import build_rag_services
    from app.modules.feedback_memory.rag_service import FeedbackRAGService

    evaluator, feedback_generator, task_generator = build_default_agents()
    service = SessionService(
        db,
        evaluator=evaluator,
        feedback_generator=feedback_generator,
        task_generator=task_generator,
    )

    # Wire RAG services for mentor note generation.
    try:
        embedding_gen, mentor_gen = build_rag_services()
        service._rag_service = FeedbackRAGService(
            db, embedding_generator=embedding_gen,
        )
        service._mentor_generator = mentor_gen
    except Exception:
        # RAG is optional — if Pinecone/OpenAI embeddings aren't configured,
        # the service runs without mentor notes.
        import logging
        logging.getLogger(__name__).warning(
            "RAG services unavailable — mentor notes disabled", exc_info=True,
        )

    return service


logger = logging.getLogger(__name__)


router = APIRouter(prefix="/sessions", tags=["sessions"])


# ── POST /sessions/start ───────────────────────────────────────────


def _course_length_for_enrollment(enrollment: UserEnrollment) -> str:
    return f"{enrollment.course.duration_weeks}w"


def _day_id_for_enrollment(enrollment: UserEnrollment) -> str:
    return (
        f"day_{enrollment.course.duration_weeks}_"
        f"{enrollment.current_week:02d}_{enrollment.current_day_in_week:02d}"
    )


def _allowed_activities_for_enrollment(enrollment: UserEnrollment) -> set[str]:
    allowed: set[str] = set()
    if enrollment.allow_reading:
        allowed.add("read")
    if enrollment.allow_writing:
        allowed.add("write")
    if enrollment.allow_listening:
        allowed.add("listen")
    if enrollment.allow_speaking:
        allowed.add("speak")
    return allowed


def _active_enrollment_for_user(db: Session, user_id: int) -> UserEnrollment:
    enrollment = UserEnrollmentRepository(db).get_for_user(user_id)
    if enrollment is None:
        raise NotEnrolled("User is not enrolled in a course")
    if enrollment.status is not EnrollmentStatus.ACTIVE:
        raise EnrollmentNotActive("User enrollment is not active")
    return enrollment


def _activity_from_attempt(attempt) -> DashboardPlanActivity:
    spec = get_archetype(attempt.archetype_id)
    return DashboardPlanActivity(
        sequence=attempt.sequence,
        archetype_id=attempt.archetype_id,
        archetype_name=spec.name,
        core_activity=spec.core_activity,
        ui_widget=spec.ui_widget,
        is_mandatory=attempt.is_mandatory,
        status=attempt.status,
    )


def _activity_from_plan(plan) -> DashboardPlanActivity:
    spec = get_archetype(plan.archetype_id)
    return DashboardPlanActivity(
        sequence=plan.sequence,
        archetype_id=plan.archetype_id,
        archetype_name=spec.name,
        core_activity=spec.core_activity,
        ui_widget=spec.ui_widget,
        is_mandatory=plan.is_mandatory,
        status=AttemptStatus.PENDING,
    )


def _serialize_dashboard_plan(
    *,
    day_id: str,
    topic: str,
    session: DailySession | None,
    activities: list[DashboardPlanActivity],
    is_preview: bool,
    mode: str | None = None,
) -> DashboardTodayPlanResponse | DashboardStartResponse:
    payload = {
        "day_id": day_id,
        "topic": topic,
        "session_id": session.session_id if session is not None else None,
        "status": session.status if session is not None else None,
        "is_preview": is_preview,
        "activities": activities,
    }
    if mode is not None:
        return DashboardStartResponse(**payload, mode=mode)
    return DashboardTodayPlanResponse(**payload)


def _load_existing_today_session(
    db: Session, *, user_id: int, day_id: str
) -> DailySession | None:
    sessions_repo = DailySessionRepository(db)
    in_progress = sessions_repo.get_latest_for_day(
        user_id=user_id, day_id=day_id, status=SessionStatus.IN_PROGRESS
    )
    if in_progress is not None:
        return in_progress
    return sessions_repo.get_latest_for_day(
        user_id=user_id, day_id=day_id, status=SessionStatus.COMPLETED
    )


def _resolve_day_from_preference(
    db: Session, user_id: int
) -> tuple[CurriculumDay, UserCoursePreference]:
    """Resolve today's curriculum day from UserCoursePreference (V2 path).

    Returns (day, pref). Raises DayNotFound if curriculum is not seeded.
    """
    pref = PreferenceService(db).get(user_id=user_id)
    week = CurriculumWeekRepository(db).get_by_number(
        course_length=pref.course_length,
        week_number=pref.current_week,
    )
    if week is None:
        raise DayNotFound(
            f"No curriculum week for course_length={pref.course_length!r} "
            f"week={pref.current_week}"
        )
    day = CurriculumDayRepository(db).get_for_week(
        week_pk=week.id, day_number=pref.current_day_in_week,
    )
    if day is None:
        raise DayNotFound(
            f"No curriculum day for week_id={week.week_id!r} "
            f"day={pref.current_day_in_week}"
        )
    return day, pref


def _allowed_for_pref(pref: UserCoursePreference) -> set[str]:
    return {
        activity
        for activity, on in {
            "read": pref.allow_read,
            "write": pref.allow_write,
            "listen": pref.allow_listen,
            "speak": pref.allow_speak,
        }.items()
        if on
    }


@router.get(
    "/today-plan",
    response_model=DashboardTodayPlanResponse,
)
def today_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardTodayPlanResponse:
    try:
        day, pref = _resolve_day_from_preference(db, current_user.id)
        day_id = day.day_id
        existing = _load_existing_today_session(db, user_id=current_user.id, day_id=day_id)
        if existing is not None:
            return _serialize_dashboard_plan(
                day_id=day_id,
                topic=day.topic,
                session=existing,
                activities=[_activity_from_attempt(a) for a in existing.attempts],
                is_preview=False,
            )
        planned = plan_session(
            day,
            tasks_per_day=pref.tasks_per_day,
            allowed_activities=_allowed_for_pref(pref),
        )
        return _serialize_dashboard_plan(
            day_id=day_id,
            topic=day.topic,
            session=None,
            activities=[_activity_from_plan(a) for a in planned],
            is_preview=True,
        )
    except DayNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except NoActivitiesPlanned as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/advance-day",
    response_model=AdvanceDayResponse,
)
def advance_day(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AdvanceDayResponse:
    try:
        service = SessionService(db)
        week, day_in_week = service.advance_day(user_id=current_user.id)
        return AdvanceDayResponse(week=week, day_in_week=day_in_week)
    except DayNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except SessionAdvanceBlocked as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/today/start-or-continue",
    response_model=DashboardStartResponse,
)
async def start_or_continue_today(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DashboardStartResponse:
    try:
        day, pref = _resolve_day_from_preference(db, current_user.id)
        day_id = day.day_id
        existing = _load_existing_today_session(db, user_id=current_user.id, day_id=day_id)
        if existing is not None:
            mode = (
                "continue"
                if existing.status is SessionStatus.IN_PROGRESS
                else "completed"
            )
            return _serialize_dashboard_plan(
                day_id=day_id,
                topic=day.topic,
                session=existing,
                activities=[_activity_from_attempt(a) for a in existing.attempts],
                is_preview=False,
                mode=mode,
            )
        service = _make_session_service(db)
        session = await service.start_session(
            user_id=current_user.id,
            day_id=day_id,
            course_length=CourseLength(pref.course_length),
            tasks_per_day=pref.tasks_per_day,
            allowed_activities=_allowed_for_pref(pref),
            user_interests=_get_user_interests(db, current_user.id),
        )
        return _serialize_dashboard_plan(
            day_id=day_id,
            topic=day.topic,
            session=session,
            activities=[_activity_from_attempt(a) for a in session.attempts],
            is_preview=False,
            mode="start",
        )
    except DayNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (InvalidTasksPerDay, NoActivitiesPlanned) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except SessionAlreadyOpen as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


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
            week_number=payload.week_number,
            day_index=payload.day_index,
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
async def next_activity(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NextActivityResponse:
    try:
        service = _make_session_service(db)
        attempt = service.next_activity(session_id=session_id, user_id=current_user.id)
        attempt = await service.prepare_attempt_for_delivery(attempt)
        spec = get_archetype(attempt.archetype_id)
        task_content = dict(attempt.task_content or {})
        if (
            task_content.get("widget") == "listen_and_respond"
            and not task_content.get("audio_url")
            and str(task_content.get("audio_script") or "").strip()
        ):
            task_content.setdefault("browser_tts_fallback", True)
        return NextActivityResponse(
            sequence=attempt.sequence,
            archetype_id=attempt.archetype_id,
            is_mandatory=attempt.is_mandatory,
            status=attempt.status,
            ui_widget=spec.ui_widget,
            task_content=task_content,
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
        activities=[
            ActivityBreakdown.model_validate(a) for a in (scorecard.activities or [])
        ],
        mentor_note=scorecard.mentor_note,
    )
