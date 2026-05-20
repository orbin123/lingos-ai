"""HTTP endpoints for the progress module.

Reads from the daily-sessions flow: ActivityAttempt / ActivityEvaluation /
ActivityFeedback / SessionScorecard (plus the SkillPoints gamification
layer and ProgressLog history).
"""

from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.curriculum.models import CurriculumDay, CurriculumWeek
from app.modules.progress.models import ProgressLog, SkillPoints, SkillPointsLog
from app.modules.progress.repository import (
    ProgressLogRepository,
    SkillPointsLogRepository,
    SkillPointsRepository,
)
from app.modules.progress.schemas import (
    DifficultyDistribution,
    ProgressLogPoint,
    RecentActivity,
    SkillHistorySeries,
    SkillPointsLogRead,
    SkillPointsRead,
    SkillScoreSnapshot,
    StatsDashboard,
    StatsFeedback,
    StatsMistake,
    WeeklySnapshot,
)
from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityEvaluation,
    ActivityFeedback,
    AttemptStatus,
    DailySession,
)
from app.modules.skills.models import Skill
from app.scoring import get_archetype


router = APIRouter(prefix="/progress", tags=["progress"])

WEEKLY_TASK_GOAL = 7

# Map CEFR level → difficulty bucket for the dashboard breakdown. The
# new curriculum carries CEFR at the week level; per-activity difficulty
# does not exist anymore, so we project up to the parent week's level.
_CEFR_TIERS: dict[str, str] = {
    "A1": "beginner",
    "A2": "beginner",
    "B1": "intermediate",
    "B2": "intermediate",
    "C1": "advanced",
    "C2": "advanced",
}


def _week_start(now: datetime) -> datetime:
    local_now = now.astimezone(timezone.utc)
    start_date = local_now.date() - timedelta(days=local_now.weekday())
    return datetime.combine(start_date, time.min, tzinfo=timezone.utc)


def _archetype_name(archetype_id: str) -> str:
    try:
        return get_archetype(archetype_id).name
    except Exception:
        return archetype_id


def _mistakes_from_feedback(fb: ActivityFeedback | None) -> list[StatsMistake]:
    if fb is None or not fb.mistakes:
        return []
    out: list[StatsMistake] = []
    for m in fb.mistakes[:3]:
        if not isinstance(m, dict):
            continue
        issue = m.get("user_wrote") or m.get("issue") or "Review this answer."
        correction = m.get("correction") or m.get("rule")
        out.append(
            StatsMistake(
                label="Mistake:",
                issue=str(issue),
                correction=str(correction) if correction else None,
            )
        )
    return out


def _strength_from_feedback(
    fb: ActivityFeedback | None, score: float
) -> StatsMistake:
    issue = (
        (fb.did_well[0] if fb and fb.did_well else None)
        or f"Strong task performance at {score:.1f}."
    )
    return StatsMistake(
        label="Strength:",
        issue=str(issue),
        correction=str(fb.next_tip) if fb and fb.next_tip else None,
    )


def _fallback_strengths(scores: list[SkillScoreSnapshot]) -> list[str]:
    if not scores:
        return [
            "Complete a few sessions to surface your strongest patterns.",
            "Your score profile will become more precise as feedback accumulates.",
            "Consistent practice will reveal which sub-skills are leading.",
        ]
    top = sorted(scores, key=lambda s: s.score, reverse=True)[:3]
    return [
        f"{s.skill_name.replace('_', ' ').title()} is currently tracking at {s.score:.1f}."
        for s in top
    ]


def _fallback_focus_areas(scores: list[SkillScoreSnapshot]) -> list[str]:
    if not scores:
        return [
            "Finish the diagnosis and first sessions to unlock focus areas.",
            "The Feedback Agent will highlight repeated mistakes here.",
            "Your weakest sub-skills will update after evaluated activities.",
        ]
    low = sorted(scores, key=lambda s: s.score)[:3]
    return [
        f"Spend extra reps on {s.skill_name.replace('_', ' ').title()}."
        for s in low
    ]


def _build_activity(att: ActivityAttempt) -> RecentActivity:
    ev = att.evaluation
    fb = att.feedback
    score = float(ev.raw_score) if ev is not None else 0.0
    mistakes = _mistakes_from_feedback(fb)
    return RecentActivity(
        id=att.id,
        user_task_id=att.id,
        task_name=_archetype_name(att.archetype_id),
        task_type=att.archetype_id,
        completed_at=att.submitted_at or att.created_at,
        score=score,
        mistake_count=len(mistakes),
        mistakes=[] if score >= 8 else mistakes,
        strength=_strength_from_feedback(fb, score) if score >= 8 else None,
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
    """Return the user's current display score on every tracked skill."""
    rows = SkillPointsRepository(db).get_all_for_user(current_user.id)
    skills_by_id = {s.id: s for s in db.query(Skill).all()}
    return [
        SkillScoreSnapshot(
            skill_id=r.skill_id,
            skill_name=skills_by_id[r.skill_id].name,
            display_label=(
                skills_by_id[r.skill_id].display_label
                or skills_by_id[r.skill_id].name
            ),
            score=float(r.display_score),
        )
        for r in rows
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
    """Return score history for ONE skill over the last `days` days."""
    rows = ProgressLogRepository(db).list_for_user_skill(
        user_id=current_user.id,
        skill_id=skill_id,
        days=days,
    )
    return [ProgressLogPoint.model_validate(r) for r in rows]


@router.get(
    "/stats",
    response_model=StatsDashboard,
    status_code=status.HTTP_200_OK,
)
def get_stats_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StatsDashboard:
    """Stats page data. Weekly snapshot aggregates from evaluations, and
    strengths/focus areas pull from the latest activity feedback row.
    """
    now = datetime.now(timezone.utc)
    current_week_start = _week_start(now)
    previous_week_start = current_week_start - timedelta(days=7)

    # ── Skill scores (gamification display score) ──
    skill_points_rows = SkillPointsRepository(db).get_all_for_user(current_user.id)
    skills_by_id: dict[int, Skill] = {s.id: s for s in db.query(Skill).all()}
    scores = [
        SkillScoreSnapshot(
            skill_id=r.skill_id,
            skill_name=skills_by_id[r.skill_id].name,
            display_label=(
                skills_by_id[r.skill_id].display_label
                or skills_by_id[r.skill_id].name
            ),
            score=float(r.display_score),
        )
        for r in skill_points_rows
    ]
    overall_score = (
        round(sum(s.score for s in scores) / len(scores), 1) if scores else 0.0
    )

    # ── Weekly evaluation averages → score_change ──
    def avg_eval_score(start: datetime, end: datetime) -> float | None:
        value = (
            db.query(func.avg(ActivityEvaluation.raw_score))
            .join(
                ActivityAttempt,
                ActivityAttempt.id == ActivityEvaluation.attempt_id,
            )
            .join(DailySession, DailySession.id == ActivityAttempt.session_id)
            .filter(
                DailySession.user_id == current_user.id,
                ActivityEvaluation.created_at >= start,
                ActivityEvaluation.created_at < end,
            )
            .scalar()
        )
        return float(value) if value is not None else None

    cur_avg = avg_eval_score(current_week_start, now)
    prev_avg = avg_eval_score(previous_week_start, current_week_start)
    score_change = (
        round(cur_avg - prev_avg, 1)
        if cur_avg is not None and prev_avg is not None
        else 0.0
    )

    # ── Activities completed this week ──
    tasks_completed = (
        db.query(func.count(ActivityAttempt.id))
        .join(DailySession, DailySession.id == ActivityAttempt.session_id)
        .filter(
            DailySession.user_id == current_user.id,
            ActivityAttempt.status == AttemptStatus.EVALUATED,
            ActivityAttempt.submitted_at >= current_week_start,
        )
        .scalar()
        or 0
    )

    best_skill = max(scores, key=lambda s: s.score, default=None)

    # ── Weekly points per skill (for the bar trend column) ──
    weekly_points_rows = (
        db.query(SkillPointsLog.skill_id, func.sum(SkillPointsLog.points_earned))
        .filter(
            SkillPointsLog.user_id == current_user.id,
            SkillPointsLog.created_at >= current_week_start,
        )
        .group_by(SkillPointsLog.skill_id)
        .all()
    )
    weekly_points_by_skill: dict[int, int] = {
        skill_id: int(pts) for skill_id, pts in weekly_points_rows
    }

    # ── Difficulty distribution from each evaluated attempt's CEFR week ──
    cefr_counts = (
        db.query(CurriculumWeek.cefr_level, func.count(ActivityAttempt.id))
        .join(CurriculumDay, CurriculumDay.week_id == CurriculumWeek.id)
        .join(DailySession, DailySession.day_id == CurriculumDay.day_id)
        .join(ActivityAttempt, ActivityAttempt.session_id == DailySession.id)
        .filter(
            DailySession.user_id == current_user.id,
            ActivityAttempt.status == AttemptStatus.EVALUATED,
        )
        .group_by(CurriculumWeek.cefr_level)
        .all()
    )
    beginner = intermediate = advanced = 0
    for cefr, count in cefr_counts:
        tier = _CEFR_TIERS.get(str(cefr or "").upper())
        if tier == "beginner":
            beginner += int(count)
        elif tier == "intermediate":
            intermediate += int(count)
        elif tier == "advanced":
            advanced += int(count)
    difficulty_distribution = DifficultyDistribution(
        beginner=beginner,
        intermediate=intermediate,
        advanced=advanced,
        total=beginner + intermediate + advanced,
    )

    # ── 7-day per-skill history (forward-fill from display_score) ──
    history_start = (now - timedelta(days=6)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    day_labels = [
        (history_start + timedelta(days=i)).strftime("%a") for i in range(7)
    ]
    day_dates: list[date] = [
        (history_start + timedelta(days=i)).date() for i in range(7)
    ]

    log_rows = (
        db.query(ProgressLog)
        .filter(
            ProgressLog.user_id == current_user.id,
            ProgressLog.created_at >= history_start,
        )
        .order_by(ProgressLog.skill_id, ProgressLog.created_at.asc())
        .all()
    )
    logs_by_skill_date: dict[int, dict[date, float]] = defaultdict(dict)
    for log in log_rows:
        logs_by_skill_date[log.skill_id][log.created_at.date()] = float(log.score)

    skill_id_to_display: dict[int, float] = {
        r.skill_id: float(r.display_score) for r in skill_points_rows
    }
    skill_history: list[SkillHistorySeries] = []
    for sp_row in skill_points_rows:
        sid = sp_row.skill_id
        daily_map = logs_by_skill_date.get(sid, {})
        series: list[float] = []
        last_val = skill_id_to_display.get(sid, 0.0)
        for d in day_dates:
            if d in daily_map:
                last_val = daily_map[d]
            series.append(round(last_val, 1))
        skill_history.append(
            SkillHistorySeries(
                skill_id=sid,
                skill_name=skills_by_id[sid].name,
                display_label=skills_by_id[sid].display_label
                or skills_by_id[sid].name,
                scores=series,
            )
        )

    # ── Recent activities (latest 5 evaluated attempts) ──
    recent_attempts = (
        db.query(ActivityAttempt)
        .join(DailySession, DailySession.id == ActivityAttempt.session_id)
        .filter(
            DailySession.user_id == current_user.id,
            ActivityAttempt.status == AttemptStatus.EVALUATED,
        )
        .options(
            selectinload(ActivityAttempt.evaluation),
            selectinload(ActivityAttempt.feedback),
        )
        .order_by(
            ActivityAttempt.submitted_at.desc().nullslast(),
            ActivityAttempt.created_at.desc(),
        )
        .limit(5)
        .all()
    )
    recent_activities = [_build_activity(att) for att in recent_attempts]

    # ── Strengths / focus areas from the latest feedback row ──
    latest_fb = recent_attempts[0].feedback if recent_attempts else None
    strengths = (
        list(latest_fb.did_well[:3])
        if latest_fb and latest_fb.did_well
        else None
    ) or _fallback_strengths(scores)

    focus_areas: list[str] = []
    if latest_fb and latest_fb.mistakes:
        for m in latest_fb.mistakes[:3]:
            if isinstance(m, dict) and m.get("issue"):
                focus_areas.append(str(m["issue"]))
    if not focus_areas:
        focus_areas = _fallback_focus_areas(scores)

    return StatsDashboard(
        weekly_snapshot=WeeklySnapshot(
            overall_score=overall_score,
            overall_score_change=score_change,
            tasks_completed=int(tasks_completed),
            weekly_task_goal=WEEKLY_TASK_GOAL,
            best_skill_name=best_skill.skill_name if best_skill else None,
            best_skill_display_label=best_skill.display_label if best_skill else None,
            best_skill_score=best_skill.score if best_skill else None,
        ),
        skill_scores=scores,
        weekly_points_by_skill=weekly_points_by_skill,
        difficulty_distribution=difficulty_distribution,
        skill_history_labels=day_labels,
        skill_history=skill_history,
        feedback=StatsFeedback(
            strengths=strengths[:3],
            focus_areas=focus_areas[:3],
        ),
        recent_activities=recent_activities,
    )


@router.get(
    "/activities",
    response_model=list[RecentActivity],
    status_code=status.HTTP_200_OK,
)
def get_all_activities(
    limit: int = Query(50, ge=1, le=200, description="Max rows to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[RecentActivity]:
    """Return all completed activities for the current user, newest first."""
    rows = (
        db.query(ActivityAttempt)
        .join(DailySession, DailySession.id == ActivityAttempt.session_id)
        .filter(
            DailySession.user_id == current_user.id,
            ActivityAttempt.status == AttemptStatus.EVALUATED,
        )
        .options(
            selectinload(ActivityAttempt.evaluation),
            selectinload(ActivityAttempt.feedback),
        )
        .order_by(
            ActivityAttempt.submitted_at.desc().nullslast(),
            ActivityAttempt.created_at.desc(),
        )
        .limit(limit)
        .offset(offset)
        .all()
    )
    return [_build_activity(att) for att in rows]


@router.get(
    "/skill-points",
    response_model=list[SkillPointsRead],
    status_code=status.HTTP_200_OK,
)
def get_skill_points(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SkillPointsRead]:
    """Return points-based progress for every skill."""
    rows = (
        db.query(SkillPoints)
        .filter(SkillPoints.user_id == current_user.id)
        .all()
    )
    return [SkillPointsRead.model_validate(r) for r in rows]


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
    """Return recent points gains, newest first."""
    repo = SkillPointsLogRepository(db)
    rows = repo.list_for_user(
        user_id=current_user.id,
        skill_id=skill_id,
        limit=limit,
    )
    return [SkillPointsLogRead.model_validate(r) for r in rows]
