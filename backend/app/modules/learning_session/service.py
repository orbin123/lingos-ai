"""Business logic for chat-driven learning sessions.

LearningSession is the **conversation envelope** layered on top of the
V2 `DailySession`. The V2 row owns the task content, the evaluation, the
feedback rows, the scorecard, and the scoring writeback. This service
owns the conversation (messages, phase, teacher persona, streaming).

The flow:

  1. ``create_session`` — find/create the V2 DailySession for today via
     UserCoursePreference (or accept an explicit `daily_session_id`),
     run the PlannerAgent against the V2 curriculum row to build a
     teacher persona, persist a LearningSession row, return the
     session_id the frontend opens a WebSocket against.

  2. ``process_message_stream`` — the WebSocket message handler. Routes
     by `phase` + incoming message type, calls the V2 SessionService for
     evaluation/feedback/completion, formats results as chat messages.
"""

from __future__ import annotations

import asyncio
import logging
import re
import uuid
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.orm import Session

from app.ai.agents.planner import PlannerAgent
from app.ai.agents.teacher import stream_teaching_turn
from app.ai.graphs.nodes import (
    stream_answer_question,
    task_delivery_node,
)
from app.ai.graphs.state import LearningSessionState
from app.modules.auth.repository import UserProfileRepository
from app.modules.curriculum.adapters import v2_course_topic
from app.modules.curriculum.repository import (
    CurriculumDayRepository,
    TaskArchetypeRepository,
)
from app.modules.learning_session.models import LearningSession
from app.modules.learning_session.repository import LearningSessionRepository
from app.modules.learning_session.schemas import (
    StartSessionResponse,
    WSIncomingMessage,
    WSOutgoingMessage,
)
from app.modules.preferences.service import PreferenceService
from app.modules.sessions.exceptions import (
    AttemptAlreadySubmitted,
    AttemptNotFound,
    SessionAbandoned,
    SessionAlreadyCompleted,
    SessionAlreadyOpen,
    SessionNotFound,
)
from app.modules.sessions.models import (
    ActivityAttempt,
    AttemptStatus,
    DailySession,
    SessionStatus,
)
from app.modules.sessions.repository import (
    ActivityAttemptRepository,
    DailySessionRepository,
)
from app.modules.sessions.service import SessionService
from app.scoring import CourseLength

logger = logging.getLogger(__name__)


_ACKNOWLEDGEMENT_PHRASES = (
    "yes", "yeah", "yep", "sure", "ok", "okay",
)

_ACKNOWLEDGEMENT_PATTERNS = tuple(
    re.compile(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])")
    for phrase in _ACKNOWLEDGEMENT_PHRASES
)

_EXPLICIT_UNDERSTANDING_PHRASES = (
    "ready", "let's go", "lets go", "i understand", "understand", "got it",
    "i got it", "i'm ready", "im ready", "go ahead", "begin", "start",
)

_EXPLICIT_UNDERSTANDING_PATTERNS = tuple(
    re.compile(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])")
    for phrase in _EXPLICIT_UNDERSTANDING_PHRASES
)

_NON_UNDERSTANDING_PHRASES = (
    "i don't understand", "i dont understand", "i do not understand",
    "i didn't understand", "i didnt understand", "i did not understand",
    "don't understand", "dont understand", "do not understand",
    "didn't understand", "didnt understand", "did not understand",
    "not understand", "not clear", "unclear", "confused",
    "i don't get", "i dont get", "i didn't get", "i didnt get",
    "not ready", "not yet", "wait", "explain again",
)

_NON_UNDERSTANDING_PATTERNS = tuple(
    re.compile(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])")
    for phrase in _NON_UNDERSTANDING_PHRASES
)

_QUESTION_START_PATTERN = re.compile(
    r"^\s*(what|why|how|when|where|which|who|can you|could you|would you)\b"
)

_READINESS_PROMPT_PATTERNS = (
    re.compile(r"\b(do you|does this|is this|that|it)\s+(feel\s+)?(clear|make sense)\b"),
    re.compile(r"\b(are you|do you feel|feel)\s+ready\b"),
    re.compile(r"\bready\s+(for|to)\s+(practice|try|start|begin)\b"),
    re.compile(r"\bif\s+(that|this|it)\s+feels\s+clear\b"),
    re.compile(r"\bif\s+you\s+(feel\s+)?(ready|clear)\b"),
    re.compile(r"\bsay\s+['\"]?(ready|yes|okay|ok)['\"]?\b"),
)

_TEACHING_STREAM_FIRST_CHUNK_TIMEOUT_S = 8.0
_TEACHING_STREAM_CHUNK_TIMEOUT_S = 20.0
_FOLLOWUP_STREAM_FIRST_CHUNK_TIMEOUT_S = 8.0
_FOLLOWUP_STREAM_CHUNK_TIMEOUT_S = 20.0


class LearningSessionTaskUnavailable(Exception):
    """Raised when a chat session cannot be opened against the V2 daily session."""


def _last_tutor_message(messages: list[dict]) -> str:
    for message in reversed(messages):
        if message.get("role") in ("ai", "assistant"):
            return str(message.get("content") or "").strip()
    return ""


def _tutor_asked_readiness(text: str) -> bool:
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return False
    return any(pattern.search(cleaned) for pattern in _READINESS_PROMPT_PATTERNS)


def _looks_like_acknowledgement(text: str) -> bool:
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return False
    return cleaned in _ACKNOWLEDGEMENT_PHRASES or any(
        pattern.search(cleaned) for pattern in _ACKNOWLEDGEMENT_PATTERNS
    )


def _looks_like_understanding(
    text: str,
    *,
    previous_tutor_message: str = "",
) -> bool:
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return False
    if any(pattern.search(cleaned) for pattern in _NON_UNDERSTANDING_PATTERNS):
        return False
    if "?" in cleaned and _QUESTION_START_PATTERN.search(cleaned):
        return False
    if cleaned in _EXPLICIT_UNDERSTANDING_PHRASES:
        return True
    if any(pattern.search(cleaned) for pattern in _EXPLICIT_UNDERSTANDING_PATTERNS):
        return True
    if _looks_like_acknowledgement(cleaned):
        return _tutor_asked_readiness(previous_tutor_message)
    return False


class LearningSessionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.session_repo = LearningSessionRepository(db)
        self.daily_repo = DailySessionRepository(db)
        self.attempts_repo = ActivityAttemptRepository(db)
        self.curriculum_day_repo = CurriculumDayRepository(db)
        self.archetype_repo = TaskArchetypeRepository(db)
        self.profile_repo = UserProfileRepository(db)

    # ------------------------------------------------------------------
    # Session creation
    # ------------------------------------------------------------------

    async def create_session(
        self,
        *,
        user_id: int,
        daily_session_id: int | None = None,
    ) -> StartSessionResponse:
        """Create a chat session layered on the user's V2 DailySession.

        If `daily_session_id` is None, find/create today's DailySession via
        `UserCoursePreference`. Resume the existing LearningSession if one
        already exists for that DailySession.
        """
        daily = await self._resolve_daily_session(
            user_id=user_id, daily_session_id=daily_session_id
        )

        # Resume an existing chat envelope if one exists for this DailySession.
        existing = self.session_repo.get_by_daily_session_id(daily.id)
        if existing is not None:
            return StartSessionResponse(
                session_id=existing.session_id,
                daily_session_id=daily.id,
                topic=existing.topic,
                skill_name=existing.skill_name,
                task_type=existing.task_type,
                message="Session resumed",
            )

        # Load curriculum + first archetype + run PlannerAgent for the persona.
        day = self.curriculum_day_repo.get_by_day_id(daily.day_id)
        if day is None:
            raise LookupError(
                f"CurriculumDay day_id={daily.day_id!r} not found"
            )
        week = day.week
        if week is None:
            raise LookupError(
                f"CurriculumWeek for day_id={daily.day_id!r} not found"
            )

        attempts = self.attempts_repo.list_for_session(daily.id)
        if not attempts:
            raise LearningSessionTaskUnavailable(
                f"DailySession {daily.session_id} has no activity attempts"
            )
        first = attempts[0]
        archetype = self.archetype_repo.get(first.archetype_id)
        if archetype is None:
            raise LookupError(
                f"TaskArchetype archetype_id={first.archetype_id!r} not found"
            )

        topic_dict = v2_course_topic(day, week, archetype)
        course_slug = f"{daily.course_length}-course"
        learner_profile = self._profile_context(user_id)

        try:
            plan = await PlannerAgent().generate(
                user_id=user_id,
                course_slug=course_slug,
                topic_entry=topic_dict,
                learner_profile=learner_profile,
            )
        except Exception:
            logger.exception(
                "PlannerAgent failed for user_id=%s daily=%s; using neutral persona",
                user_id, daily.session_id,
            )
            plan = {"teacher_instructions": None}

        session_id = uuid.uuid4().hex
        self.session_repo.create(
            session_id=session_id,
            user_id=user_id,
            daily_session_id=daily.id,
            topic=day.topic,
            skill_name=topic_dict["sub_skill"],
            activity_type=archetype.core_activity,
            task_type=archetype.core_activity,
            user_level=topic_dict["sub_level"],
            pre_generated_tasks=dict(first.task_content or {}),
            task_queue=self._queue_from_attempts(attempts),
            teacher_instructions=plan.get("teacher_instructions"),
        )
        self.db.commit()

        return StartSessionResponse(
            session_id=session_id,
            daily_session_id=daily.id,
            topic=day.topic,
            skill_name=topic_dict["sub_skill"],
            task_type=archetype.core_activity,
            message="Session ready",
        )

    async def _resolve_daily_session(
        self,
        *,
        user_id: int,
        daily_session_id: int | None,
    ) -> DailySession:
        """Return the DailySession the chat will be layered on.

        Explicit id: load and verify ownership.
        No id: find/create today's session via UserCoursePreference.
        """
        if daily_session_id is not None:
            daily = self.db.get(DailySession, int(daily_session_id))
            if daily is None:
                raise LookupError(
                    f"DailySession id={daily_session_id} not found"
                )
            if daily.user_id != user_id:
                raise PermissionError(
                    f"User {user_id} cannot start session for daily {daily_session_id}"
                )
            return daily

        # No id — find or create today's session for the user.
        pref = PreferenceService(self.db).get(user_id=user_id)
        from app.modules.curriculum.repository import CurriculumWeekRepository

        week = CurriculumWeekRepository(self.db).get_by_number(
            course_length=pref.course_length,
            week_number=pref.current_week,
        )
        if week is None:
            raise LookupError(
                f"No curriculum week for course_length={pref.course_length!r} "
                f"week={pref.current_week}"
            )
        day = CurriculumDayRepository(self.db).get_for_week(
            week_pk=week.id, day_number=pref.current_day_in_week,
        )
        if day is None:
            raise LookupError(
                f"No curriculum day for week_id={week.week_id!r} "
                f"day={pref.current_day_in_week}"
            )

        # If an in-progress session exists, return it.
        existing = self.daily_repo.get_in_progress(
            user_id=user_id, day_id=day.day_id
        )
        if existing is not None:
            return existing

        # Otherwise start a fresh V2 session for today.
        allowed = {
            a for a, on in {
                "read": pref.allow_read,
                "write": pref.allow_write,
                "listen": pref.allow_listen,
                "speak": pref.allow_speak,
            }.items() if on
        }
        v2_service = _make_v2_session_service(self.db)
        try:
            return await v2_service.start_session(
                user_id=user_id,
                day_id=day.day_id,
                course_length=CourseLength(pref.course_length),
                tasks_per_day=pref.tasks_per_day,
                allowed_activities=allowed,
            )
        except SessionAlreadyOpen:
            # Race / retry — fetch the row another process created.
            existing = self.daily_repo.get_in_progress(
                user_id=user_id, day_id=day.day_id
            )
            if existing is None:
                raise
            return existing

    @staticmethod
    def _queue_from_attempts(attempts: list[ActivityAttempt]) -> list[dict[str, Any]]:
        return [
            {
                "sequence": a.sequence,
                "archetype_id": a.archetype_id,
                "is_mandatory": a.is_mandatory,
                "status": a.status.value if hasattr(a.status, "value") else str(a.status),
            }
            for a in attempts
        ]

    async def restart_session(
        self,
        *,
        session_id: str,
        user_id: int,
    ) -> StartSessionResponse:
        """Restart the chat conversation without resetting V2 progress.

        Re-runs the PlannerAgent so teacher_instructions reflect any
        curriculum content changes made since the session was first created.
        """
        session = self._load_session(session_id)
        if session.user_id != user_id:
            raise PermissionError(
                f"User {user_id} cannot restart session {session_id}"
            )

        # Refresh teacher instructions against current curriculum data so
        # content edits in source_24w.py (after re-seeding) take effect.
        try:
            daily = self.db.get(DailySession, session.daily_session_id)
            if daily is not None:
                day = self.curriculum_day_repo.get_by_day_id(daily.day_id)
                if day is not None and day.week is not None:
                    task_queue = session.task_queue or []
                    archetype_id = task_queue[0]["archetype_id"] if task_queue else None
                    archetype = self.archetype_repo.get(archetype_id) if archetype_id else None
                    if archetype is not None:
                        topic_dict = v2_course_topic(day, day.week, archetype)
                        course_slug = f"{daily.course_length}-course"
                        plan = await PlannerAgent().generate(
                            user_id=user_id,
                            course_slug=course_slug,
                            topic_entry=topic_dict,
                            learner_profile=self._profile_context(user_id),
                        )
                        session.teacher_instructions = plan.get("teacher_instructions")
        except Exception:
            logger.warning(
                "PlannerAgent re-run failed for session_id=%s; keeping existing instructions",
                session_id,
            )

        session.messages = []
        session.user_submission = None
        session.evaluation = None
        session.feedback = None
        session.understanding_confirmed = False
        session.phase = "teaching"
        self.session_repo.save(session)
        self.db.commit()

        return StartSessionResponse(
            session_id=session.session_id,
            daily_session_id=session.daily_session_id,
            topic=session.topic,
            skill_name=session.skill_name,
            task_type=session.task_type,
            message="Session restarted",
        )

    # ------------------------------------------------------------------
    # WebSocket message handling
    # ------------------------------------------------------------------

    async def initial_messages_stream(
        self, session_id: str
    ) -> AsyncIterator[WSOutgoingMessage]:
        """Stream the first teaching turn when the WebSocket connects."""
        session = self._load_session(session_id)
        state = self._state_from_row(session)
        self._enrich_state_with_profile(state, session.user_id)
        async for msg in self._stream_teaching_turn(session, state):
            yield msg

    async def resume_messages_stream(
        self, session_id: str
    ) -> AsyncIterator[WSOutgoingMessage]:
        """Replay enough state for a previously-started chat to continue."""
        session = self._load_session(session_id)
        state = self._state_from_row(session)
        self._enrich_state_with_profile(state, session.user_id)
        total = len(session.task_queue or []) or 1
        current = int(session.current_task_index or 0)

        # If the V2 DailySession is already complete, end the chat.
        daily = self.db.get(DailySession, session.daily_session_id)
        if daily is not None and daily.status is SessionStatus.COMPLETED:
            message = (
                "Today's activities are complete. Go back to the dashboard "
                "to review the day and advance when you're ready."
            )
            async for msg in self._stream_chat_text(
                message, actions=["Go to dashboard"]
            ):
                yield msg
            return

        if session.phase == "teaching":
            previous = _last_tutor_message(session.messages or [])
            message = previous or (
                f"Welcome back. We are learning {session.topic}. "
                "Tell me when you feel ready for the first activity."
            )
            async for msg in self._stream_chat_text(message):
                yield msg
            return

        if session.phase == "practice_task":
            message = f"Welcome back. Continue with activity {current + 1} of {total}."
            yield WSOutgoingMessage(
                type="chat_message", role="assistant", content=message,
            )
            payload = {
                **(session.pre_generated_tasks or {}),
                "_session": {
                    "current_task_index": current,
                    "total_tasks": total,
                    "daily_session_id": session.daily_session_id,
                },
            }
            yield WSOutgoingMessage(
                type="ui_event",
                widget=payload.get("widget") or payload.get("ui_widget") or session.task_type,
                payload=payload,
            )
            return

        if session.phase in ("feedback", "scorecard", "follow_up"):
            message = "Ready for the next step?"
            async for msg in self._stream_chat_text(
                message, actions=self._post_feedback_actions(session),
            ):
                yield msg
            return

        if session.phase == "ended":
            message = "This chat is finished. Go back to the dashboard when you're ready."
            async for msg in self._stream_chat_text(
                message, actions=["Go to dashboard"],
            ):
                yield msg

    async def process_message_stream(
        self, session_id: str, message: WSIncomingMessage
    ) -> AsyncIterator[WSOutgoingMessage]:
        session = self._load_session(session_id)
        state = self._state_from_row(session)
        self._enrich_state_with_profile(state, session.user_id)

        if message.type == "user_message":
            async for msg in self._handle_user_message_stream(session, state, message):
                yield msg
            return
        if message.type == "task_submission":
            async for msg in self._handle_task_submission_stream(session, state, message):
                yield msg
            return
        if message.type == "follow_up_action":
            async for msg in self._handle_follow_up_stream(session, state, message):
                yield msg
            return
        yield WSOutgoingMessage(
            type="error",
            content=f"Unknown message type: {message.type!r}",
        )

    # ------------------------------------------------------------------
    # Per-message handlers
    # ------------------------------------------------------------------

    async def _handle_user_message_stream(
        self,
        session: LearningSession,
        state: LearningSessionState,
        message: WSIncomingMessage,
    ) -> AsyncIterator[WSOutgoingMessage]:
        text = message.content or ""
        messages = list(state.get("messages", []))
        messages.append({"role": "user", "content": text, "type": "chat"})
        state["messages"] = messages
        session.messages = messages

        if state.get("phase") in ("teaching", None):
            previous_tutor_message = _last_tutor_message(messages[:-1])
            confirmed = _looks_like_understanding(
                text, previous_tutor_message=previous_tutor_message,
            )
            session.understanding_confirmed = (
                session.understanding_confirmed or confirmed
            )
            state["understanding_confirmed"] = session.understanding_confirmed

            if confirmed:
                # Pull the next pending V2 attempt and deliver it.
                attempt = self._next_pending_attempt(session)
                if attempt is None:
                    # No activities left — gently nudge to complete.
                    async for msg in self._complete_and_announce(session, state):
                        yield msg
                    return
                state["task_content"] = dict(attempt.task_content or {})
                state["task_type"] = self._task_type_for_attempt(attempt)
                state["current_sequence"] = attempt.sequence
                state["current_task_index"] = attempt.sequence - 1
                session.pre_generated_tasks = state["task_content"]
                session.task_type = state["task_type"]
                session.current_task_index = state["current_task_index"]

                update = await task_delivery_node(state)
                self._apply_update(session, update)
                self.db.commit()
                async for msg in self._stream_outgoing_events(
                    update.get("outgoing_events", [])
                ):
                    yield msg
            else:
                async for msg in self._stream_teaching_turn(session, state):
                    yield msg
            return

        if state.get("phase") in ("feedback", "follow_up", "scorecard"):
            async for msg in self._stream_followup_response(session, state, text):
                yield msg
            return

        # practice_task / ended — nudge.
        nudge = (
            "Submit your answers using the task above when you're ready."
            if state.get("phase") == "practice_task"
            else "This session has ended. Start a new one from the dashboard."
        )
        messages.append({"role": "ai", "content": nudge, "type": "chat"})
        session.messages = messages
        self.session_repo.save(session)
        self.db.commit()
        async for msg in self._stream_chat_text(nudge):
            yield msg

    async def _handle_task_submission_stream(
        self,
        session: LearningSession,
        state: LearningSessionState,
        message: WSIncomingMessage,
    ) -> AsyncIterator[WSOutgoingMessage]:
        answers = message.answers or {}
        session.user_submission = answers
        state["user_submission"] = answers

        sequence = state.get("current_sequence")
        if sequence is None:
            attempt = self._next_pending_attempt(session)
            if attempt is None:
                async for msg in self._complete_and_announce(session, state):
                    yield msg
                return
            sequence = attempt.sequence
            state["current_sequence"] = sequence

        v2_service = _make_v2_session_service(self.db)
        daily = self.db.get(DailySession, session.daily_session_id)
        if daily is None:
            yield WSOutgoingMessage(
                type="error",
                content="Linked daily session is missing.",
            )
            return

        try:
            attempt, evaluation, feedback = await v2_service.submit_activity(
                session_id=daily.session_id,
                user_id=session.user_id,
                sequence=int(sequence),
                user_response=answers,
            )
        except AttemptAlreadySubmitted:
            yield WSOutgoingMessage(
                type="error",
                content="This activity was already submitted.",
            )
            return
        except (AttemptNotFound, SessionNotFound) as exc:
            yield WSOutgoingMessage(type="error", content=str(exc))
            return

        evaluation_dict = {
            "raw_score": float(evaluation.raw_score),
            "rubric_scores": dict(evaluation.rubric_scores or {}),
            "base_reward": evaluation.base_reward,
            "weighted_points": dict(evaluation.weighted_points or {}),
            "evaluator_notes": evaluation.evaluator_notes,
        }
        feedback_dict = {
            "score": feedback.score,
            "summary": feedback.summary,
            "did_well": list(feedback.did_well or []),
            "mistakes": list(feedback.mistakes or []),
            "next_tip": feedback.next_tip,
            "sub_skill_breakdown": dict(feedback.sub_skill_breakdown or {}),
        }

        # Emit the scorecard widget.
        scorecard_payload = {
            "overall_score": feedback.score,
            "skill_name": session.skill_name,
            "topic": session.topic,
            "rubric_scores": evaluation_dict["rubric_scores"],
            "weighted_points": evaluation_dict["weighted_points"],
            "_session": {
                "current_task_index": int(state.get("current_task_index") or 0),
                "total_tasks": len(session.task_queue or []) or 1,
                "sequence": int(sequence),
            },
        }
        yield WSOutgoingMessage(
            type="ui_event", widget="scorecard", payload=scorecard_payload,
        )

        # Emit the feedback card.
        feedback_payload = {
            **feedback_dict,
            "_session": scorecard_payload["_session"],
        }
        yield WSOutgoingMessage(
            type="ui_event", widget="feedback_card", payload=feedback_payload,
        )

        # Stream the conversational feedback summary as a chat message.
        summary_text = feedback.summary or "Good effort."
        if feedback.next_tip:
            summary_text = f"{summary_text} {feedback.next_tip}"
        actions = self._next_actions_for_session(session)
        async for msg in self._stream_chat_text(summary_text, actions=actions):
            yield msg

        session.evaluation = evaluation_dict
        session.feedback = feedback_dict
        session.phase = "feedback"
        messages = list(session.messages or [])
        messages.append({"role": "ai", "content": "[scorecard delivered]", "type": "ui_event"})
        messages.append({"role": "ai", "content": "[feedback card delivered]", "type": "ui_event"})
        messages.append({"role": "ai", "content": summary_text, "type": "chat"})
        session.messages = messages
        self.session_repo.save(session)
        self.db.commit()

    async def _handle_follow_up_stream(
        self,
        session: LearningSession,
        state: LearningSessionState,
        message: WSIncomingMessage,
    ) -> AsyncIterator[WSOutgoingMessage]:
        action_text = message.action or message.content or ""
        messages = list(state.get("messages", []))
        messages.append({"role": "user", "content": action_text, "type": "chat"})
        state["messages"] = messages
        session.messages = messages

        async for msg in self._stream_followup_response(session, state, action_text):
            yield msg

    async def _stream_followup_response(
        self,
        session: LearningSession,
        state: LearningSessionState,
        raw_action: str,
    ) -> AsyncIterator[WSOutgoingMessage]:
        messages = list(state.get("messages", []))
        action = raw_action.strip().lower()

        end_signals = (
            "go to dashboard", "end session", "end", "stop", "bye", "goodbye",
        )
        another_signals = (
            "next activity", "try another task", "another task",
            "next task", "more",
        )
        question_signals = ("ask a question", "question", "doubt", "clarif")

        if any(sig in action for sig in end_signals):
            async for msg in self._complete_and_announce(session, state):
                yield msg
            return

        if any(sig in action for sig in another_signals):
            attempt = self._next_pending_attempt(session)
            if attempt is None:
                async for msg in self._complete_and_announce(session, state):
                    yield msg
                return
            state["task_content"] = dict(attempt.task_content or {})
            state["task_type"] = self._task_type_for_attempt(attempt)
            state["current_sequence"] = attempt.sequence
            state["current_task_index"] = attempt.sequence - 1
            state["phase"] = "practice_task"
            session.pre_generated_tasks = state["task_content"]
            session.task_type = state["task_type"]
            session.current_task_index = state["current_task_index"]
            session.user_submission = None
            session.evaluation = None
            session.feedback = None
            session.phase = "practice_task"

            update = await task_delivery_node(state)
            self._apply_update(session, update)
            self.db.commit()
            async for msg in self._stream_outgoing_events(
                update.get("outgoing_events", [])
            ):
                yield msg
            return

        if action in question_signals or action == "ask a question":
            prompt_msg = "Sure — what would you like to know?"
            messages.append({"role": "ai", "content": prompt_msg, "type": "chat"})
            self._apply_update(
                session,
                {"phase": "follow_up", "messages": messages},
            )
            self.db.commit()
            async for msg in self._stream_chat_text(prompt_msg):
                yield msg
            return

        async for msg in self._stream_followup_answer(session, state, raw_action):
            yield msg

    async def _complete_and_announce(
        self,
        session: LearningSession,
        state: LearningSessionState,
    ) -> AsyncIterator[WSOutgoingMessage]:
        """End the chat and complete the V2 DailySession if not yet completed."""
        daily = self.db.get(DailySession, session.daily_session_id)
        if daily is not None and daily.status is SessionStatus.IN_PROGRESS:
            # If at least one attempt is evaluated, complete; otherwise leave open.
            attempts = self.attempts_repo.list_for_session(daily.id)
            evaluated = [a for a in attempts if a.status is AttemptStatus.EVALUATED]
            if evaluated:
                try:
                    v2_service = _make_v2_session_service(self.db)
                    await v2_service.complete_session(
                        session_id=daily.session_id, user_id=session.user_id,
                    )
                except (SessionNotFound, SessionAbandoned, SessionAlreadyCompleted):
                    pass

        farewell = (
            "Great work. Go back to the dashboard to review today's "
            "activities and advance when you're ready."
        )
        messages = list(session.messages or [])
        messages.append({"role": "ai", "content": farewell, "type": "chat"})
        session.messages = messages
        session.phase = "ended"
        self.session_repo.save(session)
        self.db.commit()

        async for msg in self._stream_chat_text(
            farewell, actions=["Go to dashboard"],
        ):
            yield msg

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def _profile_context(self, user_id: int) -> dict[str, Any]:
        profile = self.profile_repo.get_by_user_id(user_id)
        if profile is None:
            return {
                "interests": "",
                "primary_goals": "",
                "personalisation_context": "",
                "self_assessed_level": "beginner",
                "structured_personalisation": None,
            }
        return {
            "interests": profile.interests.strip() if profile.interests else "",
            "primary_goals": (
                profile.primary_goals.strip() if profile.primary_goals else ""
            ),
            "personalisation_context": (
                profile.personalisation_context.strip()
                if profile.personalisation_context
                else ""
            ),
            "self_assessed_level": (
                profile.self_assessed_level.value
                if profile.self_assessed_level
                else "beginner"
            ),
            "structured_personalisation": profile.structured_personalisation,
        }

    def _enrich_state_with_profile(
        self, state: LearningSessionState, user_id: int,
    ) -> None:
        state["learner_profile"] = self._profile_context(user_id)

    def _load_session(self, session_id: str) -> LearningSession:
        session = self.session_repo.get_by_session_id(session_id)
        if session is None:
            raise LookupError(f"No learning_session with id={session_id!r}")
        return session

    def _state_from_row(self, session: LearningSession) -> LearningSessionState:
        daily = self.db.get(DailySession, session.daily_session_id)
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "daily_session_id": session.daily_session_id,
            "daily_session_uuid": daily.session_id if daily is not None else None,
            "task_queue": list(session.task_queue or []),
            "current_task_index": session.current_task_index,
            "phase": session.phase,
            "messages": list(session.messages or []),
            "topic": session.topic,
            "skill_name": session.skill_name,
            "activity_type": session.activity_type,
            "user_level": session.user_level,
            "task_content": session.pre_generated_tasks,
            "task_type": session.task_type,
            "user_submission": session.user_submission,
            "evaluation": session.evaluation,
            "feedback": session.feedback,
            "understanding_confirmed": session.understanding_confirmed,
            "current_activity_order": int(
                getattr(session, "current_activity_order", None) or 1
            ),
            "outgoing_events": [],
            "daily_plan": (
                {"teacher_instructions": session.teacher_instructions}
                if session.teacher_instructions
                else None
            ),
        }

    def _apply_update(
        self, session: LearningSession, update: dict[str, Any],
    ) -> None:
        if "phase" in update:
            session.phase = update["phase"]
        if "messages" in update:
            session.messages = update["messages"]
        if "evaluation" in update:
            session.evaluation = update["evaluation"]
        if "feedback" in update:
            session.feedback = update["feedback"]
        if "task_content" in update:
            session.pre_generated_tasks = update["task_content"] or {}
        if "task_queue" in update:
            session.task_queue = update["task_queue"] or []
        if "task_type" in update:
            session.task_type = str(update["task_type"] or session.task_type)
        if "current_task_index" in update:
            session.current_task_index = int(update["current_task_index"] or 0)
        if "user_submission" in update:
            session.user_submission = update["user_submission"]
        if "understanding_confirmed" in update:
            session.understanding_confirmed = bool(update["understanding_confirmed"])
        if "current_activity_order" in update:
            value = update["current_activity_order"]
            if value is not None:
                session.current_activity_order = int(value)
        self.session_repo.save(session)

    def _next_pending_attempt(
        self, session: LearningSession,
    ) -> ActivityAttempt | None:
        return self.attempts_repo.first_pending(session.daily_session_id)

    @staticmethod
    def _task_type_for_attempt(attempt: ActivityAttempt) -> str:
        content = attempt.task_content or {}
        return str(content.get("ui_widget") or content.get("widget") or "")

    def _next_actions_for_session(self, session: LearningSession) -> list[str]:
        next_attempt = self._next_pending_attempt(session)
        if next_attempt is None:
            return ["Go to dashboard"]
        return ["Next activity", "Go to dashboard"]

    @staticmethod
    def _post_feedback_actions(session: LearningSession) -> list[str]:
        queue = list(session.task_queue or [])
        has_next = any(
            item.get("status") not in ("evaluated", "submitted")
            for item in queue
        )
        if has_next:
            return ["Next activity", "Go to dashboard"]
        return ["Go to dashboard"]

    # ------------------------------------------------------------------
    # Streaming primitives
    # ------------------------------------------------------------------

    @staticmethod
    def _split_text_chunks(text: str) -> list[str]:
        return re.findall(r"\S+\s*", text) or ([text] if text else [])

    async def _stream_chat_text(
        self,
        text: str,
        *,
        actions: list[str] | None = None,
        role: str = "assistant",
        stream_id: str | None = None,
    ) -> AsyncIterator[WSOutgoingMessage]:
        sid = stream_id or uuid.uuid4().hex
        yield WSOutgoingMessage(
            type="chat_stream_start", role=role, stream_id=sid,
        )
        for chunk in self._split_text_chunks(text):
            yield WSOutgoingMessage(
                type="chat_stream_delta", role=role,
                stream_id=sid, content=chunk,
            )
        yield WSOutgoingMessage(
            type="chat_stream_end", role=role, stream_id=sid,
            content=text, actions=actions,
        )

    async def _stream_outgoing_events(
        self, events: list[dict],
    ) -> AsyncIterator[WSOutgoingMessage]:
        for event in events:
            if event.get("type") == "chat_message":
                async for msg in self._stream_chat_text(
                    str(event.get("content") or ""),
                    actions=event.get("actions"),
                    role=str(event.get("role") or "assistant"),
                ):
                    yield msg
            else:
                yield WSOutgoingMessage(**event)

    @staticmethod
    async def _timed_chunks(
        source: AsyncIterator[str],
        *,
        first_chunk_timeout_s: float,
        chunk_timeout_s: float,
        timeout_message: str,
    ) -> AsyncIterator[str]:
        timeout = first_chunk_timeout_s
        try:
            while True:
                try:
                    chunk = await asyncio.wait_for(anext(source), timeout=timeout)
                except StopAsyncIteration:
                    break
                except TimeoutError:
                    logger.warning(timeout_message)
                    break
                timeout = chunk_timeout_s
                yield chunk
        finally:
            aclose = getattr(source, "aclose", None)
            if aclose is not None:
                await aclose()

    async def _stream_teaching_turn(
        self,
        session: LearningSession,
        state: LearningSessionState,
    ) -> AsyncIterator[WSOutgoingMessage]:
        stream_id = uuid.uuid4().hex
        yield WSOutgoingMessage(
            type="chat_stream_start", role="assistant", stream_id=stream_id,
        )

        chunks: list[str] = []
        try:
            daily_plan = state.get("daily_plan") or {}
            teacher_instructions = (
                daily_plan.get("teacher_instructions") if daily_plan else None
            )
            teaching_chunks = stream_teaching_turn(
                topic=state.get("topic") or "today's English topic",
                sub_skill=state.get("skill_name") or "grammar",
                task_type=state.get("task_type") or "fill_in_blanks",
                user_level=int(state.get("user_level", 5)),
                learner_profile=state.get("learner_profile") or {},
                conversation=list(state.get("messages", [])),
                teacher_instructions=teacher_instructions,
            )
            async for chunk in self._timed_chunks(
                teaching_chunks,
                first_chunk_timeout_s=_TEACHING_STREAM_FIRST_CHUNK_TIMEOUT_S,
                chunk_timeout_s=_TEACHING_STREAM_CHUNK_TIMEOUT_S,
                timeout_message="teaching turn streaming timed out",
            ):
                if not chunk:
                    continue
                chunks.append(chunk)
                yield WSOutgoingMessage(
                    type="chat_stream_delta", role="assistant",
                    stream_id=stream_id, content=chunk,
                )
        except Exception:
            logger.exception("teaching turn streaming failed; using fallback")

        content = "".join(chunks).strip()
        if not content:
            fallback = (
                f"Today we are learning {state.get('topic') or 'this topic'}. "
                "I will guide you through a quick concept check, then we will "
                "do a short practice. Say 'ready' when you want to begin."
            )
            for chunk in self._split_text_chunks(fallback):
                yield WSOutgoingMessage(
                    type="chat_stream_delta", role="assistant",
                    stream_id=stream_id, content=chunk,
                )
            content = fallback

        new_messages = list(state.get("messages", []))
        new_messages.append({"role": "ai", "content": content, "type": "chat"})
        self._apply_update(
            session, {"phase": "teaching", "messages": new_messages},
        )
        self.db.commit()

        yield WSOutgoingMessage(
            type="chat_stream_end", role="assistant",
            stream_id=stream_id, content=content,
        )

    async def _stream_followup_answer(
        self,
        session: LearningSession,
        state: LearningSessionState,
        question: str,
    ) -> AsyncIterator[WSOutgoingMessage]:
        stream_id = uuid.uuid4().hex
        yield WSOutgoingMessage(
            type="chat_stream_start", role="assistant", stream_id=stream_id,
        )

        chunks: list[str] = []
        answer_chunks = stream_answer_question(state, question)
        async for chunk in self._timed_chunks(
            answer_chunks,
            first_chunk_timeout_s=_FOLLOWUP_STREAM_FIRST_CHUNK_TIMEOUT_S,
            chunk_timeout_s=_FOLLOWUP_STREAM_CHUNK_TIMEOUT_S,
            timeout_message="follow-up answer streaming timed out",
        ):
            if chunk:
                chunks.append(chunk)
                yield WSOutgoingMessage(
                    type="chat_stream_delta", role="assistant",
                    stream_id=stream_id, content=chunk,
                )

        content = "".join(chunks).strip()
        if not content:
            content = "Sure — what would you like to know?"
            for chunk in self._split_text_chunks(content):
                yield WSOutgoingMessage(
                    type="chat_stream_delta", role="assistant",
                    stream_id=stream_id, content=chunk,
                )

        messages = list(state.get("messages", []))
        messages.append({"role": "ai", "content": content, "type": "chat"})
        self._apply_update(
            session, {"phase": "follow_up", "messages": messages},
        )
        self.db.commit()

        yield WSOutgoingMessage(
            type="chat_stream_end", role="assistant",
            stream_id=stream_id, content=content,
        )


def _make_v2_session_service(db: Session) -> SessionService:
    """Construct the production-wired V2 SessionService.

    Mirrors `app.modules.sessions.routes._make_session_service` so the
    chat layer talks to the same LLM-wired evaluator/feedback/task
    generator the REST shell uses.
    """
    from app.ai.sessions import build_default_agents

    evaluator, feedback_generator, task_generator = build_default_agents()
    return SessionService(
        db,
        evaluator=evaluator,
        feedback_generator=feedback_generator,
        task_generator=task_generator,
    )
