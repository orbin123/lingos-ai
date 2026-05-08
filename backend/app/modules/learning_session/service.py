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
from app.tasks.schemas import ALL_TEMPLATES, get_templates_for
from app.tasks.schemas.base import Activity, SubSkill

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


_UNDERSTANDING_PHRASES = (
    "yes", "yeah", "yep", "sure", "ok", "okay", "ready", "let's go",
    "lets go", "i understand", "understand", "got it", "i got it",
    "i'm ready", "im ready", "go ahead", "begin", "start",
)

_UNDERSTANDING_PATTERNS = tuple(
    re.compile(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])")
    for phrase in _UNDERSTANDING_PHRASES
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

_TEACHING_STREAM_FIRST_CHUNK_TIMEOUT_S = 8.0
_TEACHING_STREAM_CHUNK_TIMEOUT_S = 20.0
_FOLLOWUP_STREAM_FIRST_CHUNK_TIMEOUT_S = 8.0
_FOLLOWUP_STREAM_CHUNK_TIMEOUT_S = 20.0


def _looks_like_understanding(text: str) -> bool:
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return False
    if any(pattern.search(cleaned) for pattern in _NON_UNDERSTANDING_PATTERNS):
        return False
    if "?" in cleaned and _QUESTION_START_PATTERN.search(cleaned):
        return False
    if cleaned in _UNDERSTANDING_PHRASES:
        return True
    return any(pattern.search(cleaned) for pattern in _UNDERSTANDING_PATTERNS)


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

        course_topic = self._course_topic_for(enrollment)
        topic = course_topic.topic_name if course_topic else plan.skill_name
        user_level = course_topic.sub_level if course_topic else self._user_sub_level(user_id)
        template = self._pick_template(plan=plan, user_level=user_level)
        user_profile = self._generation_profile(
            user_id=user_id,
            user_level=user_level,
            topic=topic,
            course_topic=course_topic,
        )

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
        self._enrich_state_with_profile(state, session.user_id)
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
        async for msg in self._stream_teaching_turn(session, state):
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

    def _profile_context(self, user_id: int) -> dict[str, str]:
        profile = UserProfileRepository(self.db).get_by_user_id(user_id)
        if profile is None:
            return {
                "interests": "",
                "primary_goals": "",
                "personalisation_context": "",
                "self_assessed_level": "beginner",
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
            "interests": interests,
            "primary_goals": primary_goals,
            "personalisation_context": profile_context["personalisation_context"],
            "self_assessed_level": profile_context["self_assessed_level"],
            "content_guidance": " ".join(content_guidance_parts),
        }

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
            teaching_chunks = stream_teaching_turn(
                topic=state.get("topic") or "today's English topic",
                sub_skill=state.get("skill_name") or "grammar",
                task_type=state.get("task_type") or "fill_in_blanks",
                user_level=int(state.get("user_level", 5)),
                learner_profile=state.get("learner_profile") or {},
                conversation=list(state.get("messages", [])),
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
            confirmed = _looks_like_understanding(text)
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

        update = await followup_node(state)
        self._apply_update(session, update)
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

        end_signals = ("end session", "end", "stop", "bye", "goodbye")
        another_signals = ("try another task", "another task", "next task", "more")
        question_signals = ("ask a question", "question", "doubt", "clarif")

        if any(sig in action for sig in end_signals):
            farewell = "Great work today! See you tomorrow."
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
            prompt_msg = (
                "Awesome — want to keep practicing the same topic, or move to "
                "the next concept?"
            )
            messages.append({"role": "ai", "content": prompt_msg, "type": "chat"})
            self._apply_update(
                session,
                {
                    "phase": "teaching",
                    "messages": messages,
                },
            )
            self.db.commit()
            async for msg in self._stream_chat_text(prompt_msg):
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
