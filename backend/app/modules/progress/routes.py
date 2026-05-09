"""HTTP endpoints for the progress module."""

from datetime import datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.progress.models import SkillPoints
from app.modules.progress.repository import ProgressLogRepository, SkillPointsLogRepository
from app.modules.progress.schemas import (
    ProgressLogPoint,
    RecentActivity,
    SkillPointsLogRead,
    SkillPointsRead,
    SkillScoreSnapshot,
    StatsDashboard,
    StatsFeedback,
    StatsMistake,
    WeeklySnapshot,
)
from app.modules.responses.models import Evaluation, UserResponse
from app.modules.skills.repository import UserSkillScoreRepository
from app.modules.tasks.models import UserTask, UserTaskStatus

router = APIRouter(prefix="/progress", tags=["progress"])

WEEKLY_TASK_GOAL = 7


def _week_start(now: datetime) -> datetime:
    local_now = now.astimezone(timezone.utc)
    start_date = local_now.date() - timedelta(days=local_now.weekday())
    return datetime.combine(start_date, time.min, tzinfo=timezone.utc)


def _task_type_value(task_type: object) -> str:
    return getattr(task_type, "value", str(task_type))


def _fallback_strengths(scores: list[SkillScoreSnapshot]) -> list[str]:
    if not scores:
        return [
            "Complete a few tasks to surface your strongest patterns.",
            "Your score profile will become more precise as feedback accumulates.",
            "Consistent practice will reveal which sub-skills are leading.",
        ]
    top_scores = sorted(scores, key=lambda score: score.score, reverse=True)[:3]
    return [
        f"{score.skill_name.replace('_', ' ').title()} is currently tracking at {score.score:.1f}."
        for score in top_scores
    ]


def _fallback_focus_areas(scores: list[SkillScoreSnapshot]) -> list[str]:
    if not scores:
        return [
            "Finish the diagnosis and first tasks to unlock focus areas.",
            "The Feedback Agent will highlight repeated mistakes here.",
            "Your weakest sub-skills will update after evaluated tasks.",
        ]
    low_scores = sorted(scores, key=lambda score: score.score)[:3]
    return [
        f"Spend extra reps on {score.skill_name.replace('_', ' ').title()}."
        for score in low_scores
    ]


def _feedback_list(body: dict, *, kind: str) -> list[str]:
    candidates: list[str] = []
    keys = (
        ["strengths", "what_went_well", "positive_patterns"]
        if kind == "strengths"
        else ["focus_areas", "areas_to_improve", "improvement_areas"]
    )
    for key in keys:
        value = body.get(key)
        if isinstance(value, list):
            candidates.extend(str(item) for item in value if item)
        elif isinstance(value, str) and value.strip():
            candidates.append(value)

    if kind == "focus":
        errors = body.get("errors")
        if isinstance(errors, list):
            for error in errors[:3]:
                if isinstance(error, dict):
                    why_wrong = error.get("why_wrong")
                    rule = error.get("rule")
                    if why_wrong:
                        candidates.append(str(why_wrong))
                    elif rule:
                        candidates.append(str(rule))

    if kind == "strengths":
        message = body.get("overall_message")
        if isinstance(message, str) and message.strip():
            candidates.append(message)

    return candidates[:3]


def _mistakes_from_feedback(body: dict) -> list[StatsMistake]:
    errors = body.get("errors")
    if not isinstance(errors, list):
        return []

    mistakes: list[StatsMistake] = []
    for error in errors[:3]:
        if not isinstance(error, dict):
            continue
        issue = (
            error.get("user_answer")
            or error.get("why_wrong")
            or error.get("error_type")
            or "Review this answer."
        )
        correction = error.get("correct_answer") or error.get("rule") or error.get("memory_tip")
        mistakes.append(
            StatsMistake(
                label="Mistake:",
                issue=str(issue),
                correction=str(correction) if correction else None,
            )
        )
    return mistakes


def _strength_from_feedback(body: dict, score: float) -> StatsMistake:
    strengths = _feedback_list(body, kind="strengths")
    issue = strengths[0] if strengths else f"Strong task performance at {score:.1f}."
    suggestion = body.get("practice_suggestion")
    return StatsMistake(
        label="Strength:",
        issue=issue,
        correction=str(suggestion) if suggestion else None,
    )


@router.get(
    "/scores",
    response_model=list[SkillScoreSnapshot],
    status_code=status.HTTP_200_OK,
)
def get_current_scores(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SkillScoreSnapshot]:
    """Return the user's current score on every tracked skill.

    Used by the dashboard spider chart. Returns an empty list if the
    user has not completed diagnosis yet (no rows seeded).
    """
    rows = UserSkillScoreRepository(db).get_for_user(current_user.id)
    return [
        SkillScoreSnapshot(
            skill_id=row.skill_id,
            skill_name=row.skill.name,
            score=float(row.score),
        )
        for row in rows
    ]


@router.get(
    "/history",
    response_model=list[ProgressLogPoint],
    status_code=status.HTTP_200_OK,
)
def get_skill_history(
    skill_id: int = Query(..., gt=0, description="Skill to fetch history for"),
    days: int = Query(
        30, ge=1, le=365, description="Window size in days (max 365)"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProgressLogPoint]:
    """Return score history for ONE skill over the last `days` days.

    Used by the dashboard line chart. Points are ordered oldest → newest.
    Empty list if there are no logs in the window.
    """
    rows = ProgressLogRepository(db).list_for_user_skill(
        user_id=current_user.id,
        skill_id=skill_id,
        days=days,
    )
    return [ProgressLogPoint.model_validate(row) for row in rows]


@router.get(
    "/stats",
    response_model=StatsDashboard,
    status_code=status.HTTP_200_OK,
)
def get_stats_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StatsDashboard:
    """Return the authenticated stats page data.

    The weekly snapshot is aggregated from Evaluation Agent scores, while
    strengths, focus areas, and mistake rows are derived from persisted
    Feedback Agent responses.
    """
    now = datetime.now(timezone.utc)
    current_week_start = _week_start(now)
    previous_week_start = current_week_start - timedelta(days=7)

    scores = [
        SkillScoreSnapshot(
            skill_id=row.skill_id,
            skill_name=row.skill.name,
            score=float(row.score),
        )
        for row in UserSkillScoreRepository(db).get_for_user(current_user.id)
    ]

    def average_score(start: datetime, end: datetime) -> float | None:
        value = (
            db.query(func.avg(Evaluation.overall_score))
            .join(UserResponse, UserResponse.id == Evaluation.response_id)
            .join(UserTask, UserTask.id == UserResponse.user_task_id)
            .filter(
                UserTask.user_id == current_user.id,
                Evaluation.created_at >= start,
                Evaluation.created_at < end,
            )
            .scalar()
        )
        return float(value) if value is not None else None

    current_average = average_score(current_week_start, now)
    previous_average = average_score(previous_week_start, current_week_start)
    score_change = (
        round(current_average - previous_average, 1)
        if current_average is not None and previous_average is not None
        else 0.0
    )

    tasks_completed = (
        db.query(func.count(UserTask.id))
        .filter(
            UserTask.user_id == current_user.id,
            UserTask.status == UserTaskStatus.COMPLETED,
            UserTask.completed_at >= current_week_start,
        )
        .scalar()
        or 0
    )

    best_skill = max(scores, key=lambda score: score.score, default=None)

    recent_rows = (
        db.query(UserTask)
        .filter(
            UserTask.user_id == current_user.id,
            UserTask.status == UserTaskStatus.COMPLETED,
        )
        .options(joinedload(UserTask.task))
        .order_by(UserTask.completed_at.desc().nullslast(), UserTask.created_at.desc())
        .limit(3)
        .all()
    )

    recent_activities: list[RecentActivity] = []
    feedback_bodies: list[dict] = []

    for user_task in recent_rows:
        response = (
            db.query(UserResponse)
            .filter(UserResponse.user_task_id == user_task.id)
            .first()
        )
        evaluation = response.evaluation if response is not None else None
        feedback = evaluation.feedback if evaluation is not None else None
        body = feedback.body if feedback is not None else {}
        if body:
            feedback_bodies.append(body)

        score = float(evaluation.overall_score) if evaluation is not None else 0.0
        mistakes = _mistakes_from_feedback(body)
        recent_activities.append(
            RecentActivity(
                id=user_task.id,
                task_name=user_task.task.title,
                task_type=_task_type_value(user_task.task.task_type),
                completed_at=user_task.completed_at or user_task.created_at,
                score=score,
                mistake_count=len(mistakes),
                mistakes=[] if score >= 8 else mistakes,
                strength=_strength_from_feedback(body, score) if score >= 8 else None,
            )
        )

    latest_feedback = feedback_bodies[0] if feedback_bodies else {}
    strengths = _feedback_list(latest_feedback, kind="strengths") or _fallback_strengths(scores)
    focus_areas = _feedback_list(latest_feedback, kind="focus") or _fallback_focus_areas(scores)

    return StatsDashboard(
        weekly_snapshot=WeeklySnapshot(
            overall_score_change=score_change,
            tasks_completed=int(tasks_completed),
            weekly_task_goal=WEEKLY_TASK_GOAL,
            best_skill_name=best_skill.skill_name if best_skill else None,
            best_skill_score=best_skill.score if best_skill else None,
        ),
        skill_scores=scores,
        feedback=StatsFeedback(
            strengths=strengths[:3],
            focus_areas=focus_areas[:3],
        ),
        recent_activities=recent_activities,
    )


@router.get(
    "/skill-points",
    response_model=list[SkillPointsRead],
    status_code=status.HTTP_200_OK,
)
def get_skill_points(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SkillPointsRead]:
    """Return points-based progress for every skill.

    Used by the dashboard to display the gamified progress bars.
    Returns an empty list if the user has no points rows yet.
    """
    rows = (
        db.query(SkillPoints)
        .filter(SkillPoints.user_id == current_user.id)
        .all()
    )
    return [SkillPointsRead.model_validate(row) for row in rows]


@router.get(
    "/points-history",
    response_model=list[SkillPointsLogRead],
    status_code=status.HTTP_200_OK,
)
def get_points_history(
    skill_id: int | None = Query(None, gt=0, description="Filter by skill"),
    limit: int = Query(50, ge=1, le=200, description="Max rows to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SkillPointsLogRead]:
    """Return recent points gains, newest first.

    Optionally filtered by skill_id. Used for "You earned +X points!"
    notifications and the points history timeline.
    """
    repo = SkillPointsLogRepository(db)
    rows = repo.list_for_user(
        user_id=current_user.id,
        skill_id=skill_id,
        limit=limit,
    )
    return [SkillPointsLogRead.model_validate(row) for row in rows]
