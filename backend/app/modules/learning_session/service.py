"""Business logic for chat-driven learning sessions.

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
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.ai.agents.task_generator import TaskGeneratorAgent
from app.ai.graphs.nodes import (
    evaluation_node,
    feedback_node,
    followup_node,
    task_delivery_node,
    teach_node,
)
from app.ai.graphs.state import LearningSessionState
from app.modules.curriculum.constants import WEEK_SCHEDULE
from app.modules.curriculum.exceptions import (
    EnrollmentNotActive,
    NotEnrolled,
)
from app.modules.curriculum.models import EnrollmentStatus, UserEnrollment
from app.modules.curriculum.repository import (
    EnrollmentSkillHistoryRepository,
    UserEnrollmentRepository,
)
from app.modules.curriculum.rotation import RotationEngine
from app.modules.learning_session.models import LearningSession
from app.modules.learning_session.repository import LearningSessionRepository
from app.modules.learning_session.schemas import (
    StartSessionResponse,
    WSIncomingMessage,
    WSOutgoingMessage,
)
from app.modules.skills.repository import SkillRepository, UserSkillScoreRepository
from app.modules.tasks.models import TaskType
from app.tasks.schemas import ALL_TEMPLATES

logger = logging.getLogger(__name__)


# Activity → preferred grammar template id. We default to the read
# fill-in-blanks template for MVP regardless of the rotation pick because
# that is the only widget the frontend currently renders.
_DEFAULT_TEMPLATE_ID = "grammar_read_fill_blanks_v1"


_UNDERSTANDING_PHRASES = (
    "yes", "yeah", "yep", "sure", "ok", "okay", "ready", "let's go",
    "lets go", "i understand", "understand", "got it", "i got it",
    "i'm ready", "im ready", "go ahead", "begin", "start",
)


def _looks_like_understanding(text: str) -> bool:
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return False
    if cleaned in _UNDERSTANDING_PHRASES:
        return True
    return any(phrase in cleaned for phrase in _UNDERSTANDING_PHRASES)


class LearningSessionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.enrollment_repo = UserEnrollmentRepository(db)
        self.history_repo = EnrollmentSkillHistoryRepository(db)
        self.skill_repo = SkillRepository(db)
        self.score_repo = UserSkillScoreRepository(db)
        self.session_repo = LearningSessionRepository(db)
        self.rotation = RotationEngine()
        self.generator = TaskGeneratorAgent()

    # ------------------------------------------------------------------
    # Session creation
    # ------------------------------------------------------------------
    async def create_session(self, *, user_id: int) -> StartSessionResponse:
        enrollment = self._load_enrollment(user_id)
        plan = self._decide_plan(enrollment)
        template = self._pick_template()

        user_level = self._user_sub_level(user_id)
        user_profile = {
            "sub_level": user_level,
            "weak_areas": "grammar",
            "topic": "workplace",
        }

        try:
            task_content = await self.generator.generate(template, user_profile)
        except Exception:
            logger.exception(
                "create_session: task generation failed for user_id=%s "
                "template=%s",
                user_id,
                template.template_id,
            )
            raise

        topic = self._extract_topic(task_content, template.template_id)
        session_id = uuid.uuid4().hex

        self.session_repo.create(
            session_id=session_id,
            user_id=user_id,
            enrollment_id=enrollment.id,
            topic=topic,
            skill_name=plan.skill_name,
            activity_type=plan.activity_type.value,
            task_type=template.task_type,
            user_level=user_level,
            pre_generated_tasks=task_content,
        )

        self.history_repo.upsert_after_assignment(
            enrollment_id=enrollment.id,
            skill_id=plan.skill_id,
            activity_type=plan.activity_type,
        )

        self.db.commit()

        return StartSessionResponse(
            session_id=session_id,
            topic=topic,
            skill_name=plan.skill_name,
            task_type=template.task_type,
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
        update = await teach_node(state)
        self._apply_update(session, update)
        self.db.commit()
        return self._render_outgoing(update.get("outgoing_events", []))

    async def process_message(
        self, session_id: str, message: WSIncomingMessage
    ) -> list[WSOutgoingMessage]:
        session = self._load_session(session_id)
        state = self._state_from_row(session)

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
    def _pick_template():
        for tpl in ALL_TEMPLATES:
            if tpl.template_id == _DEFAULT_TEMPLATE_ID:
                return tpl
        raise RuntimeError(
            f"Default template {_DEFAULT_TEMPLATE_ID!r} not found in ALL_TEMPLATES"
        )

    def _user_sub_level(self, user_id: int) -> int:
        scores = self.score_repo.get_for_user(user_id)
        if not scores:
            return 5
        avg = sum(float(s.score) for s in scores) / len(scores)
        return max(1, min(10, round(avg)))

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

    @staticmethod
    def _state_from_row(session: LearningSession) -> LearningSessionState:
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
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
            "outgoing_events": [],
        }

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
        if "understanding_confirmed" in update:
            session.understanding_confirmed = bool(update["understanding_confirmed"])
        self.session_repo.save(session)

    @staticmethod
    def _render_outgoing(events: list[dict]) -> list[WSOutgoingMessage]:
        return [WSOutgoingMessage(**evt) for evt in events]

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
            confirmed = _looks_like_understanding(text)
            session.understanding_confirmed = (
                session.understanding_confirmed or confirmed
            )
            state["understanding_confirmed"] = session.understanding_confirmed
            if confirmed:
                update = await task_delivery_node(state)
            else:
                update = await teach_node(state)
            self._apply_update(session, update)
            self.db.commit()
            return self._render_outgoing(update.get("outgoing_events", []))

        if state.get("phase") in ("feedback", "follow_up", "scorecard"):
            update = await followup_node(state)
            self._apply_update(session, update)
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
        self.db.commit()

        events = list(eval_update.get("outgoing_events", []))
        events.extend(feedback_update.get("outgoing_events", []))
        return self._render_outgoing(events)

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

        update = await followup_node(state)
        self._apply_update(session, update)
        self.db.commit()
        return self._render_outgoing(update.get("outgoing_events", []))
