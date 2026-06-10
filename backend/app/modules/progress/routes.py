"""HTTP endpoints for the progress module.

Reads from the daily-sessions flow: ActivityAttempt / ActivityEvaluation /
ActivityFeedback / SessionScorecard (plus the SkillPoints gamification
layer and ProgressLog history).
"""

from collections import defaultdict

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user, require_learner
from app.modules.auth.models import User
from app.modules.curriculum.models import CurriculumDay, CurriculumWeek
from app.modules.feedback_memory.rag_service import FeedbackRAGService
from app.modules.preferences.service import PreferenceService
from app.modules.progress import stats_insights
from app.modules.progress.curriculum_periods import (
    StatsRange,
    build_period,
    day_of_day_id,
)
from app.modules.progress.models import SkillPoints, SkillPointsLog
from app.modules.progress.repository import (
    ProgressLogRepository,
    SkillPointsLogRepository,
    SkillPointsRepository,
)
from app.modules.progress.schemas import (
    CurriculumMilestone,
    DifficultyDistribution,
    PeriodSnapshot,
    PracticePatterns,
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


router = APIRouter(
    prefix="/progress",
    tags=["progress"],
    dependencies=[Depends(require_learner)],
)

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


def _avg_eval_score(
    db: Session, user_id: int, day_ids: list[str]
) -> float | None:
    """Average raw evaluation score across the given curriculum days."""
    if not day_ids:
        return None
    value = (
        db.query(func.avg(ActivityEvaluation.raw_score))
        .join(ActivityAttempt, ActivityAttempt.id == ActivityEvaluation.attempt_id)
        .join(DailySession, DailySession.id == ActivityAttempt.session_id)
        .filter(
            DailySession.user_id == user_id,
            DailySession.day_id.in_(day_ids),
        )
        .scalar()
    )
    return float(value) if value is not None else None


def _count_completed(db: Session, user_id: int, day_ids: list[str]) -> int:
    """Count EVALUATED activity attempts inside the given curriculum days."""
    if not day_ids:
        return 0
    return int(
        db.query(func.count(ActivityAttempt.id))
        .join(DailySession, DailySession.id == ActivityAttempt.session_id)
        .filter(
            DailySession.user_id == user_id,
            ActivityAttempt.status == AttemptStatus.EVALUATED,
            DailySession.day_id.in_(day_ids),
        )
        .scalar()
        or 0
    )


def _completed_sessions(
    db: Session, user_id: int, day_ids: list[str]
) -> list[DailySession]:
    """Completed daily sessions whose day_id falls in the given period."""
    if not day_ids:
        return []
    return (
        db.query(DailySession)
        .filter(
            DailySession.user_id == user_id,
            DailySession.day_id.in_(day_ids),
            DailySession.completed_at.isnot(None),
        )
        .all()
    )


def _session_seconds(sessions: list[DailySession]) -> int:
    """Total practice seconds across completed sessions (negatives ignored)."""
    total = 0.0
    for s in sessions:
        if s.completed_at is not None and s.started_at is not None:
            delta = (s.completed_at - s.started_at).total_seconds()
            if delta > 0:
                total += delta
    return int(total)


@router.get(
    "/stats",
    response_model=StatsDashboard,
    status_code=status.HTTP_200_OK,
)
def get_stats_dashboard(
    range_: StatsRange = Query(
        "week", alias="range", description="week | month | all"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StatsDashboard:
    """Stats page data, anchored to the learner's *curriculum* calendar.

    Range-dependent sections (period KPIs, score history, practice patterns,
    recent activities) reflect ``range``. The sub-skill overview and the
    difficulty donut are always all-time. Strengths / focus areas are
    qualitative, number-free coaching copy synthesized from the learner's
    recurring feedback patterns (RAG-backed).
    """
    user_id = current_user.id

    # ── Curriculum position → period window ──
    pref = PreferenceService(db).get(user_id)
    period = build_period(
        range_,
        course_length=pref.course_length,
        tasks_per_day=pref.tasks_per_day,
        current_week=pref.current_week,
        current_day=pref.current_day_in_week,
    )

    # ── Skill scores (gamification display score) — ALWAYS all-time ──
    skill_points_rows = SkillPointsRepository(db).get_all_for_user(user_id)
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
    all_time_overall = (
        round(sum(s.score for s in scores) / len(scores), 1) if scores else 0.0
    )

    # ── Period KPIs (overall score = avg eval in period) ──
    period_avg = _avg_eval_score(db, user_id, period.day_ids)
    overall_score = round(period_avg, 1) if period_avg is not None else 0.0
    prev_avg = _avg_eval_score(db, user_id, period.comparison_day_ids or [])
    score_change = (
        round(period_avg - prev_avg, 1)
        if period_avg is not None and prev_avg is not None
        else 0.0
    )

    tasks_completed = _count_completed(db, user_id, period.day_ids)
    tasks_goal = period.expected_tasks
    completion_pct = (
        round(100.0 * tasks_completed / tasks_goal, 1) if tasks_goal else 0.0
    )

    period_sessions = _completed_sessions(db, user_id, period.day_ids)
    time_practiced = _session_seconds(period_sessions)
    time_change: int | None = None
    if period.comparison_day_ids:
        prev_sessions = _completed_sessions(db, user_id, period.comparison_day_ids)
        time_change = time_practiced - _session_seconds(prev_sessions)

    # ── Points earned per skill in the period (best-skill + trend column) ──
    period_points_rows = (
        (
            db.query(
                SkillPointsLog.skill_id,
                func.sum(SkillPointsLog.points_earned),
            )
            .join(DailySession, DailySession.id == SkillPointsLog.session_id)
            .filter(
                SkillPointsLog.user_id == user_id,
                DailySession.day_id.in_(period.day_ids),
            )
            .group_by(SkillPointsLog.skill_id)
            .all()
        )
        if period.day_ids
        else []
    )
    period_points_by_skill: dict[int, int] = {
        skill_id: int(pts) for skill_id, pts in period_points_rows
    }

    # Best skill: most points earned this period, else the all-time leader.
    best_skill_id: int | None = (
        max(period_points_by_skill, key=lambda k: period_points_by_skill[k])
        if period_points_by_skill
        else None
    )
    best_skill = next(
        (s for s in scores if s.skill_id == best_skill_id), None
    ) or max(scores, key=lambda s: s.score, default=None)

    # ── Difficulty distribution — ALWAYS all-time ──
    cefr_counts = (
        db.query(CurriculumWeek.cefr_level, func.count(ActivityAttempt.id))
        .join(CurriculumDay, CurriculumDay.week_id == CurriculumWeek.id)
        .join(DailySession, DailySession.day_id == CurriculumDay.day_id)
        .join(ActivityAttempt, ActivityAttempt.session_id == DailySession.id)
        .filter(
            DailySession.user_id == user_id,
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

    # ── Per-skill score history, bucketed by the curriculum period ──
    # SkillPointsLog is the only per-skill signal tied to a session/day_id, so
    # reconstruct each skill's trajectory from it: anchor at the current
    # display points and subtract the deltas earned AFTER each bucket's closing
    # boundary. day_ids sort in curriculum order, so the lexicographic max of a
    # bucket is its boundary and `did > boundary` selects everything later.
    plog_rows = (
        db.query(
            SkillPointsLog.skill_id,
            SkillPointsLog.points_earned,
            DailySession.day_id,
        )
        .join(DailySession, DailySession.id == SkillPointsLog.session_id)
        .filter(SkillPointsLog.user_id == user_id)
        .all()
    )
    deltas_by_skill: dict[int, list[tuple[str, int]]] = defaultdict(list)
    for skill_id, pts, day_id in plog_rows:
        deltas_by_skill[skill_id].append((day_id, int(pts)))
    current_points_by_skill: dict[int, int] = {
        r.skill_id: int(r.points) for r in skill_points_rows
    }
    boundaries = [max(bucket) for bucket in period.bucket_day_ids]

    skill_history: list[SkillHistorySeries] = []
    for sp_row in skill_points_rows:
        sid = sp_row.skill_id
        current_points = current_points_by_skill.get(sid, 0)
        skill_deltas = deltas_by_skill.get(sid, [])
        series: list[float] = []
        for boundary in boundaries:
            after = sum(d for (did, d) in skill_deltas if did > boundary)
            score_at = (current_points - after) / 1000.0
            series.append(round(max(0.0, min(10.0, score_at)), 1))
        skill_history.append(
            SkillHistorySeries(
                skill_id=sid,
                skill_name=skills_by_id[sid].name,
                display_label=skills_by_id[sid].display_label
                or skills_by_id[sid].name,
                scores=series,
            )
        )

    # ── Recent activities — filtered to the period ──
    recent_attempts = (
        (
            db.query(ActivityAttempt)
            .join(DailySession, DailySession.id == ActivityAttempt.session_id)
            .filter(
                DailySession.user_id == user_id,
                ActivityAttempt.status == AttemptStatus.EVALUATED,
                DailySession.day_id.in_(period.day_ids),
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
        if period.day_ids
        else []
    )
    recent_activities = [_build_activity(att) for att in recent_attempts]

    # ── Practice patterns — over the period ──
    pattern_rows = (
        (
            db.query(DailySession.day_id, ActivityEvaluation.raw_score)
            .join(ActivityAttempt, ActivityAttempt.session_id == DailySession.id)
            .outerjoin(
                ActivityEvaluation,
                ActivityEvaluation.attempt_id == ActivityAttempt.id,
            )
            .filter(
                DailySession.user_id == user_id,
                ActivityAttempt.status == AttemptStatus.EVALUATED,
                DailySession.day_id.in_(period.day_ids),
            )
            .all()
        )
        if period.day_ids
        else []
    )
    count_by_dow: dict[int, int] = defaultdict(int)
    score_sum_by_dow: dict[int, float] = defaultdict(float)
    score_n_by_dow: dict[int, int] = defaultdict(int)
    for day_id, raw in pattern_rows:
        dow = day_of_day_id(day_id)
        if dow is None:
            continue
        count_by_dow[dow] += 1
        if raw is not None:
            score_sum_by_dow[dow] += float(raw)
            score_n_by_dow[dow] += 1
    most_active_dow = (
        max(count_by_dow, key=lambda d: count_by_dow[d]) if count_by_dow else None
    )
    best_dow = (
        max(
            score_n_by_dow,
            key=lambda d: score_sum_by_dow[d] / score_n_by_dow[d],
        )
        if score_n_by_dow
        else None
    )
    avg_session_seconds = (
        int(time_practiced / len(period_sessions)) if period_sessions else None
    )
    pattern_subtitle = {
        "week": "This curriculum week",
        "month": "This curriculum month (4 weeks)",
        "all": "All time",
    }[range_]
    practice_patterns = PracticePatterns(
        most_active_day=f"Day {most_active_dow}" if most_active_dow else None,
        best_day=f"Day {best_dow}" if best_dow else None,
        avg_session_seconds=avg_session_seconds,
        sessions_count=len(period_sessions),
        subtitle=pattern_subtitle,
    )

    # ── Strengths / focus — RAG-backed recurring themes, number-free copy ──
    themes = FeedbackRAGService(db).compute_stats_themes(user_id)
    strengths, focus_areas = stats_insights.build_insights(themes)

    period_snapshot = PeriodSnapshot(
        range=range_,
        overall_score=overall_score,
        overall_score_change=score_change,
        tasks_completed=tasks_completed,
        tasks_goal=tasks_goal,
        completion_pct=completion_pct,
        time_practiced_seconds=time_practiced,
        time_practiced_change_seconds=time_change,
        best_skill_name=best_skill.skill_name if best_skill else None,
        best_skill_display_label=best_skill.display_label if best_skill else None,
        best_skill_score=best_skill.score if best_skill else None,
        curriculum_week=period.current_week,
        curriculum_day=period.current_day,
        weeks_completed=period.weeks_completed,
    )

    total_weeks = 48 if pref.course_length == "48w" else 24
    curriculum_milestone = CurriculumMilestone(
        current_week=period.current_week,
        current_day=period.current_day,
        total_weeks=total_weeks,
        course_length=pref.course_length,
        overall_score=all_time_overall,
    )

    return StatsDashboard(
        range=range_,
        period_snapshot=period_snapshot,
        curriculum_milestone=curriculum_milestone,
        practice_patterns=practice_patterns,
        weekly_snapshot=WeeklySnapshot(
            overall_score=overall_score,
            overall_score_change=score_change,
            tasks_completed=tasks_completed,
            weekly_task_goal=tasks_goal,
            best_skill_name=best_skill.skill_name if best_skill else None,
            best_skill_display_label=best_skill.display_label if best_skill else None,
            best_skill_score=best_skill.score if best_skill else None,
        ),
        skill_scores=scores,
        weekly_points_by_skill=period_points_by_skill,
        difficulty_distribution=difficulty_distribution,
        skill_history_labels=period.bucket_labels,
        skill_history=skill_history,
        feedback=StatsFeedback(
            strengths=strengths,
            focus_areas=focus_areas,
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
