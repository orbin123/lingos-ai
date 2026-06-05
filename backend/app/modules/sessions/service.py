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

from app.core.config import settings
from app.modules.sessions.contracts.agent_inputs import (
    EvaluatorAgentInput,
    FeedbackAgentInput,
    TaskGenAgentInput,
    build_agent_input,
)
from app.modules.sessions.contracts.validation import normalize_task_content
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
from app.modules.progress.repository import (
    SkillPointsLogRepository,
    SkillPointsRepository,
)
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
    is_valid_task_content,
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


def _validate_agent_input(model_cls, **fields) -> None:
    """Guard a service→agent boundary input.

    Raises under ``settings.strict_contracts``; otherwise logs and proceeds on
    the legacy path. Validation is for its side effect (catch missing/mistyped
    inputs early) — callers keep using their original values.
    """
    if build_agent_input(model_cls, strict=settings.strict_contracts, **fields) is None:
        logger.warning(
            "Agent input validation failed at %s boundary — proceeding on legacy path",
            model_cls.__name__,
        )


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
        self.points_log_repo = SkillPointsLogRepository(db)
        self.preferences_repo = UserCoursePreferenceRepository(db)

        # RAG memory service — optional. When absent (tests, early phases),
        # activity memory storage and mentor note generation are skipped.
        self._rag_service: Any | None = None
        self._mentor_generator: Any | None = None
        self._pending_rag_tasks: list[asyncio.Task[None]] = []

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

        If the day is file-authored (24w ``day_24_*`` or 48w ``day_48_*``,
        resolved via ``file_source``), the archetype order and task specs come
        from the composed band source files instead of the planner.
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
        healed = normalize_task_content(spec.archetype_id, content)
        if spec.archetype_id == "SPEAK_PIC_DESC":
            from app.ai.sessions.llm_task_generator import LLMTaskGenerator

            image_alt = str(healed.get("image_alt") or "").strip()
            image_url = str(healed.get("image_url") or "").strip()
            if image_alt and not image_url and not healed.get("image_error"):
                healed = await LLMTaskGenerator._attach_required_image(
                    content=healed,
                    archetype=spec,
                )
        if healed != content:
            attempt.task_content = healed
            self.db.commit()
            self.db.refresh(attempt)
            content = healed
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
        return is_valid_task_content(spec.archetype_id, content)

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
        return self._attach_activity_contract(
            content=dict(generated.content),
            archetype=archetype,
            sequence=attempt.sequence,
            is_mandatory=attempt.is_mandatory,
            task_spec=task_spec,
        )

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
        _validate_agent_input(
            EvaluatorAgentInput,
            archetype_id=attempt.archetype_id,
            task_content=attempt.task_content or {},
            user_response=user_response or {},
        )
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
        _validate_agent_input(
            FeedbackAgentInput,
            archetype_id=attempt.archetype_id,
            task_content=attempt.task_content or {},
            evaluation={
                "raw_score": eval_result.raw_score,
                "rubric_scores": dict(eval_result.rubric_scores or {}),
            },
            user_response=user_response or {},
        )
        # Phase 2 (flagged): make feedback memory-aware. Advisory only —
        # never changes the score. No-op when the flag is off or RAG is
        # unavailable.
        learner_history: str | None = None
        if settings.RAG_PER_ACTIVITY_FEEDBACK and self._rag_service is not None:
            try:
                learner_history = await asyncio.wait_for(
                    self._rag_service.retrieve_context_for_activity(
                        user_id=session.user_id,
                        archetype_id=attempt.archetype_id,
                        query_text=f"{spec.name}: {eval_result.evaluator_notes or ''}",
                    ),
                    timeout=settings.RAG_PER_ACTIVITY_TIMEOUT_S,
                )
            except Exception:
                # Best-effort: a slow/failed lookup must never block feedback.
                logger.warning(
                    "Per-activity RAG retrieval skipped (timeout/error) for attempt=%d",
                    attempt.id, exc_info=True,
                )
                learner_history = None

        fb: FeedbackResult = await self.feedback_generator.generate(
            archetype=spec,
            evaluation=eval_result,
            user_response=user_response,
            task_content=attempt.task_content,
            feedback_overrides=file_overrides.get("feedback") or None,
            learner_history=learner_history,
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

        # Streak: first evaluated activity per local calendar day (same TX).
        from app.modules.streaks.service import StreakService

        StreakService(self.db).record_in_same_tx(
            user_id=session.user_id,
            session_id=session.id,
            now_utc=now,
        )

        self.db.commit()
        self.db.refresh(attempt)
        self.db.refresh(evaluation)
        self.db.refresh(feedback)

        # NOTE: activity feedback is NOT indexed to the vector store here.
        # Doing so on `self.db` (the request/WebSocket-scoped session) from a
        # background task races the live chat flow — a SQLAlchemy Session is
        # not safe for concurrent use. Indexing happens in the post-completion
        # background worker (`run_post_completion_rag`), which opens its own
        # session and re-indexes every evaluated activity idempotently.

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

        existing = self.scorecards_repo.get_for_session(session.id)

        if existing is not None:
            if session.status is SessionStatus.COMPLETED:
                # Check whether any attempt evaluation score has changed since the
                # scorecard was built.
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

                logger.info(
                    "complete_session: scorecard for session %r has stale scores, rebuilding",
                    session_id,
                )

            # We either have an IN_PROGRESS session that was previously completed
            # (restarted) OR a COMPLETED session with stale scores. Delete to rebuild.
            old_points_applied = existing.points_applied
            self.db.delete(existing)
            self.db.flush()
            # Re-open the session so it can be completed again.
            session.status = SessionStatus.IN_PROGRESS

        # If the prior scorecard was already deleted on a reopen (per-activity
        # reset or full restart drop the scorecard, not the append-only points
        # log), the `existing` row is gone but the log still proves points were
        # awarded for this session. Treat that as already-applied so a
        # re-completion rebuilds the scorecard with the new scores WITHOUT
        # awarding a second batch of points.
        if not old_points_applied and self.points_log_repo.has_for_session(
            session.id
        ):
            old_points_applied = True

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

        # The Coach's Note is NOT generated here. Completion stays fast and the
        # scorecard is committed with mentor_note=None; the note is produced by
        # the explicit, awaited ``ensure_mentor_note`` step (owned by the chat WS
        # / REST completion path) so it can be delivered to the client in-band
        # instead of racing a hard inline timeout. See ensure_mentor_note.
        session.status = SessionStatus.COMPLETED
        session.completed_at = now

        self.db.commit()
        self.db.refresh(scorecard)

        # Background (own DB session): index per-activity vectors only. The note
        # and the day-level summary vector are handled by ensure_mentor_note.
        if self._rag_service is not None:
            self._schedule_post_completion_rag(
                session_id=session.session_id,
                user_id=session.user_id,
            )

        return scorecard, report

    async def run_post_completion_rag(
        self,
        *,
        session_id: str,
        user_id: int,
    ) -> None:
        """Index per-activity feedback vectors after completion.

        Runs after ``complete_session`` has committed. The mentor note and the
        day-level session-summary vector are NOT produced here — they belong to
        ``ensure_mentor_note`` (the awaited, in-band delivery path). Never raises.
        """
        try:
            session = self._load_owned(session_id=session_id, user_id=user_id)
            scorecard = self.scorecards_repo.get_for_session(session.id)
            if scorecard is None:
                return

            attempts = self.attempts_repo.list_for_session(session.id)

            if self._rag_service is not None:
                for attempt in attempts:
                    if attempt.status is not AttemptStatus.EVALUATED:
                        continue
                    if attempt.feedback is None:
                        continue
                    await self._store_activity_memory_safe(
                        user_id=session.user_id,
                        session_id=session.id,
                        attempt_id=attempt.id,
                        archetype_id=attempt.archetype_id,
                        day_id=session.day_id,
                        feedback=attempt.feedback,
                        spec=get_archetype(attempt.archetype_id),
                    )

            self.db.commit()
        except Exception:
            logger.warning(
                "Post-completion RAG pipeline failed for session=%s",
                session_id,
                exc_info=True,
            )
            self.db.rollback()

    async def ensure_mentor_note(
        self,
        *,
        session_id: str,
        user_id: int,
    ) -> str | None:
        """Generate (if needed) and persist the Coach's Note for a session.

        Idempotent: if the scorecard already carries a note it is returned
        without re-invoking the LLM. Otherwise the note is generated, persisted
        alongside the day-level session-summary vector, committed, and returned.
        Safe to call from the awaited completion path (chat WS / REST) and from a
        write-only background fallback. Never raises.
        """
        try:
            session = self._load_owned(session_id=session_id, user_id=user_id)
            scorecard = self.scorecards_repo.get_for_session(session.id)
            if scorecard is None:
                return None
            if scorecard.mentor_note:
                return scorecard.mentor_note
            if self._rag_service is None or self._mentor_generator is None:
                return None

            activities_breakdown = [
                dict(item)
                for item in (scorecard.activities or [])
                if isinstance(item, dict)
            ]
            mentor_note = await self._generate_mentor_note_safe(
                session=session,
                activities_breakdown=activities_breakdown,
            )
            if not mentor_note:
                return None

            scorecard.mentor_note = mentor_note
            # Day-level summary vector depends on the note, so it is stored here
            # rather than in the activity-indexing worker. Idempotent.
            await self._store_session_memory_safe(
                user_id=session.user_id,
                session_id=session.id,
                day_id=session.day_id,
                activities_summary=activities_breakdown,
                points_earned={
                    k: int(v)
                    for k, v in dict(scorecard.points_earned or {}).items()
                },
                mentor_note=mentor_note,
            )
            self.db.commit()
            return mentor_note
        except Exception:
            logger.warning(
                "ensure_mentor_note failed for session=%s",
                session_id,
                exc_info=True,
            )
            self.db.rollback()
            return None

    def _schedule_post_completion_rag(
        self,
        *,
        session_id: str,
        user_id: int,
    ) -> None:
        """Fire-and-forget mentor note + RAG indexing after completion commit."""
        task = asyncio.create_task(
            _run_post_completion_rag_worker(
                session_id=session_id,
                user_id=user_id,
            )
        )
        self._pending_rag_tasks.append(task)
        task.add_done_callback(self._discard_pending_rag_task)

    def _schedule_rag_delete(
        self,
        *,
        attempt_ids: list[int],
        session_pk: int,
        delete_summary: bool,
    ) -> None:
        """Fire-and-forget Pinecone/Postgres-mirror vector cleanup after a reset.

        Runs on its own DB session (the delete also touches the Postgres mirror),
        so it never shares the request-scoped ``self.db`` and never blocks the
        reset/restart commit. Best-effort: failures are logged, never raised.
        """
        task = asyncio.create_task(
            _run_rag_delete_worker(
                attempt_ids=list(attempt_ids),
                session_pk=session_pk,
                delete_summary=delete_summary,
            )
        )
        self._pending_rag_tasks.append(task)
        task.add_done_callback(self._discard_pending_rag_task)

    def _discard_pending_rag_task(self, task: asyncio.Task[None]) -> None:
        try:
            self._pending_rag_tasks.remove(task)
        except ValueError:
            pass
        if task.cancelled():
            return
        exc = task.exception()
        if exc is not None:
            logger.warning(
                "Post-completion RAG background task failed",
                exc_info=exc,
            )

    # ── read ───────────────────────────────────────────────────────

    def get_scorecard(self, *, session_id: str, user_id: int) -> SessionScorecard | None:
        session = self._load_owned(session_id=session_id, user_id=user_id)
        return self.scorecards_repo.get_for_session(session.id)

    def get_session(self, *, session_id: str, user_id: int) -> DailySession:
        return self._load_owned(session_id=session_id, user_id=user_id)

    # ── reset ──────────────────────────────────────────────────────

    async def reset_activity(
        self,
        *,
        session_id: str,
        user_id: int,
        sequence: int,
    ) -> ActivityAttempt:
        """Reset a single activity so it can be re-attempted.

        Deletes the attempt's evaluation + feedback and flips it back to
        PENDING (clearing the stored response). If the daily session was
        already COMPLETED, it is reopened (status → IN_PROGRESS, completed_at
        cleared) and its now-stale scorecard is deleted; the scorecard is
        rebuilt the next time the session is completed.

        Also purges the attempt's RAG memory vector (and the now-stale
        session-summary vector if the session was completed) so Pinecone
        stays in sync with Postgres. The RAG cleanup is additive and never
        blocks the reset.
        """
        session = self._load_owned(session_id=session_id, user_id=user_id)
        if session.status is SessionStatus.ABANDONED:
            raise SessionAbandoned(f"session {session_id!r} was abandoned")

        attempt = self.attempts_repo.get(session_pk=session.id, sequence=sequence)
        if attempt is None:
            raise AttemptNotFound(
                f"session {session_id!r}: no attempt at sequence {sequence}"
            )

        was_completed = session.status is SessionStatus.COMPLETED
        attempt_id = attempt.id
        session_pk = session.id

        self.evaluations_repo.delete_for_attempt(attempt.id)
        self.feedback_repo.delete_for_attempt(attempt.id)
        self.attempts_repo.reset_to_pending(attempt)

        if was_completed:
            self.scorecards_repo.delete_for_session(session.id)
            session.status = SessionStatus.IN_PROGRESS
            session.completed_at = None

        # Commit the V2 reset immediately so per-activity retry never waits on
        # Pinecone. Vector cleanup (which also touches the Postgres mirror) is
        # scheduled fire-and-forget on its own DB session afterwards.
        self.db.commit()
        self.db.refresh(attempt)

        if self._rag_service is not None:
            self._schedule_rag_delete(
                attempt_ids=[attempt_id],
                session_pk=session_pk,
                delete_summary=was_completed,
            )

        return attempt

    async def reset_session_full(
        self,
        *,
        session_id: str,
        user_id: int,
    ) -> DailySession:
        """Reset every activity in the day so it can be re-attempted from scratch.

        Deletes each attempt's evaluation + feedback, flips all attempts back to
        PENDING (clearing stored responses), deletes the SessionScorecard, and
        reopens the DailySession (status → IN_PROGRESS, completed_at cleared).
        The scorecard is rebuilt the next time the day is completed.

        Owns its commit so callers (e.g. the chat-layer ``restart_session``)
        don't have to duplicate V2 deletes. RAG vector cleanup is additive,
        runs in the background, and never blocks the restart.
        """
        session = self._load_owned(session_id=session_id, user_id=user_id)
        if session.status is SessionStatus.ABANDONED:
            raise SessionAbandoned(f"session {session_id!r} was abandoned")

        session_pk = session.id
        attempts = self.attempts_repo.list_for_session(session.id)
        attempt_ids = [attempt.id for attempt in attempts]

        for attempt in attempts:
            self.evaluations_repo.delete_for_attempt(attempt.id)
            self.feedback_repo.delete_for_attempt(attempt.id)
            self.attempts_repo.reset_to_pending(attempt)

        self.scorecards_repo.delete_for_session(session.id)
        session.status = SessionStatus.IN_PROGRESS
        session.completed_at = None

        # Commit the V2 reset immediately so restart never waits on Pinecone.
        self.db.commit()
        self.db.refresh(session)

        if self._rag_service is not None and attempt_ids:
            self._schedule_rag_delete(
                attempt_ids=attempt_ids,
                session_pk=session_pk,
                delete_summary=True,
            )

        return session

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
        course_cap = 24 if pref.course_length == "24w" else 48
        max_week = min(max((w.week_number for w in weeks), default=0), course_cap)
        if max_week <= 0:
            raise DayNotFound(
                f"No curriculum weeks for course_length={pref.course_length!r}"
            )
        if pref.current_week >= max_week and pref.current_day_in_week >= 7:
            raise SessionAdvanceBlocked("You are already at the final course day.")

        # Pre-flight: verify the target position exists before committing.
        if pref.current_day_in_week >= 7:
            next_week_num = pref.current_week + 1
            next_week_row = self.weeks_repo.get_by_number(
                course_length=pref.course_length,
                week_number=next_week_num,
            )
            if next_week_row is None:
                raise DayNotFound(
                    f"Cannot advance: week {next_week_num} is not seeded for "
                    f"course_length={pref.course_length!r}"
                )
            next_day_row = self.days_repo.get_for_week(
                week_pk=next_week_row.id,
                day_number=1,
            )
            if next_day_row is None:
                raise DayNotFound(
                    f"Cannot advance: day 1 not seeded for week {next_week_num}"
                )

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
        _validate_agent_input(
            TaskGenAgentInput,
            archetype_id=archetype_id,
            day_topic=day_topic,
            explanation_brief=explanation_brief,
            cefr_level=cefr_level,
            sub_level=sub_level,
            task_spec=task_spec or {},
        )
        generated = await self.task_generator.generate(
            archetype=spec,
            day_topic=day_topic,
            explanation_brief=explanation_brief,
            cefr_level=cefr_level,
            sub_level=sub_level,
            user_interests=user_interests,
            task_spec=task_spec,
        )
        content = self._attach_activity_contract(
            content=dict(generated.content),
            archetype=spec,
            sequence=sequence,
            is_mandatory=is_mandatory,
            task_spec=task_spec,
        )
        attempt = ActivityAttempt(
            session_id=session.id,
            archetype_id=archetype_id,
            sequence=sequence,
            is_mandatory=is_mandatory,
            status=AttemptStatus.PENDING,
            task_content=content,
        )
        self.db.add(attempt)
        self.db.flush()
        return attempt

    @staticmethod
    def _attach_activity_contract(
        *,
        content: dict,
        archetype: ArchetypeSpec,
        sequence: int,
        is_mandatory: bool,
        task_spec: dict | None,
    ) -> dict:
        """Persist deterministic blueprint metadata beside generated content."""

        spec = task_spec or {}
        contract = {
            "activity_id": spec.get("activity_id"),
            "sequence": sequence,
            "archetype_id": archetype.archetype_id,
            "activity": spec.get("activity") or archetype.core_activity,
            "task_widget": spec.get("task_widget")
            or content.get("widget")
            or content.get("ui_widget")
            or archetype.ui_widget,
            "evaluator_type": spec.get("evaluator_type") or "default",
            "evaluation_widget": spec.get("evaluation_widget") or "activity_score",
            "feedback_type": spec.get("feedback_type") or "default",
            "feedback_widget": spec.get("feedback_widget") or "feedback_card",
            "mandatory": bool(spec.get("mandatory", is_mandatory)),
        }
        contract = {
            key: value
            for key, value in contract.items()
            if value not in (None, "", {})
        }
        content["activity_contract"] = contract
        content.setdefault("task_widget", contract["task_widget"])
        content.setdefault("evaluator_type", contract["evaluator_type"])
        content.setdefault("evaluation_widget", contract["evaluation_widget"])
        content.setdefault("feedback_type", contract["feedback_type"])
        content.setdefault("feedback_widget", contract["feedback_widget"])
        if contract.get("activity_id") is not None:
            content.setdefault("activity_id", contract["activity_id"])
        return content

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
        file-authored (24w/48w, resolved via ``file_source``) and has non-empty
        override dicts. Returns ``{}`` for non-authored days or when
        ``file_source`` raises.
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
                current_session_id=session.id,
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


async def _run_post_completion_rag_worker(
    *,
    session_id: str,
    user_id: int,
) -> None:
    """Background worker with its own DB session for post-completion RAG."""
    from app.core.database import SessionLocal
    from app.modules.sessions.routes import _make_session_service

    db = SessionLocal()
    try:
        service = _make_session_service(db)
        await service.run_post_completion_rag(
            session_id=session_id,
            user_id=user_id,
        )
    except Exception:
        logger.warning(
            "Post-completion RAG worker failed for session=%s",
            session_id,
            exc_info=True,
        )
        db.rollback()
    finally:
        db.close()


async def generate_mentor_note_async(
    *,
    session_id: str,
    user_id: int,
) -> str | None:
    """Ensure the Coach's Note on a dedicated DB session, off the request loop.

    Used both as the chat WS in-band generator (awaited under a ceiling via
    ``asyncio.shield`` so a timeout never cancels the DB work) and as the
    write-only fallback when that await times out — in either case the note is
    persisted for later scorecard/dashboard reads. Never raises.
    """
    from app.core.database import SessionLocal
    from app.modules.sessions.routes import _make_session_service

    db = SessionLocal()
    try:
        service = _make_session_service(db)
        return await service.ensure_mentor_note(
            session_id=session_id,
            user_id=user_id,
        )
    except Exception:
        logger.warning(
            "Mentor note worker failed for session=%s",
            session_id,
            exc_info=True,
        )
        db.rollback()
        return None
    finally:
        db.close()


async def _run_rag_delete_worker(
    *,
    attempt_ids: list[int],
    session_pk: int,
    delete_summary: bool,
) -> None:
    """Background worker (own DB session) that purges stale RAG vectors.

    Called fire-and-forget after a per-activity or full-session reset has
    committed. Removes the activity-feedback vector(s) for each reset attempt
    and, when the day was reopened, the now-stale session-summary vector.
    The underlying delete also writes the Postgres mirror, so it must run on a
    dedicated session rather than the request-scoped one. Never raises.
    """
    from app.core.database import SessionLocal
    from app.modules.sessions.routes import _make_session_service

    db = SessionLocal()
    try:
        service = _make_session_service(db)
        rag = service._rag_service
        if rag is None:
            return
        for attempt_id in attempt_ids:
            await rag.delete_for_attempt(attempt_id)
        if delete_summary:
            await rag.delete_session_summary(session_pk)
    except Exception:
        logger.warning(
            "rag.delete.worker failed for session_pk=%s attempts=%s",
            session_pk,
            attempt_ids,
            exc_info=True,
        )
        db.rollback()
    finally:
        db.close()
