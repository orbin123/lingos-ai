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

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.curriculum.file_source import (
    get_day_by_id as file_get_day_by_id,
    resolve_archetypes as file_resolve_archetypes,
    task_spec_for as file_task_spec_for,
)
from app.modules.curriculum.repository import (
    CurriculumDayRepository,
    CurriculumWeekRepository,
    TaskArchetypeRepository,
)
from app.modules.preferences.repository import UserCoursePreferenceRepository
from app.modules.progress.repository import SkillPointsRepository
from app.modules.sessions.evaluator import Evaluator, EvaluationResult, StubEvaluator
from app.modules.sessions.exceptions import (
    AttemptAlreadySubmitted,
    AttemptNotFound,
    DayNotFound,
    NoActivitiesPlanned,
    SessionAdvanceBlocked,
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
from app.modules.sessions.planner import plan_session
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
    is_valid_listening_payload,
    is_valid_open_text_payload,
    is_valid_speak_and_record_payload,
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
    tier_for_score,
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
        self.weeks_repo = CurriculumWeekRepository(db)
        self.archetypes_repo = TaskArchetypeRepository(db)
        self.skills_repo = SkillRepository(db)
        self.points_repo = SkillPointsRepository(db)
        self.preferences_repo = UserCoursePreferenceRepository(db)

        # RAG memory service — optional. When absent (tests, early phases),
        # activity memory storage and mentor note generation are skipped.
        self._rag_service: Any | None = None
        self._mentor_generator: Any | None = None

    # ── start ──────────────────────────────────────────────────────

    async def start_session(
        self,
        *,
        user_id: int,
        day_id: str | None = None,
        course_length: CourseLength,
        tasks_per_day: int,
        allowed_activities: set[str],
        sub_level: int | None = None,
        user_interests: list[str] | None = None,
        now: datetime | None = None,
        week_number: int | None = None,
        day_index: int | None = None,
    ) -> DailySession:
        """Create a new session for `(user_id, day_id)`. Raises if one is open.

        If the day is file-authored in ``source_24w.py``, the archetype order
        and task specs come from the file instead of the planner.
        """
        now = now or datetime.now(timezone.utc)

        if day_id is None:
            raise DayNotFound("day_id is required")

        day = self.days_repo.get_by_day_id(day_id)
        if day is None:
            raise DayNotFound(f"day_id={day_id!r} not found in curriculum_days")

        if self.sessions_repo.get_in_progress(user_id=user_id, day_id=day_id) is not None:
            raise SessionAlreadyOpen(
                f"user {user_id} already has an in-progress session for day {day_id!r}"
            )

        file_day_override = None
        try:
            file_day_override = file_get_day_by_id(day.day_id)
        except DayNotFound:
            file_day_override = None

        source_plan: list[tuple[int, ArchetypeSpec, dict]] | None = None
        if file_day_override is not None:
            source_plan = []
            for i, spec in enumerate(file_resolve_archetypes(file_day_override)):
                if spec.core_activity not in allowed_activities:
                    continue
                source_plan.append((i, spec, file_task_spec_for(file_day_override, i)))
            if not source_plan:
                raise NoActivitiesPlanned(
                    f"source day {day.day_id!r}: no archetypes match "
                    f"allowed activities {sorted(allowed_activities)}"
                )
        else:
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
        parent_week = day.week  # loaded via relationship
        if parent_week is None:
            raise DayNotFound(f"day_id={day_id!r} has no parent curriculum week")

        if file_day_override is not None and source_plan is not None:
            effective_sub_level = sub_level or file_day_override.sub_level_min
            for sequence, (_orig_index, spec, task_spec) in enumerate(
                source_plan, start=1,
            ):
                await self._materialise_attempt(
                    session=session,
                    day_topic=file_day_override.topic,
                    explanation_brief=file_day_override.explanation_brief,
                    archetype_id=spec.archetype_id,
                    sequence=sequence,
                    is_mandatory=True,
                    cefr_level=file_day_override.cefr_level,
                    sub_level=effective_sub_level,
                    user_interests=user_interests,
                    task_spec=task_spec or None,
                )
        else:
            effective_sub_level = sub_level or parent_week.sub_level_min
            for activity in plan:
                await self._materialise_attempt(
                    session=session,
                    day_topic=day.topic,
                    explanation_brief=day.explanation_brief,
                    archetype_id=activity.archetype_id,
                    sequence=activity.sequence,
                    is_mandatory=activity.is_mandatory,
                    cefr_level=parent_week.cefr_level,
                    sub_level=effective_sub_level,
                    user_interests=user_interests,
                    task_spec=None,
                )

        self.db.commit()
        self.db.refresh(session)
        return session

    # ── next ───────────────────────────────────────────────────────

    def next_activity(self, *, session_id: str, user_id: int) -> ActivityAttempt:
        """Return the next pending attempt + its task_content.

        Synchronous fetch only. Callers that ship the payload to the UI MUST
        also await `prepare_attempt_for_delivery(...)` to self-heal any
        attempt that was persisted with incomplete content by an older code
        path (e.g. listening attempts missing audio_script / items).

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

    async def prepare_attempt_for_delivery(
        self, attempt: ActivityAttempt
    ) -> ActivityAttempt:
        """Heal `task_content` if it's broken for its archetype, then return.

        Keeps the UI from seeing the "Audio could not be prepared" dead-end
        on listening attempts whose content was persisted by an older
        StubTaskGenerator that didn't populate `audio_script` / `items` /
        `inner_widget`. Mutates the row in-place + commits when it
        regenerates so the eventual evaluator sees the same content the
        widget rendered.

        No-op when the existing content is already valid for its archetype.
        """
        spec = get_archetype(attempt.archetype_id)
        content = dict(attempt.task_content or {})
        if self._is_attempt_content_valid(content, spec):
            return attempt

        logger.warning(
            "session attempt id=%s archetype=%s has invalid task_content "
            "(phase=%s); regenerating via %s",
            attempt.id,
            attempt.archetype_id,
            content.get("phase"),
            type(self.task_generator).__name__,
        )
        repaired = await self._regenerate_task_content(
            attempt=attempt, archetype=spec, prior=content,
        )
        attempt.task_content = repaired
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    @staticmethod
    def _is_attempt_content_valid(content: dict, spec: ArchetypeSpec) -> bool:
        if not content:
            return False
        if spec.core_activity == "listen":
            if not is_valid_listening_payload(content):
                return False
            audio_script = str(content.get("audio_script") or "").strip()
            audio_url = str(content.get("audio_url") or "").strip()
            return bool(audio_url or audio_script)
        if spec.archetype_id == "WRITE_OPEN_SENT":
            return is_valid_open_text_payload(content, expected_items=3)
        if spec.archetype_id == "SPEAK_TIMED" or spec.ui_widget == "SpeakAndRecord":
            return is_valid_speak_and_record_payload(content)
        return True

    async def _regenerate_task_content(
        self,
        *,
        attempt: ActivityAttempt,
        archetype: ArchetypeSpec,
        prior: dict,
    ) -> dict:
        """Best-effort regeneration that reuses any context already on the row."""
        source_context = self._file_repair_context_for_attempt(attempt, archetype)
        day_topic = (
            (source_context[0].topic if source_context else "")
            or str(prior.get("topic") or "").strip()
            or str(prior.get("topic_name") or "").strip()
            or archetype.name
        )
        explanation_brief = (
            (source_context[0].explanation_brief if source_context else "")
            or str(prior.get("explanation_brief") or "").strip()
        )
        cefr_level = (
            (source_context[0].cefr_level if source_context else "")
            or str(prior.get("cefr_level") or "A1").strip()
            or "A1"
        )
        try:
            sub_level = int(
                source_context[0].sub_level_min
                if source_context
                else prior.get("sub_level") or 1
            )
        except (TypeError, ValueError):
            sub_level = 1

        task_spec: dict = (
            dict(source_context[1])
            if source_context and source_context[1]
            else {"topic_override": day_topic}
        )
        task_spec.setdefault("topic_override", day_topic)
        instructions = str(prior.get("instructions") or "").strip()
        if instructions and "instructions_override" not in task_spec:
            task_spec["instructions_override"] = instructions
        if prior.get("task_intro") and "task_intro" not in task_spec:
            task_spec["task_intro"] = prior["task_intro"]
        if (
            prior.get("estimated_time_minutes")
            and "estimated_time_minutes" not in task_spec
        ):
            task_spec["estimated_time_minutes"] = prior["estimated_time_minutes"]

        generated = await self.task_generator.generate(
            archetype=archetype,
            day_topic=day_topic,
            explanation_brief=explanation_brief,
            cefr_level=cefr_level,
            sub_level=sub_level,
            user_interests=None,
            task_spec=task_spec,
        )
        return generated.content

    @staticmethod
    def _file_repair_context_for_attempt(
        attempt: ActivityAttempt, archetype: ArchetypeSpec,
    ) -> tuple[Any, dict] | None:
        """Return file-authored day/spec context for stale persisted attempts."""
        try:
            day = file_get_day_by_id(attempt.session.day_id)
        except DayNotFound:
            return None

        matching_indexes = [
            index
            for index, archetype_id in enumerate(day.task_archetypes_used)
            if archetype_id == archetype.archetype_id
        ]
        if len(matching_indexes) == 1:
            spec_index = matching_indexes[0]
        else:
            spec_index = attempt.sequence - 1

        task_spec = file_task_spec_for(day, spec_index)
        return day, task_spec

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

        # Lookup file-authored overrides for evaluator and feedback.
        file_overrides = self._file_overrides_for_day(session.day_id)

        # Run the evaluator.
        eval_result: EvaluationResult = await self.evaluator.evaluate(
            archetype=spec,
            task_content=attempt.task_content,
            user_response=user_response,
            evaluator_overrides=file_overrides.get("evaluator") or None,
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
            task_content=attempt.task_content,
            feedback_overrides=file_overrides.get("feedback") or None,
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

        # Fire-and-forget: store activity feedback in RAG memory.
        # Failures are logged, never block the user.
        if self._rag_service is not None:
            asyncio.create_task(
                self._store_activity_memory_safe(
                    user_id=session.user_id,
                    session_id=session.id,
                    attempt_id=attempt.id,
                    archetype_id=attempt.archetype_id,
                    day_id=session.day_id,
                    feedback=feedback,
                    spec=spec,
                )
            )

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

        Semi-idempotent: calling `complete` twice on an already-COMPLETED session
        returns the existing scorecard — UNLESS the current attempt evaluations
        differ from the stored scorecard activities (e.g. after a session restart
        where scores were re-evaluated). In that case the stale scorecard is
        deleted and rebuilt so the scorecard always reflects the latest scores.
        """
        now = now or datetime.now(timezone.utc)
        session = self._load_owned(session_id=session_id, user_id=user_id)

        if session.status is SessionStatus.ABANDONED:
            raise SessionAbandoned(f"session {session_id!r} was abandoned")

        # Track whether a prior scorecard had already applied points.
        # Set to True in the COMPLETED rebuild path to prevent double-counting.
        old_points_applied: bool = False

        if session.status is SessionStatus.COMPLETED:
            existing = self.scorecards_repo.get_for_session(session.id)
            if existing is None:
                raise RuntimeError(
                    f"session {session_id!r} is COMPLETED but has no scorecard"
                )

            # Check whether any attempt evaluation score has changed since the
            # scorecard was built (happens when session is restarted and the
            # learner re-submits activities with better scores).
            current_attempts = self.attempts_repo.list_for_session(session.id)
            stored_scores: dict[int, float] = {
                a["attempt_id"]: float(a["raw_score"])
                for a in (existing.activities or [])
                if isinstance(a, dict)
            }
            scores_changed = False
            for att in current_attempts:
                if att.status is not AttemptStatus.EVALUATED or att.evaluation is None:
                    continue
                current_raw = float(att.evaluation.raw_score)
                stored_raw = stored_scores.get(att.id)
                if stored_raw is None or abs(current_raw - stored_raw) > 0.05:
                    scores_changed = True
                    break

            if not scores_changed:
                return existing, ApplyReport(
                    applied=False, rows_written=0, rows_skipped=0,
                    reason="session already completed",
                )

            # Scores changed — delete stale scorecard and rebuild below.
            logger.info(
                "complete_session: scorecard for session %r has stale scores, rebuilding",
                session_id,
            )
            old_points_applied = existing.points_applied
            self.db.delete(existing)
            self.db.flush()
            # Re-open the session so it can be completed again.
            session.status = SessionStatus.IN_PROGRESS

        # Build ActivityScore list from every EVALUATED attempt.
        attempts = self.attempts_repo.list_for_session(session.id)
        scored: list[ActivityScore] = []
        activities_breakdown: list[dict] = []
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
            raw = float(attempt.evaluation.raw_score)
            activities_breakdown.append({
                "attempt_id": attempt.id,
                "sequence": attempt.sequence,
                "archetype_id": attempt.archetype_id,
                "archetype_label": spec.name,
                "raw_score": raw,
                "tier": tier_for_score(raw).value,
                "base_reward": int(attempt.evaluation.base_reward),
                "weighted_points": {
                    k: float(v) for k, v in dict(attempt.evaluation.weighted_points).items()
                },
            })

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
            activities=activities_breakdown,
            completed_at=now,
            points_applied=False,
        )
        self.scorecards_repo.add(scorecard)

        # Flush so apply_session_scorecard sees committed scorecard + session state.
        # If we are rebuilding a scorecard that already had its points applied
        # (e.g. after a session restart where scores improved), skip re-applying
        # to avoid double-counting points in SkillPoints.
        if old_points_applied:
            report = ApplyReport(
                applied=False, rows_written=0, rows_skipped=0,
                reason="rebuilt scorecard — points already applied from first completion",
            )
            scorecard.points_applied = True  # preserve applied status
        else:
            report = apply_session_scorecard(self.db, session=session, scorecard=scorecard)
            scorecard.points_applied = report.applied

        # Generate mentor note via RAG (additive, never blocks).
        mentor_note = await self._generate_mentor_note_safe(
            session=session,
            activities_breakdown=activities_breakdown,
        )
        scorecard.mentor_note = mentor_note

        session.status = SessionStatus.COMPLETED
        session.completed_at = now

        # Record streak event in the same transaction. Idempotent under
        # double-fire via the unique constraint on (user_id, local_date).
        from app.modules.streaks.service import StreakService
        StreakService(self.db).record_in_same_tx(
            user_id=session.user_id,
            session_id=session.id,
            now_utc=now,
        )

        self.db.commit()
        self.db.refresh(scorecard)

        # Fire-and-forget: store session summary in RAG memory.
        if self._rag_service is not None and mentor_note:
            asyncio.create_task(
                self._store_session_memory_safe(
                    user_id=session.user_id,
                    session_id=session.id,
                    day_id=session.day_id,
                    activities_summary=activities_breakdown,
                    points_earned=dict(aggregation.points_earned),
                    mentor_note=mentor_note,
                )
            )

        return scorecard, report

    # ── read ───────────────────────────────────────────────────────

    def get_scorecard(self, *, session_id: str, user_id: int) -> SessionScorecard | None:
        session = self._load_owned(session_id=session_id, user_id=user_id)
        return self.scorecards_repo.get_for_session(session.id)

    def get_session(self, *, session_id: str, user_id: int) -> DailySession:
        return self._load_owned(session_id=session_id, user_id=user_id)

    # ── advance day ────────────────────────────────────────────────

    def advance_day(self, *, user_id: int) -> tuple[int, int]:
        """Move the learner's preference pointer to the next unlocked day."""
        pref = self.preferences_repo.get_or_create_for_user(user_id)
        week = self.weeks_repo.get_by_number(
            course_length=pref.course_length,
            week_number=pref.current_week,
        )
        if week is None:
            raise DayNotFound(
                f"No curriculum week for course_length={pref.course_length!r} "
                f"week={pref.current_week}"
            )

        day = self.days_repo.get_for_week(
            week_pk=week.id,
            day_number=pref.current_day_in_week,
        )
        if day is None:
            raise DayNotFound(
                f"No curriculum day for week_id={week.week_id!r} "
                f"day={pref.current_day_in_week}"
            )

        latest = self.sessions_repo.get_latest_for_day(
            user_id=user_id,
            day_id=day.day_id,
        )
        if latest is None or latest.status is not SessionStatus.COMPLETED:
            raise SessionAdvanceBlocked(
                "Complete today's session before unlocking the next day."
            )

        weeks = self.weeks_repo.list_for_course(pref.course_length)
        max_week = max((w.week_number for w in weeks), default=0)
        if max_week <= 0:
            raise DayNotFound(
                f"No curriculum weeks for course_length={pref.course_length!r}"
            )
        if pref.current_week >= max_week and pref.current_day_in_week >= 7:
            raise SessionAdvanceBlocked("You are already at the final course day.")

        now = datetime.now(timezone.utc)
        if pref.current_day_in_week >= 7:
            pref.current_week += 1
            pref.current_day_in_week = 1
        else:
            pref.current_day_in_week += 1
        pref.current_day_started_at = now
        pref.last_completed_on = now.date()

        self.db.commit()
        self.db.refresh(pref)
        return pref.current_week, pref.current_day_in_week

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
        day_topic: str,
        explanation_brief: str,
        archetype_id: str,
        sequence: int,
        is_mandatory: bool,
        cefr_level: str,
        sub_level: int,
        user_interests: list[str] | None,
        task_spec: dict | None = None,
    ) -> ActivityAttempt:
        spec = get_archetype(archetype_id)
        generated = await self.task_generator.generate(
            archetype=spec,
            day_topic=day_topic,
            explanation_brief=explanation_brief,
            cefr_level=cefr_level,
            sub_level=sub_level,
            user_interests=user_interests,
            task_spec=task_spec,
        )
        attempt = ActivityAttempt(
            session_id=session.id,
            archetype_id=archetype_id,
            sequence=sequence,
            is_mandatory=is_mandatory,
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

    @staticmethod
    def _file_overrides_for_day(day_id: str) -> dict[str, dict]:
        """Return evaluator/feedback overrides from the file-authored day, if any.

        Returns ``{"evaluator": {...}, "feedback": {...}}`` when the day is
        file-authored in ``source_24w.py`` and has non-empty override dicts.
        Returns ``{}`` for non-authored days or when ``file_source`` raises.
        """
        try:
            file_day = file_get_day_by_id(day_id)
        except DayNotFound:
            return {}
        result: dict[str, dict] = {}
        if file_day.evaluator_overrides:
            result["evaluator"] = dict(file_day.evaluator_overrides)
        if file_day.feedback_overrides:
            result["feedback"] = dict(file_day.feedback_overrides)
        return result

    # ── RAG helpers (fire-and-forget) ──────────────────────────────

    async def _store_activity_memory_safe(
        self,
        *,
        user_id: int,
        session_id: int,
        attempt_id: int,
        archetype_id: str,
        day_id: str,
        feedback: Any,
        spec: Any,
    ) -> None:
        """Store activity feedback in RAG memory. Never raises."""
        try:
            if self._rag_service is None:
                return
            await self._rag_service.store_activity_feedback(
                user_id=user_id,
                session_id=session_id,
                attempt_id=attempt_id,
                archetype_id=archetype_id,
                archetype_name=spec.name,
                day_id=day_id,
                score=feedback.score,
                mistakes=list(feedback.mistakes or []),
                did_well=list(feedback.did_well or []),
                next_tip=feedback.next_tip,
                summary=feedback.summary,
            )
        except Exception:
            logger.warning(
                "Failed to store activity memory for attempt=%d",
                attempt_id, exc_info=True,
            )

    async def _store_session_memory_safe(
        self,
        *,
        user_id: int,
        session_id: int,
        day_id: str,
        activities_summary: list[dict],
        points_earned: dict[str, int],
        mentor_note: str,
    ) -> None:
        """Store session summary in RAG memory. Never raises."""
        try:
            if self._rag_service is None:
                return
            await self._rag_service.store_session_summary(
                user_id=user_id,
                session_id=session_id,
                day_id=day_id,
                activities_summary=activities_summary,
                points_earned=points_earned,
                mentor_note=mentor_note,
            )
        except Exception:
            logger.warning(
                "Failed to store session memory for session=%d",
                session_id, exc_info=True,
            )

    async def _generate_mentor_note_safe(
        self,
        *,
        session: DailySession,
        activities_breakdown: list[dict],
    ) -> str | None:
        """Retrieve RAG context and generate mentor note. Never raises.

        Returns None on any failure — scorecard is still returned.
        """
        if self._rag_service is None or self._mentor_generator is None:
            return None

        try:
            # Collect today's mistakes from all attempts
            attempts = self.attempts_repo.list_for_session(session.id)
            today_mistakes: list[dict] = []
            for attempt in attempts:
                if attempt.feedback is not None:
                    today_mistakes.extend(attempt.feedback.mistakes or [])

            # Retrieve RAG context
            rag_context = await self._rag_service.retrieve_context_for_feedback(
                user_id=session.user_id,
                current_mistakes=today_mistakes,
                current_day_id=session.day_id,
            )

            # Collect points earned from activities_breakdown
            points_earned: dict[str, int] = {}
            for act in activities_breakdown:
                for skill, pts in act.get("weighted_points", {}).items():
                    points_earned[skill] = points_earned.get(skill, 0) + int(pts)

            # Generate mentor note
            mentor_note = await self._mentor_generator.generate(
                today_activities=activities_breakdown,
                today_mistakes=today_mistakes,
                rag_context=rag_context,
                points_earned=points_earned,
            )
            return mentor_note

        except Exception:
            logger.warning(
                "Mentor note generation failed for session=%s",
                session.session_id, exc_info=True,
            )
            return None
