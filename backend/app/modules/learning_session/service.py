"""DEPRECATED — Phase 7. Use `app.modules.sessions.service.SessionService`.

The new sessions flow (`/api/sessions/*`) supersedes this module. Routes
here remain mounted as a rollback path for the legacy /task/chat UI;
Phase 8 cleanup removes both the routes and this module.

Business logic for chat-driven learning sessions.

The service has two surfaces:

  1. ``create_session`` — runs the rotation engine, generates a task with
     the LLM, persists a LearningSession row, and returns the session id
     the frontend will use to open a WebSocket.

  2. ``process_message`` — the WebSocket message handler. Loads the
     persisted state, runs exactly the right LangGraph node based on
     phase + incoming message type, and persists the result.

The graph itself (`get_learning_session_graph()`) is built so it can be
exercised end-to-end in tests, but for chat we step through it node by
node — each user/network round trip advances one phase.
"""

from __future__ import annotations

import logging
import re
import uuid
import asyncio
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.orm import Session

from app.ai.agents.teacher import stream_teaching_turn
from app.ai.agents.task_generator import TaskGeneratorAgent
from app.ai.graphs.nodes import (
    evaluation_node,
    feedback_node,
    followup_node,
    plan_loader_node,
    stream_answer_question,
    task_delivery_node,
    teach_node,
)
from app.ai.graphs.state import LearningSessionState
from app.modules.curriculum.exceptions import (
    EnrollmentNotActive,
    NotEnrolled,
)
from app.modules.curriculum.models import EnrollmentStatus, UserEnrollment
from app.modules.curriculum.repository import (
    DailyPlanRepository,
    EnrollmentSkillHistoryRepository,
    UserEnrollmentRepository,
)
from app.modules.curriculum.rotation import RotationEngine
from app.modules.curriculum.topics import CourseTopic, get_course_topic
from app.modules.auth.repository import UserProfileRepository
from app.modules.learning_session.models import LearningSession
from app.modules.learning_session.repository import LearningSessionRepository
from app.modules.learning_session.schemas import (
    StartSessionResponse,
    WSIncomingMessage,
    WSOutgoingMessage,
)
from app.modules.skills.repository import SkillRepository, UserSkillScoreRepository
from app.modules.tasks.models import TaskType
from app.modules.tasks.models import UserTaskStatus
from app.modules.tasks.repository import UserTaskRepository
from app.modules.tasks.service import TaskService
from app.tasks.schemas import ALL_TEMPLATES, get_templates_for
from app.tasks.schemas.base import Activity, SubSkill, TaskTemplate

logger = logging.getLogger(__name__)


# Fallback template used only when a planned sub-skill/activity has no
# matching template.
_DEFAULT_TEMPLATE_ID = "grammar_read_fill_blanks_v1"

_TASK_TYPE_TO_ACTIVITY = {
    "reading": Activity.READ,
    "writing": Activity.WRITE,
    "listening": Activity.LISTEN,
    "speaking": Activity.SPEAK,
}

_SKILL_NAME_TO_SUBSKILL = {
    "grammar": SubSkill.GRAMMAR,
    "vocabulary": SubSkill.VOCABULARY,
    "pronunciation": SubSkill.PRONUNCIATION,
    "fluency": SubSkill.FLUENCY,
    "expression": SubSkill.THOUGHT_ORGANIZATION,
    "comprehension": SubSkill.LISTENING,
    "tone": SubSkill.TONE,
}


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

_DOUBT_CLARIFIED_PATTERNS = (
    re.compile(r"\b(did|does)\s+(that|this|it)\s+(answer|clarify|clear)\b"),
    re.compile(r"\b(is|was)\s+(that|this|it|your doubt)\s+(clear|clarified)\b"),
    re.compile(r"\b(is|was)\s+your\s+doubt\s+(clear|clarified)\b"),
    re.compile(r"\bdo\s+you\s+understand\s+(now|that|this|it)?\b"),
)

_TEACHING_STREAM_FIRST_CHUNK_TIMEOUT_S = 8.0
_TEACHING_STREAM_CHUNK_TIMEOUT_S = 20.0
_FOLLOWUP_STREAM_FIRST_CHUNK_TIMEOUT_S = 8.0
_FOLLOWUP_STREAM_CHUNK_TIMEOUT_S = 20.0


class LearningSessionTaskUnavailable(Exception):
    """Raised when a requested dashboard task cannot start a chat session."""


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


def _tutor_asked_doubt_clarified(text: str) -> bool:
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return False
    return any(pattern.search(cleaned) for pattern in _DOUBT_CLARIFIED_PATTERNS)


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


def _learner_turn_count(messages: list[dict]) -> int:
    return sum(1 for message in messages if message.get("role") == "user")


def _readiness_turn_threshold(topic: str) -> int:
    normalized = (topic or "").lower()
    if "present simple" in normalized or "simple present" in normalized:
        return 4
    return 3


def _needs_clarification(text: str) -> bool:
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return False
    if any(pattern.search(cleaned) for pattern in _NON_UNDERSTANDING_PATTERNS):
        return True
    return "?" in cleaned and _QUESTION_START_PATTERN.search(cleaned) is not None


class LearningSessionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.enrollment_repo = UserEnrollmentRepository(db)
        self.history_repo = EnrollmentSkillHistoryRepository(db)
        self.daily_plan_repo = DailyPlanRepository(db)
        self.skill_repo = SkillRepository(db)
        self.score_repo = UserSkillScoreRepository(db)
        self.session_repo = LearningSessionRepository(db)
        self.user_task_repo = UserTaskRepository(db)
        self.rotation = RotationEngine()
        self.generator = TaskGeneratorAgent()

    # ------------------------------------------------------------------
    # Session creation
    # ------------------------------------------------------------------
    async def create_session(
        self,
        *,
        user_id: int,
        user_task_id: int | None = None,
    ) -> StartSessionResponse:
        enrollment = self._load_enrollment(user_id)
        bundle = await TaskService(self.db).get_or_create_day_bundle_async(
            user_id=user_id,
        )
        if not bundle:
            raise LearningSessionTaskUnavailable(
                "No daily activities are available for the current enrollment day"
            )
        return self._create_or_resume_daily_session(
            user_id=user_id,
            enrollment=enrollment,
            bundle=bundle,
            requested_user_task_id=user_task_id,
        )

    def _create_or_resume_daily_session(
        self,
        *,
        user_id: int,
        enrollment: UserEnrollment,
        bundle: list,
        requested_user_task_id: int | None,
    ) -> StartSessionResponse:
        if requested_user_task_id is not None:
            matching = next(
                (task for task in bundle if task.id == requested_user_task_id),
                None,
            )
            if matching is None:
                raise LearningSessionTaskUnavailable(
                    f"UserTask {requested_user_task_id} is not part of the current day bundle"
                )
            if matching.user_id != user_id:
                raise PermissionError(
                    f"User {user_id} cannot start UserTask {requested_user_task_id}"
                )

        active_index = self._resolve_active_queue_index(
            bundle=bundle,
            requested_user_task_id=requested_user_task_id,
        )
        active_user_task = bundle[active_index]
        existing = self._find_daily_session(enrollment=enrollment, bundle=bundle)

        if existing is not None:
            existing.task_queue = self._queue_from_bundle(bundle)
            active_changed = existing.user_task_id != active_user_task.id
            if active_changed:
                self._apply_active_user_task(
                    existing,
                    active_user_task,
                    active_index,
                    reset_result_state=True,
                )
                existing.phase = (
                    "ended"
                    if self._all_queue_tasks_complete(existing)
                    else "practice_task"
                )
            elif not existing.task_queue:
                existing.task_queue = self._queue_from_bundle(bundle)

            self.session_repo.save(existing)
            self.db.commit()
            return StartSessionResponse(
                session_id=existing.session_id,
                topic=existing.topic,
                skill_name=existing.skill_name,
                task_type=existing.task_type,
                user_task_id=existing.user_task_id,
                message="Session resumed",
            )

        session_id = uuid.uuid4().hex
        active_content = dict(active_user_task.task.content or {})
        session = self.session_repo.create(
            session_id=session_id,
            user_id=user_id,
            enrollment_id=enrollment.id,
            user_task_id=active_user_task.id,
            topic=self._topic_for_user_task(active_user_task),
            skill_name=self._skill_name_for_user_task(active_user_task),
            activity_type=self._activity_type_for_user_task(active_user_task),
            task_type=active_user_task.task.task_type.value,
            user_level=int(
                active_content.get("sub_level")
                or active_user_task.task.difficulty
                or 5
            ),
            pre_generated_tasks=active_content,
            task_queue=self._queue_from_bundle(bundle),
        )
        session.current_task_index = active_index
        if active_user_task.status == UserTaskStatus.PENDING:
            active_user_task.status = UserTaskStatus.IN_PROGRESS
        self.session_repo.save(session)
        self.db.commit()

        return StartSessionResponse(
            session_id=session_id,
            topic=session.topic,
            skill_name=session.skill_name,
            task_type=session.task_type,
            user_task_id=active_user_task.id,
            message="Session ready",
        )

    def restart_session(
        self,
        *,
        session_id: str,
        user_id: int,
    ) -> StartSessionResponse:
        """Restart the active chat loop without undoing dashboard progress."""
        session = self._load_session(session_id)
        if session.user_id != user_id:
            raise PermissionError(
                f"User {user_id} cannot restart session {session_id}"
            )

        self._refresh_queue_statuses(session)

        if self._all_queue_tasks_complete(session):
            session.phase = "ended"
            self.session_repo.save(session)
            self.db.commit()
            return StartSessionResponse(
                session_id=session.session_id,
                topic=session.topic,
                skill_name=session.skill_name,
                task_type=session.task_type,
                user_task_id=session.user_task_id,
                message="Session complete",
            )

        queue = sorted(
            list(session.task_queue or []),
            key=lambda item: int(item.get("sequence_index") or 0),
        )
        first_incomplete = next(
            (
                item
                for item in queue
                if item.get("status") != UserTaskStatus.COMPLETED.value
            ),
            None,
        )

        if first_incomplete is not None:
            user_task_id = first_incomplete.get("user_task_id")
            user_task = (
                self.user_task_repo.get_by_id(int(user_task_id))
                if user_task_id is not None
                else None
            )
            if user_task is None:
                raise LookupError(
                    f"UserTask {user_task_id} does not exist for session restart"
                )
            next_index = int(first_incomplete.get("sequence_index") or 0)
            self._apply_active_user_task(
                session,
                user_task,
                next_index,
                reset_result_state=True,
            )
            session.current_activity_order = next_index + 1
            self._refresh_queue_statuses(session)

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
            topic=session.topic,
            skill_name=session.skill_name,
            task_type=session.task_type,
            user_task_id=session.user_task_id,
            message="Session restarted",
        )

    async def _create_session_from_user_task(
        self,
        *,
        user_id: int,
        enrollment: UserEnrollment,
        user_task_id: int,
    ) -> StartSessionResponse:
        user_task = self.user_task_repo.get_by_id(user_task_id)
        if user_task is None:
            raise LookupError(f"UserTask {user_task_id} does not exist")
        if user_task.user_id != user_id:
            raise PermissionError(
                f"User {user_id} cannot start UserTask {user_task_id}"
            )
        if user_task.enrollment_id not in (None, enrollment.id):
            raise LearningSessionTaskUnavailable(
                f"UserTask {user_task_id} is not part of the active enrollment"
            )
        if user_task.status in (UserTaskStatus.COMPLETED, UserTaskStatus.SKIPPED):
            raise LearningSessionTaskUnavailable(
                f"UserTask {user_task_id} is already {user_task.status.value}"
            )

        # Auto-resume: if an active (not yet fully completed) session exists
        # for this task, return it instead of creating a new one.
        existing = (
            self.db.query(LearningSession)
            .filter(
                LearningSession.user_task_id == user_task_id,
                LearningSession.user_id == user_id,
                LearningSession.feedback.is_(None),
            )
            .order_by(LearningSession.id.desc())
            .first()
        )
        if existing is not None:
            return StartSessionResponse(
                session_id=existing.session_id,
                topic=existing.topic,
                skill_name=existing.skill_name,
                task_type=existing.task_type,
                user_task_id=user_task_id,
                message="Session resumed",
            )

        task = user_task.task
        task_content = dict(task.content or {})
        topic = (
            task_content.get("topic_name")
            or task_content.get("topic")
            or task.title
        )
        skill_name = str(task_content.get("sub_skill") or "").strip()
        activity_type = str(task_content.get("activity") or "").strip()

        if not skill_name and task.task_skills:
            linked_skill = task.task_skills[0].skill
            skill_name = linked_skill.name if linked_skill else ""
        if not activity_type:
            activity_type = task.task_type.value

        session_id = uuid.uuid4().hex
        self.session_repo.create(
            session_id=session_id,
            user_id=user_id,
            enrollment_id=enrollment.id,
            user_task_id=user_task.id,
            topic=str(topic),
            skill_name=skill_name or "grammar",
            activity_type=activity_type,
            task_type=task.task_type.value,
            user_level=int(task_content.get("sub_level") or task.difficulty or 5),
            pre_generated_tasks=task_content,
        )

        if user_task.status == UserTaskStatus.PENDING:
            user_task.status = UserTaskStatus.IN_PROGRESS

        self.db.commit()

        return StartSessionResponse(
            session_id=session_id,
            topic=str(topic),
            skill_name=skill_name or "grammar",
            task_type=task.task_type.value,
            user_task_id=user_task.id,
            message="Session ready",
        )

    # ------------------------------------------------------------------
    # WebSocket message handling
    # ------------------------------------------------------------------
    async def initial_messages(
        self, session_id: str
    ) -> list[WSOutgoingMessage]:
        """Run the teach_node once when the WebSocket first connects."""
        session = self._load_session(session_id)
        state = self._state_from_row(session)
        self._enrich_state_with_profile(state, session.user_id)
        await self._ensure_daily_plan_in_state(state, session=session)
        update = await teach_node(state)
        self._apply_update(session, update)
        self.db.commit()
        return self._render_outgoing(update.get("outgoing_events", []))

    async def initial_messages_stream(
        self, session_id: str
    ) -> AsyncIterator[WSOutgoingMessage]:
        """Stream the first teaching turn when the WebSocket connects."""
        session = self._load_session(session_id)
        state = self._state_from_row(session)
        self._enrich_state_with_profile(state, session.user_id)
        await self._ensure_daily_plan_in_state(state, session=session)
        async for msg in self._stream_teaching_turn(session, state):
            yield msg

    async def _ensure_daily_plan_in_state(
        self,
        state: LearningSessionState,
        session: LearningSession | None = None,
    ) -> None:
        """Run the plan_loader node, merge the result into state, and
        persist `current_activity_order` onto the session row when one is
        supplied. Best-effort — agents have fallbacks when the plan is None.
        """
        try:
            update = await plan_loader_node(state, db=self.db)
        except Exception:
            logger.exception(
                "plan_loader_node failed; continuing without a daily plan"
            )
            return
        for key, value in update.items():
            state[key] = value  # type: ignore[literal-required]
        if session is not None and "current_activity_order" in update:
            value = update["current_activity_order"]
            if value is not None:
                session.current_activity_order = int(value)
                self.session_repo.save(session)
        self.db.commit()

    async def resume_messages_stream(
        self, session_id: str
    ) -> AsyncIterator[WSOutgoingMessage]:
        """Send enough state for a previously-started daily chat to continue."""
        session = self._load_session(session_id)
        self._refresh_queue_statuses(session)
        state = self._state_from_row(session)
        self._enrich_state_with_profile(state, session.user_id)
        total = len(session.task_queue or []) or 1
        current = int(session.current_task_index or 0)

        if self._all_queue_tasks_complete(session):
            message = (
                "Today's activities are complete. Go back to the dashboard "
                "to review the day and advance when you're ready."
            )
            async for msg in self._stream_chat_text(
                message,
                actions=["Go to dashboard"],
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
                type="chat_message",
                role="assistant",
                content=message,
            )
            payload = {
                **(session.pre_generated_tasks or {}),
                "_session": {
                    "current_task_index": current,
                    "total_tasks": total,
                    "user_task_id": session.user_task_id,
                },
            }
            yield WSOutgoingMessage(
                type="ui_event",
                widget=payload.get("widget") or session.task_type,
                payload=payload,
            )
            return

        if session.phase in ("feedback", "scorecard", "follow_up"):
            message = "Ready for the next step?"
            async for msg in self._stream_chat_text(
                message,
                actions=self._post_feedback_actions(state),
            ):
                yield msg
            return

        if session.phase == "ended":
            message = "This chat is finished. Go back to the dashboard when you're ready."
            async for msg in self._stream_chat_text(
                message,
                actions=["Go to dashboard"],
            ):
                yield msg

    async def process_message(
        self, session_id: str, message: WSIncomingMessage
    ) -> list[WSOutgoingMessage]:
        session = self._load_session(session_id)
        state = self._state_from_row(session)
        self._enrich_state_with_profile(state, session.user_id)

        if message.type == "user_message":
            return await self._handle_user_message(session, state, message)
        if message.type == "task_submission":
            return await self._handle_task_submission(session, state, message)
        if message.type == "follow_up_action":
            return await self._handle_follow_up(session, state, message)
        return [
            WSOutgoingMessage(
                type="error",
                content=f"Unknown message type: {message.type!r}",
            )
        ]

    async def process_message_stream(
        self, session_id: str, message: WSIncomingMessage
    ) -> AsyncIterator[WSOutgoingMessage]:
        session = self._load_session(session_id)
        state = self._state_from_row(session)
        self._enrich_state_with_profile(state, session.user_id)

        if message.type == "user_message":
            async for msg in self._handle_user_message_stream(
                session, state, message
            ):
                yield msg
            return
        if message.type == "task_submission":
            async for msg in self._handle_task_submission_stream(
                session, state, message
            ):
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
    # Helpers — state + DB plumbing
    # ------------------------------------------------------------------
    def _load_enrollment(self, user_id: int) -> UserEnrollment:
        enrollment = self.enrollment_repo.get_for_user(user_id)
        if enrollment is None:
            raise NotEnrolled(f"User {user_id} is not enrolled in any course")
        if enrollment.status != EnrollmentStatus.ACTIVE:
            raise EnrollmentNotActive(
                f"Enrollment {enrollment.id} status is {enrollment.status.value}"
            )
        return enrollment

    def _decide_plan(self, enrollment: UserEnrollment):
        skill_name_to_id = self.skill_repo.name_to_id_map()
        history_rows = self.history_repo.list_for_enrollment(enrollment.id)
        history_by_skill_id: dict[int, TaskType | None] = {
            row.skill_id: row.last_activity_type for row in history_rows
        }
        return self.rotation.decide(
            week_number=enrollment.current_week,
            day_in_week=enrollment.current_day_in_week,
            skill_name_to_id=skill_name_to_id,
            history_by_skill_id=history_by_skill_id,
            allowed_activity_types=self._allowed_activities(enrollment),
        )

    @staticmethod
    def _allowed_activities(enrollment: UserEnrollment) -> set[TaskType]:
        allowed: set[TaskType] = set()
        if enrollment.allow_reading:
            allowed.add(TaskType.READING)
        if enrollment.allow_writing:
            allowed.add(TaskType.WRITING)
        if enrollment.allow_listening:
            allowed.add(TaskType.LISTENING)
        if enrollment.allow_speaking:
            allowed.add(TaskType.SPEAKING)
        return allowed

    @staticmethod
    def _pick_template(*, plan, user_level: int):
        sub_skill = _SKILL_NAME_TO_SUBSKILL.get(plan.skill_name)
        activity = _TASK_TYPE_TO_ACTIVITY.get(plan.activity_type.value)
        if sub_skill is not None and activity is not None:
            templates = get_templates_for(sub_skill, activity)
            if templates:
                supported = [
                    tpl
                    for tpl in templates
                    if tpl.difficulty_range[0] <= user_level <= tpl.difficulty_range[1]
                ]
                candidates = supported or templates
                activity_cycle_length = max(plan.activity_cycle_length, 1)
                occurrence_index = (max(plan.week_number, 1) - 1) // activity_cycle_length
                return candidates[occurrence_index % len(candidates)]

        for tpl in ALL_TEMPLATES:
            if tpl.template_id == _DEFAULT_TEMPLATE_ID:
                return tpl
        raise RuntimeError(
            f"Default template {_DEFAULT_TEMPLATE_ID!r} not found in ALL_TEMPLATES"
        )

    @staticmethod
    def _template_for_retry(session: LearningSession) -> TaskTemplate:
        user_level = int(session.user_level or 5)
        matching = [
            tpl
            for tpl in ALL_TEMPLATES
            if tpl.task_type == session.task_type
            and tpl.difficulty_range[0] <= user_level <= tpl.difficulty_range[1]
        ]
        if matching:
            return matching[0]

        fallback = next(
            (tpl for tpl in ALL_TEMPLATES if tpl.task_type == session.task_type),
            None,
        )
        if fallback is not None:
            return fallback

        default = next(
            (tpl for tpl in ALL_TEMPLATES if tpl.template_id == _DEFAULT_TEMPLATE_ID),
            None,
        )
        if default is None:
            raise RuntimeError(
                f"Default template {_DEFAULT_TEMPLATE_ID!r} not found in ALL_TEMPLATES"
            )
        return default

    def _user_sub_level(self, user_id: int) -> int:
        scores = self.score_repo.get_for_user(user_id)
        if not scores:
            return 5
        avg = sum(float(s.score) for s in scores) / len(scores)
        return max(1, min(10, round(avg)))

    @staticmethod
    def _course_topic_for(enrollment: UserEnrollment) -> CourseTopic | None:
        if enrollment.course is None:
            return None
        return get_course_topic(
            duration_weeks=enrollment.course.duration_weeks,
            week=enrollment.current_week,
            day=enrollment.current_day_in_week,
        )

    def _profile_context(self, user_id: int) -> dict[str, Any]:
        profile = UserProfileRepository(self.db).get_by_user_id(user_id)
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

    def _generation_profile(
        self,
        *,
        user_id: int,
        user_level: int,
        topic: str,
        course_topic: CourseTopic | None,
    ) -> dict:
        profile_context = self._profile_context(user_id)
        interests = profile_context["interests"]
        primary_goals = profile_context["primary_goals"]
        content_guidance_parts = [
            f"Keep the grammar concept anchored on '{topic}'.",
        ]
        if interests:
            content_guidance_parts.append(
                f"Use one learner interest as the surface story when natural: {interests}."
            )
        if primary_goals:
            content_guidance_parts.append(
                f"Prefer examples that support this learner goal: {primary_goals}."
            )
        content_guidance_parts.append(
            "Avoid generic office content unless the learner profile clearly points there."
        )

        return {
            "sub_level": user_level,
            "weak_areas": "course topic, not broad skill weaknesses",
            "topic": topic,
            "course_topic": topic,
            "topic_id": course_topic.topic_id if course_topic else "",
            "communication_goal": (
                course_topic.communication_goal if course_topic else topic
            ),
            "language_focus": (
                course_topic.language_focus if course_topic else ""
            ),
            "interests": interests,
            "primary_goals": primary_goals,
            "personalisation_context": profile_context["personalisation_context"],
            "structured_personalisation": profile_context.get(
                "structured_personalisation"
            ),
            "self_assessed_level": profile_context["self_assessed_level"],
            "content_guidance": " ".join(content_guidance_parts),
        }

    def _retry_generation_profile(
        self,
        *,
        session: LearningSession,
        template: TaskTemplate,
    ) -> dict:
        enrollment = self._load_enrollment(session.user_id)
        course_topic = self._course_topic_for(enrollment)
        current_content = dict(session.pre_generated_tasks or {})
        topic = (
            current_content.get("topic_name")
            or current_content.get("topic")
            or session.topic
        )
        user_level = int(session.user_level or current_content.get("sub_level") or 5)

        profile = self._generation_profile(
            user_id=session.user_id,
            user_level=user_level,
            topic=str(topic),
            course_topic=course_topic,
        )
        plan_weeks = getattr(getattr(enrollment, "course", None), "duration_weeks", None)
        previous_passage = str(current_content.get("passage") or "").strip()
        previous_title = str(
            current_content.get("passage_title")
            or current_content.get("topic_name")
            or current_content.get("title")
            or ""
        ).strip()
        avoid_previous = (
            "This is an extra practice task. Generate fresh content at the "
            "same level and for the same learning target. "
            "Do not reuse the previous title, story, names, examples, blank "
            "sentences, or passage."
        )
        if previous_title:
            avoid_previous += f" Previous title/topic text to avoid copying: {previous_title!r}."
        if previous_passage:
            avoid_previous += f" Previous passage to avoid copying: {previous_passage[:500]!r}."

        profile.update(
            {
                "topic_name": str(topic),
                "topic_id": (
                    current_content.get("topic_id")
                    or (course_topic.topic_id if course_topic else "")
                ),
                "week": enrollment.current_week,
                "day": enrollment.current_day_in_week,
                "sub_skill": current_content.get("sub_skill") or session.skill_name,
                "sub_level": user_level,
                "activity": current_content.get("activity") or template.activity.value,
                "plan_type": f"{plan_weeks}w" if plan_weeks else "custom",
                "domain": "general",
                "content_guidance": (
                    f"{profile.get('content_guidance', '')} {avoid_previous}"
                ).strip(),
            }
        )
        return profile

    async def _build_next_activity_update(
        self,
        session: LearningSession,
        state: LearningSessionState,
    ) -> dict[str, Any]:
        self._refresh_queue_statuses(session)
        queue = list(session.task_queue or [])
        current_index = int(session.current_task_index or 0)
        next_item: dict[str, Any] | None = None
        for item in queue:
            index = int(item.get("sequence_index") or 0)
            if index <= current_index:
                continue
            if item.get("status") != UserTaskStatus.COMPLETED.value:
                next_item = item
                break

        if next_item is None:
            prompt = (
                "Today's activities are complete. Go back to the dashboard "
                "to review the day and advance when you're ready."
            )
            messages = list(state.get("messages", []))
            messages.append({"role": "ai", "content": prompt, "type": "chat"})
            return {
                "phase": "ended",
                "messages": messages,
                "task_queue": queue,
                "outgoing_events": [
                    {
                        "type": "chat_message",
                        "role": "assistant",
                        "content": prompt,
                        "actions": ["Go to dashboard"],
                    }
                ],
            }

        user_task = self.user_task_repo.get_by_id(int(next_item["user_task_id"]))
        if user_task is None:
            raise LookupError(f"UserTask {next_item['user_task_id']} does not exist")

        self._apply_active_user_task(
            session,
            user_task,
            int(next_item.get("sequence_index") or 0),
            reset_result_state=True,
        )
        self._refresh_queue_statuses(session)
        session.phase = "practice_task"
        session.messages = list(state.get("messages", []))
        next_state = self._state_from_row(session)
        next_state["messages"] = list(state.get("messages", []))
        update = await task_delivery_node(next_state)
        update["task_queue"] = session.task_queue
        return update

    def _enrich_state_with_profile(
        self,
        state: LearningSessionState,
        user_id: int,
    ) -> None:
        state["learner_profile"] = self._profile_context(user_id)

    @staticmethod
    def _extract_topic(task_content: dict, template_id: str) -> str:
        for key in ("topic", "passage_title", "title"):
            value = task_content.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        blanks = task_content.get("blanks") or []
        if blanks:
            rule = blanks[0].get("grammar_rule")
            if isinstance(rule, str) and rule:
                return rule.replace("_", " ") + " tense"
        return "grammar — verb tenses"

    def _load_session(self, session_id: str) -> LearningSession:
        session = self.session_repo.get_by_session_id(session_id)
        if session is None:
            raise LookupError(f"No learning_session with id={session_id!r}")
        return session

    def _find_daily_session(
        self,
        *,
        enrollment: UserEnrollment,
        bundle: list,
    ) -> LearningSession | None:
        bundle_ids = {task.id for task in bundle}
        rows = (
            self.db.query(LearningSession)
            .filter(
                LearningSession.user_id == enrollment.user_id,
                LearningSession.enrollment_id == enrollment.id,
                LearningSession.created_at >= enrollment.current_day_started_at,
            )
            .order_by(LearningSession.id.desc())
            .all()
        )
        for row in rows:
            queue_ids = {
                int(item.get("user_task_id"))
                for item in (row.task_queue or [])
                if item.get("user_task_id") is not None
            }
            if queue_ids and queue_ids == bundle_ids:
                return row
        return None

    @staticmethod
    def _queue_from_bundle(bundle: list) -> list[dict[str, Any]]:
        return [
            {
                "user_task_id": user_task.id,
                "task_id": user_task.task_id,
                "sequence_index": index,
                "status": user_task.status.value,
                "title": user_task.task.title,
                "task_type": user_task.task.task_type.value,
                "completed_at": (
                    user_task.completed_at.isoformat()
                    if user_task.completed_at
                    else None
                ),
            }
            for index, user_task in enumerate(bundle)
        ]

    @staticmethod
    def _resolve_active_queue_index(
        *,
        bundle: list,
        requested_user_task_id: int | None,
    ) -> int:
        if requested_user_task_id is not None:
            for index, user_task in enumerate(bundle):
                if (
                    user_task.id == requested_user_task_id
                    and user_task.status != UserTaskStatus.COMPLETED
                ):
                    return index

        for index, user_task in enumerate(bundle):
            if user_task.status != UserTaskStatus.COMPLETED:
                return index
        return max(len(bundle) - 1, 0)

    def _refresh_queue_statuses(self, session: LearningSession) -> None:
        queue = []
        for item in session.task_queue or []:
            user_task_id = item.get("user_task_id")
            user_task = (
                self.user_task_repo.get_by_id(int(user_task_id))
                if user_task_id is not None
                else None
            )
            if user_task is None:
                queue.append(item)
                continue
            queue.append(
                {
                    **item,
                    "status": user_task.status.value,
                    "completed_at": (
                        user_task.completed_at.isoformat()
                        if user_task.completed_at
                        else None
                    ),
                }
            )
        session.task_queue = queue

    @staticmethod
    def _all_queue_tasks_complete(session: LearningSession) -> bool:
        queue = session.task_queue or []
        return bool(queue) and all(
            item.get("status") == UserTaskStatus.COMPLETED.value for item in queue
        )

    @staticmethod
    def _topic_for_user_task(user_task) -> str:
        content = dict(user_task.task.content or {})
        return str(
            content.get("topic_name")
            or content.get("topic")
            or content.get("passage_title")
            or user_task.task.title
        )

    @staticmethod
    def _skill_name_for_user_task(user_task) -> str:
        content = dict(user_task.task.content or {})
        skill_name = str(content.get("sub_skill") or "").strip()
        if not skill_name and user_task.task.task_skills:
            linked_skill = user_task.task.task_skills[0].skill
            skill_name = linked_skill.name if linked_skill else ""
        return skill_name or "grammar"

    @staticmethod
    def _activity_type_for_user_task(user_task) -> str:
        content = dict(user_task.task.content or {})
        return str(content.get("activity") or user_task.task.task_type.value)

    def _apply_active_user_task(
        self,
        session: LearningSession,
        user_task,
        index: int,
        *,
        reset_result_state: bool,
    ) -> None:
        content = dict(user_task.task.content or {})
        session.user_task_id = user_task.id
        session.current_task_index = index
        session.topic = self._topic_for_user_task(user_task)
        session.skill_name = self._skill_name_for_user_task(user_task)
        session.activity_type = self._activity_type_for_user_task(user_task)
        session.task_type = user_task.task.task_type.value
        session.user_level = int(content.get("sub_level") or user_task.task.difficulty or 5)
        session.pre_generated_tasks = content
        if reset_result_state:
            session.user_submission = None
            session.evaluation = None
            session.feedback = None
            session.understanding_confirmed = True
        if user_task.status == UserTaskStatus.PENDING:
            user_task.status = UserTaskStatus.IN_PROGRESS

    def _state_from_row(self, session: LearningSession) -> LearningSessionState:
        state: LearningSessionState = {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "enrollment_id": session.enrollment_id,
            "user_task_id": session.user_task_id,
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
        }
        self._rehydrate_daily_plan(state, session)
        return state

    def _rehydrate_daily_plan(
        self,
        state: LearningSessionState,
        session: LearningSession,
    ) -> None:
        """Re-fetch the day's plan from `daily_plans` so it's available on
        every WebSocket message, not just the first turn.

        Looks up by the enrollment's current (week, day). For a single-day
        session this is stable; if the user advances days mid-session the
        plan_loader will regenerate on the next session open.
        """
        try:
            enrollment = self.enrollment_repo.get_by_id(session.enrollment_id)
        except Exception:
            enrollment = None
        if enrollment is None or enrollment.course is None:
            return

        course_slug = enrollment.course.slug
        week = enrollment.current_week
        day = enrollment.current_day_in_week
        plan_row = self.daily_plan_repo.get_for_day(
            user_id=session.user_id,
            course_slug=course_slug,
            week=week,
            day=day,
        )
        if plan_row is None:
            return
        state["daily_plan"] = dict(plan_row.plan_json)
        state["course_slug"] = course_slug
        state["week"] = week
        state["day"] = day

    def _apply_update(
        self, session: LearningSession, update: dict[str, Any]
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

    def _mark_bound_task_complete(self, session: LearningSession) -> None:
        """Complete the dashboard assignment attached to this chat session."""
        user_task_id = getattr(session, "user_task_id", None)
        if user_task_id is None or not hasattr(self, "user_task_repo"):
            return

        user_task = self.user_task_repo.get_by_id(user_task_id)
        if user_task is None:
            return
        if user_task.status == UserTaskStatus.COMPLETED:
            return
        if user_task.status == UserTaskStatus.SKIPPED:
            return
        if not session.evaluation:
            return

        self._persist_session_scores(session, user_task_id)
        self.user_task_repo.mark_completed(user_task)
        self._refresh_queue_statuses(session)
        self.session_repo.save(session)

    def _persist_session_scores(
        self, session: LearningSession, user_task_id: int
    ) -> None:
        """Persist UserResponse + Evaluation rows and update skill scores.

        Chat sessions store evaluation results in LearningSession.evaluation
        (JSON) but never write UserResponse/Evaluation DB rows, so the stats
        page shows 0.0 and points never update. This method bridges that gap
        when the session ends.
        """
        from app.modules.progress.service import PointsUpdaterService, ScoreUpdaterService
        from app.modules.responses.repository import (
            EvaluationRepository,
            FeedbackRepository,
            ResponseRepository,
        )

        evaluation_data = session.evaluation
        if not evaluation_data:
            return

        response_repo = ResponseRepository(self.db)
        evaluation_repo = EvaluationRepository(self.db)

        # Idempotent: skip if already persisted (e.g. double-end-session call).
        if response_repo.get_by_user_task_id(user_task_id) is not None:
            return

        percentage = float(evaluation_data.get("percentage", 0.0))
        overall_score = round(percentage / 10.0, 2)
        user_submission = session.user_submission or {}

        response = response_repo.create(
            user_task_id=user_task_id,
            content=user_submission,
            raw_text=None,
        )
        evaluation = evaluation_repo.create(
            response_id=response.id,
            overall_score=overall_score,
            percentage=percentage,
            report=evaluation_data,
        )
        FeedbackRepository(self.db).create(
            evaluation_id=evaluation.id,
            body=session.feedback or {},
        )

        # ScoreUpdaterService.apply commits internally.
        try:
            ScoreUpdaterService(self.db).apply(evaluation.id)
        except Exception:
            logger.exception(
                "WMA score update failed for learning session task %s", user_task_id
            )

        # PointsUpdaterService.apply commits internally.
        try:
            PointsUpdaterService(self.db).apply(evaluation.id)
        except Exception:
            logger.exception(
                "Points update failed for learning session task %s", user_task_id
            )

    @staticmethod
    def _render_outgoing(events: list[dict]) -> list[WSOutgoingMessage]:
        return [WSOutgoingMessage(**evt) for evt in events]

    @staticmethod
    def _post_feedback_actions(state: LearningSessionState) -> list[str]:
        queue = list(state.get("task_queue") or [])
        current_index = int(state.get("current_task_index") or 0)
        has_next = any(
            int(item.get("sequence_index") or index) > current_index
            and item.get("status") != UserTaskStatus.COMPLETED.value
            for index, item in enumerate(queue)
        )
        if has_next:
            return ["Next activity", "Go to dashboard"]
        return ["Go to dashboard"]

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
            type="chat_stream_start",
            role=role,
            stream_id=sid,
        )
        for chunk in self._split_text_chunks(text):
            yield WSOutgoingMessage(
                type="chat_stream_delta",
                role=role,
                stream_id=sid,
                content=chunk,
            )
        yield WSOutgoingMessage(
            type="chat_stream_end",
            role=role,
            stream_id=sid,
            content=text,
            actions=actions,
        )

    async def _stream_outgoing_events(
        self, events: list[dict]
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
    def _readiness_checkpoint_message(state: LearningSessionState) -> str | None:
        messages = list(state.get("messages", []))
        if _learner_turn_count(messages) < _readiness_turn_threshold(
            state.get("topic") or ""
        ):
            return None

        latest_user = next(
            (m for m in reversed(messages) if m.get("role") == "user"),
            {},
        )
        latest_text = str(latest_user.get("content") or "")
        if _needs_clarification(latest_text):
            return None

        previous_tutor_message = _last_tutor_message(messages[:-1])
        if _tutor_asked_readiness(previous_tutor_message):
            return None

        topic = state.get("topic") or "this topic"
        return (
            f"You have practiced the main idea for {topic}: find the subject, "
            "look for time or frequency clues, and choose the verb form. "
            "Does this feel clear enough to start the practice task?"
        )

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
            type="chat_stream_start",
            role="assistant",
            stream_id=stream_id,
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
                    type="chat_stream_delta",
                    role="assistant",
                    stream_id=stream_id,
                    content=chunk,
                )
        except Exception:
            logger.exception("teaching turn streaming failed; using fallback")

        content = "".join(chunks).strip()
        if not content:
            fallback = self._teaching_fallback_for_state(state)
            chunks.clear()
            for chunk in self._split_text_chunks(fallback):
                chunks.append(chunk)
                yield WSOutgoingMessage(
                    type="chat_stream_delta",
                    role="assistant",
                    stream_id=stream_id,
                    content=chunk,
                )
            content = fallback

        new_messages = list(state.get("messages", []))
        new_messages.append({"role": "ai", "content": content, "type": "chat"})
        self._apply_update(
            session,
            {
                "phase": "teaching",
                "messages": new_messages,
            },
        )
        self.db.commit()

        yield WSOutgoingMessage(
            type="chat_stream_end",
            role="assistant",
            stream_id=stream_id,
            content=content,
        )

    @staticmethod
    def _teaching_fallback_for_state(state: LearningSessionState) -> str:
        messages = list(state.get("messages", []))
        learner_turns = sum(1 for m in messages if m.get("role") == "user")
        topic = state.get("topic") or "this topic"

        if learner_turns <= 0:
            return (
                f"Today we are learning {topic}. Look at the subject first, "
                "then choose the verb form that matches it. What clue would "
                "you check first?"
            )
        if learner_turns == 1:
            return (
                "Good example. Now turn it into a full present-simple sentence "
                "with a clear subject, like 'I read every day.' What changes "
                "if the subject is 'he' or 'she'?"
            )
        if learner_turns == 2:
            return (
                "Nice. Next rule: with he, she, or it, we usually add 's' to "
                "the verb. How would you change 'I read before sleeping' if "
                "the subject is 'she'?"
            )
        if learner_turns == 3:
            return (
                "Good. Now add a frequency clue such as always, often, or a "
                "few times a week. Can you make one sentence with a frequency "
                "word and the correct verb form?"
            )
        if learner_turns == 4:
            return (
                "Great. For a blank, first find the subject, then the time "
                "clue, then choose the verb form. In 'She ___ every evening,' "
                "would you choose 'walk' or 'walks'?"
            )
        return (
            "You have the main idea now: subject plus the right present-simple "
            "verb form. If that feels clear, say 'ready' and I will give you "
            "the practice task."
        )

    async def _stream_followup_answer(
        self,
        session: LearningSession,
        state: LearningSessionState,
        question: str,
    ) -> AsyncIterator[WSOutgoingMessage]:
        stream_id = uuid.uuid4().hex
        yield WSOutgoingMessage(
            type="chat_stream_start",
            role="assistant",
            stream_id=stream_id,
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
                    type="chat_stream_delta",
                    role="assistant",
                    stream_id=stream_id,
                    content=chunk,
                )

        content = "".join(chunks).strip()
        if not content:
            content = "Sure — what would you like to know?"
            for chunk in self._split_text_chunks(content):
                yield WSOutgoingMessage(
                    type="chat_stream_delta",
                    role="assistant",
                    stream_id=stream_id,
                    content=chunk,
                )

        clarification_check = " Did that clarify your doubt?"
        if content and not _tutor_asked_doubt_clarified(content):
            content = f"{content.rstrip()}{clarification_check}"
            yield WSOutgoingMessage(
                type="chat_stream_delta",
                role="assistant",
                stream_id=stream_id,
                content=clarification_check,
            )

        messages = list(state.get("messages", []))
        messages.append({"role": "ai", "content": content, "type": "chat"})
        self._apply_update(
            session,
            {
                "phase": "follow_up",
                "messages": messages,
            },
        )
        self.db.commit()

        yield WSOutgoingMessage(
            type="chat_stream_end",
            role="assistant",
            stream_id=stream_id,
            content=content,
        )

    # ------------------------------------------------------------------
    # Internal handlers per incoming message type
    # ------------------------------------------------------------------
    async def _handle_user_message(
        self,
        session: LearningSession,
        state: LearningSessionState,
        message: WSIncomingMessage,
    ) -> list[WSOutgoingMessage]:
        text = message.content or ""
        messages = list(state.get("messages", []))
        messages.append({"role": "user", "content": text, "type": "chat"})
        state["messages"] = messages
        session.messages = messages

        if state.get("phase") in ("teaching", None):
            previous_tutor_message = _last_tutor_message(messages[:-1])
            confirmed = _looks_like_understanding(
                text,
                previous_tutor_message=previous_tutor_message,
            )
            session.understanding_confirmed = (
                session.understanding_confirmed or confirmed
            )
            state["understanding_confirmed"] = session.understanding_confirmed
            if confirmed:
                update = await task_delivery_node(state)
            else:
                checkpoint = self._readiness_checkpoint_message(state)
                if checkpoint:
                    messages.append(
                        {"role": "ai", "content": checkpoint, "type": "chat"}
                    )
                    update = {
                        "phase": "teaching",
                        "messages": messages,
                        "outgoing_events": [
                            {
                                "type": "chat_message",
                                "role": "assistant",
                                "content": checkpoint,
                            }
                        ],
                    }
                else:
                    update = await teach_node(state)
            self._apply_update(session, update)
            self.db.commit()
            return self._render_outgoing(update.get("outgoing_events", []))

        if state.get("phase") in ("feedback", "follow_up", "scorecard"):
            update = await followup_node(state)
            self._apply_update(session, update)
            if update.get("phase") == "ended":
                self._mark_bound_task_complete(session)
            self.db.commit()
            return self._render_outgoing(update.get("outgoing_events", []))

        # practice_task / evaluation / ended — accept the message but
        # nudge the user back on track.
        nudge = (
            "Submit your answers using the task above when you're ready."
            if state.get("phase") == "practice_task"
            else "This session has ended. Start a new one from the dashboard."
        )
        messages.append({"role": "ai", "content": nudge, "type": "chat"})
        session.messages = messages
        self.session_repo.save(session)
        self.db.commit()
        return [
            WSOutgoingMessage(type="chat_message", role="assistant", content=nudge)
        ]

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
                text,
                previous_tutor_message=previous_tutor_message,
            )
            session.understanding_confirmed = (
                session.understanding_confirmed or confirmed
            )
            state["understanding_confirmed"] = session.understanding_confirmed
            if confirmed:
                update = await task_delivery_node(state)
                self._apply_update(session, update)
                self.db.commit()
                async for msg in self._stream_outgoing_events(
                    update.get("outgoing_events", [])
                ):
                    yield msg
            else:
                checkpoint = self._readiness_checkpoint_message(state)
                if checkpoint:
                    messages.append(
                        {"role": "ai", "content": checkpoint, "type": "chat"}
                    )
                    self._apply_update(
                        session,
                        {
                            "phase": "teaching",
                            "messages": messages,
                        },
                    )
                    self.db.commit()
                    async for msg in self._stream_chat_text(checkpoint):
                        yield msg
                else:
                    async for msg in self._stream_teaching_turn(session, state):
                        yield msg
            return

        if state.get("phase") in ("feedback", "follow_up", "scorecard"):
            async for msg in self._stream_followup_response(session, state, text):
                yield msg
            return

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

    async def _handle_task_submission(
        self,
        session: LearningSession,
        state: LearningSessionState,
        message: WSIncomingMessage,
    ) -> list[WSOutgoingMessage]:
        answers = message.answers or {}
        session.user_submission = answers
        state["user_submission"] = answers

        eval_update = await evaluation_node(state)
        self._apply_update(session, eval_update)
        # Merge evaluation back into state for the feedback node
        state["evaluation"] = eval_update.get("evaluation")
        state["phase"] = eval_update.get("phase", state.get("phase"))
        state["messages"] = eval_update.get("messages", state.get("messages", []))

        feedback_update = await feedback_node(state)
        self._apply_update(session, feedback_update)
        self._mark_bound_task_complete(session)
        self.db.commit()

        events = list(eval_update.get("outgoing_events", []))
        events.extend(feedback_update.get("outgoing_events", []))
        return self._render_outgoing(events)

    async def _handle_task_submission_stream(
        self,
        session: LearningSession,
        state: LearningSessionState,
        message: WSIncomingMessage,
    ) -> AsyncIterator[WSOutgoingMessage]:
        answers = message.answers or {}
        session.user_submission = answers
        state["user_submission"] = answers

        eval_update = await evaluation_node(state)
        self._apply_update(session, eval_update)
        state["evaluation"] = eval_update.get("evaluation")
        state["phase"] = eval_update.get("phase", state.get("phase"))
        state["messages"] = eval_update.get("messages", state.get("messages", []))

        for event in eval_update.get("outgoing_events", []):
            yield WSOutgoingMessage(**event)

        feedback_update = await feedback_node(state)
        self._apply_update(session, feedback_update)
        self._mark_bound_task_complete(session)
        self.db.commit()

        async for msg in self._stream_outgoing_events(
            feedback_update.get("outgoing_events", [])
        ):
            yield msg

    async def _handle_follow_up(
        self,
        session: LearningSession,
        state: LearningSessionState,
        message: WSIncomingMessage,
    ) -> list[WSOutgoingMessage]:
        action_text = message.action or message.content or ""
        messages = list(state.get("messages", []))
        messages.append({"role": "user", "content": action_text, "type": "chat"})
        state["messages"] = messages
        session.messages = messages

        action = action_text.strip().lower()
        if any(
            sig in action
            for sig in (
                "next activity",
                "try another task",
                "another task",
                "next task",
                "more",
            )
        ):
            update = await self._build_next_activity_update(session, state)
            self._apply_update(session, update)
            self.db.commit()
            return self._render_outgoing(update.get("outgoing_events", []))

        if action in ("ask a question", "question", "doubt", "clarif"):
            prompt_msg = "Sure — what would you like to know?"
            messages.append({"role": "ai", "content": prompt_msg, "type": "chat"})
            self._apply_update(
                session,
                {
                    "phase": "follow_up",
                    "messages": messages,
                },
            )
            self.db.commit()
            return [
                WSOutgoingMessage(
                    type="chat_message",
                    role="assistant",
                    content=prompt_msg,
                )
            ]

        previous_tutor_message = _last_tutor_message(messages[:-1])
        if _tutor_asked_doubt_clarified(previous_tutor_message):
            if _looks_like_understanding(
                action_text,
                previous_tutor_message=previous_tutor_message,
            ) or _looks_like_acknowledgement(action_text):
                prompt_msg = "Good. What would you like to do next?"
                messages.append({"role": "ai", "content": prompt_msg, "type": "chat"})
                self._apply_update(
                    session,
                    {"phase": "feedback", "messages": messages},
                )
                self.db.commit()
                return [
                    WSOutgoingMessage(
                        type="chat_message",
                        role="assistant",
                        content=prompt_msg,
                        actions=self._post_feedback_actions(state),
                    )
                ]

        update = await followup_node(state)
        self._apply_update(session, update)
        if update.get("phase") == "ended":
            self._mark_bound_task_complete(session)
        self.db.commit()
        return self._render_outgoing(update.get("outgoing_events", []))

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

        async for msg in self._stream_followup_response(
            session, state, action_text
        ):
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
            "go to dashboard",
            "end session",
            "end",
            "stop",
            "bye",
            "goodbye",
        )
        another_signals = (
            "next activity",
            "try another task",
            "another task",
            "next task",
            "more",
        )
        question_signals = ("ask a question", "question", "doubt", "clarif")

        previous_tutor_message = _last_tutor_message(messages)
        if _tutor_asked_doubt_clarified(previous_tutor_message):
            if _looks_like_understanding(
                raw_action,
                previous_tutor_message=previous_tutor_message,
            ) or _looks_like_acknowledgement(raw_action):
                prompt_msg = "Good. What would you like to do next?"
                messages.append({"role": "ai", "content": prompt_msg, "type": "chat"})
                self._apply_update(
                    session,
                    {
                        "phase": "feedback",
                        "messages": messages,
                    },
                )
                self.db.commit()
                async for msg in self._stream_chat_text(
                    prompt_msg,
                    actions=self._post_feedback_actions(state),
                ):
                    yield msg
                return

            if any(pattern.search(action) for pattern in _NON_UNDERSTANDING_PATTERNS):
                prompt_msg = (
                    "No problem. What part is still confusing? Ask it in one "
                    "sentence and I will explain it another way."
                )
                messages.append({"role": "ai", "content": prompt_msg, "type": "chat"})
                self._apply_update(
                    session,
                    {
                        "phase": "follow_up",
                        "messages": messages,
                    },
                )
                self.db.commit()
                async for msg in self._stream_chat_text(prompt_msg):
                    yield msg
                return

        if any(sig in action for sig in end_signals):
            farewell = (
                "Great work. Go back to the dashboard to review today's "
                "activities and advance when you're ready."
            )
            messages.append({"role": "ai", "content": farewell, "type": "chat"})
            self._apply_update(
                session,
                {
                    "phase": "ended",
                    "messages": messages,
                },
            )
            self.db.commit()
            async for msg in self._stream_chat_text(
                farewell,
                actions=["Go to dashboard"],
            ):
                yield msg
            return

        if any(sig in action for sig in another_signals):
            update = await self._build_next_activity_update(session, state)
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
                {
                    "phase": "follow_up",
                    "messages": messages,
                },
            )
            self.db.commit()
            async for msg in self._stream_chat_text(prompt_msg):
                yield msg
            return

        async for msg in self._stream_followup_answer(session, state, raw_action):
            yield msg
