"""SessionService — orchestrates the start / next / submit / complete lifecycle.

Public methods:
  - `start_session(...)`     — POST /sessions/start
  - `next_activity(...)`     — GET  /sessions/{id}/next-activity
  - `submit_activity(...)`   — POST /sessions/{id}/activities/{seq}/submit
  - `complete_session(...)`  — POST /sessions/{id}/complete
  - `get_scorecard(...)`     — GET  /sessions/{id}/scorecard

The service does its own commits at logical boundaries (one per public call).
Evaluator and FeedbackGenerator are injected — Phase 4 swaps in LLM-driven
implementations without touching this file.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.curriculum.v2_models import CurriculumDay
from app.modules.curriculum.v2_repository import (
    CurriculumDayRepository,
    TaskArchetypeRepository,
)
from app.modules.progress.repository import SkillPointsRepository
from app.modules.sessions.evaluator import Evaluator, EvaluationResult, StubEvaluator
from app.modules.sessions.exceptions import (
    AttemptAlreadySubmitted,
    AttemptNotFound,
    DayNotFound,
    NoActivitiesPlanned,
    SessionAbandoned,
    SessionAlreadyCompleted,
    SessionAlreadyOpen,
    SessionNotFound,
)
from app.modules.sessions.feedback_generator import (
    FeedbackGenerator,
    FeedbackResult,
    StubFeedbackGenerator,
)
from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityEvaluation,
    ActivityFeedback,
    AttemptStatus,
    DailySession,
    SessionScorecard,
    SessionStatus,
)
from app.modules.sessions.planner import PlannedActivity, plan_session
from app.modules.sessions.repository import (
    ActivityAttemptRepository,
    DailySessionRepository,
    EvaluationRepository,
    FeedbackRepository,
    ScorecardRepository,
)
from app.modules.sessions.scoring_writer import ApplyReport, apply_session_scorecard
from app.modules.sessions.task_generator import (
    StubTaskGenerator,
    TaskGenerator,
)
from app.modules.skills.repository import SkillRepository
from app.scoring import (
    ActivityScore,
    ArchetypeSpec,
    CourseLength,
    SUB_SKILLS,
    base_reward,
    build_session_aggregation,
    distribute,
    get_archetype,
)


logger = logging.getLogger(__name__)


class SessionService:
    """Orchestrator for the new sessions lifecycle."""

    def __init__(
        self,
        db: Session,
        *,
        evaluator: Evaluator | None = None,
        feedback_generator: FeedbackGenerator | None = None,
        task_generator: TaskGenerator | None = None,
    ) -> None:
        self.db = db
        # The three injectable agents default to stubs. Production wiring
        # (FastAPI dep / route factory) replaces these with the LLM-driven
        # implementations from `app.ai.sessions`.
        self.evaluator: Evaluator = evaluator or StubEvaluator()
        self.feedback_generator: FeedbackGenerator = (
            feedback_generator or StubFeedbackGenerator()
        )
        self.task_generator: TaskGenerator = task_generator or StubTaskGenerator()

        self.sessions_repo = DailySessionRepository(db)
        self.attempts_repo = ActivityAttemptRepository(db)
        self.evaluations_repo = EvaluationRepository(db)
        self.feedback_repo = FeedbackRepository(db)
        self.scorecards_repo = ScorecardRepository(db)
        self.days_repo = CurriculumDayRepository(db)
        self.archetypes_repo = TaskArchetypeRepository(db)
        self.skills_repo = SkillRepository(db)
        self.points_repo = SkillPointsRepository(db)

    # ── start ──────────────────────────────────────────────────────

    async def start_session(
        self,
        *,
        user_id: int,
        day_id: str,
        course_length: CourseLength,
        tasks_per_day: int,
        allowed_activities: set[str],
        sub_level: int | None = None,
        user_interests: list[str] | None = None,
        now: datetime | None = None,
    ) -> DailySession:
        """Create a new session for `(user_id, day_id)`. Raises if one is open."""
        now = now or datetime.now(timezone.utc)

        day = self.days_repo.get_by_day_id(day_id)
        if day is None:
            raise DayNotFound(f"day_id={day_id!r} not found in curriculum_days")

        if self.sessions_repo.get_in_progress(user_id=user_id, day_id=day_id) is not None:
            raise SessionAlreadyOpen(
                f"user {user_id} already has an in-progress session for day {day_id!r}"
            )

        plan = plan_session(
            day,
            tasks_per_day=tasks_per_day,
            allowed_activities=allowed_activities,
        )
        if not plan:
            # `plan_session` already raises NoActivitiesPlanned in this case;
            # belt-and-suspenders for clarity.
            raise NoActivitiesPlanned(f"empty plan for day {day_id!r}")

        is_first = not self.sessions_repo.has_completed_for_day(
            user_id=user_id, day_id=day_id
        )

        session = DailySession(
            session_id=str(uuid4()),
            user_id=user_id,
            day_id=day.day_id,
            course_length=course_length.value,
            status=SessionStatus.IN_PROGRESS,
            is_first_attempt=is_first,
            started_at=now,
        )
        self.sessions_repo.add(session)

        # Look up the parent week so the task generator can pick a content
        # depth that matches the user's CEFR + sub_level. Falls back to the
        # week's sub_level_min if no explicit sub_level is provided.
        week = session.day_id  # placeholder; replaced below from day.week_id
        parent_week = day.week  # loaded via relationship
        effective_sub_level = sub_level or parent_week.sub_level_min

        for activity in plan:
            await self._materialise_attempt(
                session=session,
                day=day,
                plan=activity,
                cefr_level=parent_week.cefr_level,
                sub_level=effective_sub_level,
                user_interests=user_interests,
            )

        self.db.commit()
        self.db.refresh(session)
        return session

    # ── next ───────────────────────────────────────────────────────

    def next_activity(self, *, session_id: str, user_id: int) -> ActivityAttempt:
        """Return the next pending attempt + its task_content.

        Raises:
          SessionNotFound       — unknown session_id, or owned by another user
          SessionAlreadyCompleted — all attempts done; caller should call complete
          SessionAbandoned       — session was abandoned
        """
        session = self._load_owned(session_id=session_id, user_id=user_id)
        self._guard_open(session)

        next_attempt = self.attempts_repo.first_pending(session.id)
        if next_attempt is None:
            raise SessionAlreadyCompleted(
                f"session {session_id!r}: no pending attempts; call complete instead"
            )
        return next_attempt

    # ── submit ─────────────────────────────────────────────────────

    async def submit_activity(
        self,
        *,
        session_id: str,
        user_id: int,
        sequence: int,
        user_response: dict | None,
        now: datetime | None = None,
    ) -> tuple[ActivityAttempt, ActivityEvaluation, ActivityFeedback]:
        """Persist response, run evaluator + feedback generator, store results."""
        now = now or datetime.now(timezone.utc)
        session = self._load_owned(session_id=session_id, user_id=user_id)
        self._guard_open(session)

        attempt = self.attempts_repo.get(session_pk=session.id, sequence=sequence)
        if attempt is None:
            raise AttemptNotFound(
                f"session {session_id!r}: no attempt at sequence {sequence}"
            )
        if attempt.status is AttemptStatus.EVALUATED:
            raise AttemptAlreadySubmitted(
                f"session {session_id!r} seq {sequence}: already evaluated"
            )

        spec = get_archetype(attempt.archetype_id)

        # Persist the user's response and flip to SUBMITTED.
        attempt.user_response = user_response
        attempt.submitted_at = now
        attempt.status = AttemptStatus.SUBMITTED

        # Run the evaluator.
        eval_result: EvaluationResult = await self.evaluator.evaluate(
            archetype=spec,
            task_content=attempt.task_content,
            user_response=user_response,
        )
        course_length = CourseLength(session.course_length)
        reward = base_reward(eval_result.raw_score, course_length)
        weighted = distribute(reward, dict(spec.weight_map))

        evaluation = ActivityEvaluation(
            attempt_id=attempt.id,
            raw_score=eval_result.raw_score,
            rubric_scores=dict(eval_result.rubric_scores),
            base_reward=reward,
            weighted_points=weighted,
            evaluator_notes=eval_result.evaluator_notes,
        )
        self.evaluations_repo.add(evaluation)

        # Run the feedback generator.
        fb: FeedbackResult = await self.feedback_generator.generate(
            archetype=spec,
            evaluation=eval_result,
            user_response=user_response,
        )
        feedback = ActivityFeedback(
            attempt_id=attempt.id,
            score=fb.score,
            summary=fb.summary,
            did_well=list(fb.did_well),
            mistakes=[
                {
                    "issue": m.issue,
                    "user_wrote": m.user_wrote,
                    "correction": m.correction,
                    "rule": m.rule,
                    "sub_skills_affected": list(m.sub_skills_affected),
                }
                for m in fb.mistakes
            ],
            next_tip=fb.next_tip,
            sub_skill_breakdown=dict(fb.sub_skill_breakdown),
        )
        self.feedback_repo.add(feedback)

        attempt.status = AttemptStatus.EVALUATED
        self.db.commit()
        self.db.refresh(attempt)
        self.db.refresh(evaluation)
        self.db.refresh(feedback)
        return attempt, evaluation, feedback

    # ── complete ───────────────────────────────────────────────────

    async def complete_session(
        self,
        *,
        session_id: str,
        user_id: int,
        now: datetime | None = None,
    ) -> tuple[SessionScorecard, ApplyReport]:
        """Aggregate evaluations, persist scorecard, apply points (if first attempt).

        Idempotent: calling `complete` twice returns the existing scorecard
        with an `ApplyReport(applied=False, reason='already complete')`.
        """
        now = now or datetime.now(timezone.utc)
        session = self._load_owned(session_id=session_id, user_id=user_id)

        if session.status is SessionStatus.ABANDONED:
            raise SessionAbandoned(f"session {session_id!r} was abandoned")

        if session.status is SessionStatus.COMPLETED:
            # Idempotent: hand back what's already stored.
            existing = self.scorecards_repo.get_for_session(session.id)
            if existing is None:
                raise RuntimeError(
                    f"session {session_id!r} is COMPLETED but has no scorecard"
                )
            return existing, ApplyReport(
                applied=False, rows_written=0, rows_skipped=0,
                reason="session already completed",
            )

        # Build ActivityScore list from every EVALUATED attempt.
        attempts = self.attempts_repo.list_for_session(session.id)
        scored: list[ActivityScore] = []
        for attempt in attempts:
            if attempt.status is not AttemptStatus.EVALUATED:
                continue
            if attempt.evaluation is None:
                continue
            spec = get_archetype(attempt.archetype_id)
            scored.append(ActivityScore(
                archetype_id=attempt.archetype_id,
                raw_score=float(attempt.evaluation.raw_score),
                weight_map=dict(spec.weight_map),
            ))

        current_totals = self._current_points_for(session.user_id)
        course_length = CourseLength(session.course_length)
        aggregation = build_session_aggregation(
            scored,
            course_length,
            current_totals=current_totals,
        )

        scorecard = SessionScorecard(
            session_id=session.id,
            points_earned=dict(aggregation.points_earned),
            subskill_totals_after=dict(aggregation.subskill_totals_after or {}),
            dashboard_after=dict(aggregation.dashboard_after or {}),
            completed_at=now,
            points_applied=False,
        )
        self.scorecards_repo.add(scorecard)

        # Flush so apply_session_scorecard sees committed scorecard + session state.
        report = apply_session_scorecard(self.db, session=session, scorecard=scorecard)
        scorecard.points_applied = report.applied

        session.status = SessionStatus.COMPLETED
        session.completed_at = now

        self.db.commit()
        self.db.refresh(scorecard)
        return scorecard, report

    # ── read ───────────────────────────────────────────────────────

    def get_scorecard(self, *, session_id: str, user_id: int) -> SessionScorecard | None:
        session = self._load_owned(session_id=session_id, user_id=user_id)
        return self.scorecards_repo.get_for_session(session.id)

    def get_session(self, *, session_id: str, user_id: int) -> DailySession:
        return self._load_owned(session_id=session_id, user_id=user_id)

    # ── helpers ────────────────────────────────────────────────────

    def _load_owned(self, *, session_id: str, user_id: int) -> DailySession:
        session = self.sessions_repo.get_by_session_id(session_id)
        if session is None or session.user_id != user_id:
            raise SessionNotFound(f"session {session_id!r} not found")
        return session

    @staticmethod
    def _guard_open(session: DailySession) -> None:
        if session.status is SessionStatus.COMPLETED:
            raise SessionAlreadyCompleted(
                f"session {session.session_id!r} already completed"
            )
        if session.status is SessionStatus.ABANDONED:
            raise SessionAbandoned(f"session {session.session_id!r} was abandoned")

    async def _materialise_attempt(
        self,
        *,
        session: DailySession,
        day: CurriculumDay,
        plan: PlannedActivity,
        cefr_level: str,
        sub_level: int,
        user_interests: list[str] | None,
    ) -> ActivityAttempt:
        spec = get_archetype(plan.archetype_id)
        generated = await self.task_generator.generate(
            archetype=spec,
            day_topic=day.topic,
            explanation_brief=day.explanation_brief,
            cefr_level=cefr_level,
            sub_level=sub_level,
            user_interests=user_interests,
        )
        attempt = ActivityAttempt(
            session_id=session.id,
            archetype_id=plan.archetype_id,
            sequence=plan.sequence,
            is_mandatory=plan.is_mandatory,
            status=AttemptStatus.PENDING,
            task_content=generated.content,
        )
        self.db.add(attempt)
        self.db.flush()
        return attempt

    def _current_points_for(self, user_id: int) -> dict[str, int]:
        """Build `{sub_skill: int_points}` for the user, filling missing skills with 0."""
        id_to_name = {v: k for k, v in self.skills_repo.name_to_id_map().items()}
        out: dict[str, int] = {skill: 0 for skill in SUB_SKILLS}
        for row in self.points_repo.get_all_for_user(user_id):
            name = id_to_name.get(row.skill_id)
            if name in out:
                out[name] = int(row.points)
        return out
