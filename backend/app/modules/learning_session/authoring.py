"""Ephemeral file-driven chat sessions for curriculum authoring.

This module is deliberately separate from the production
`LearningSessionService`: authoring sessions read `source_24w.py`, keep
state in memory, call the live AI agents, and never touch curriculum,
session, progress, or streak tables.
"""

from __future__ import annotations

import asyncio
import logging
import re
import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from app.ai.agents.teacher import stream_teaching_turn
from app.ai.graphs.nodes import stream_answer_question, task_delivery_node
from app.ai.sessions import build_default_agents
from app.core.config import settings
from app.modules.curriculum.file_source import (
    SCRIPTED_PLAN_KEY,
    FileDayRecord,
    build_teacher_instructions,
    get_day,
    resolve_archetypes,
    split_scripted_plan,
    task_spec_for,
)
from app.modules.learning_session.schemas import (
    StartSessionResponse,
    WSIncomingMessage,
    WSOutgoingMessage,
)
from app.modules.sessions.evaluator import Evaluator
from app.modules.sessions.feedback_generator import FeedbackGenerator, FeedbackResult
from app.modules.sessions.task_generator import TaskGenerator
from app.modules.sessions.widget_mapping import normalize_widget_key
from app.scoring import CourseLength, base_reward, distribute, get_archetype

logger = logging.getLogger(__name__)


_READY_RESPONSE_PHRASES = (
    "ready", "yes", "yeah", "yep", "sure", "ok", "okay",
    "let's go", "lets go", "i'm ready", "im ready", "go ahead",
    "begin", "start",
)
_NON_UNDERSTANDING_PHRASES = (
    "i don't understand", "i dont understand", "i do not understand",
    "i didn't understand", "i didnt understand", "i did not understand",
    "don't understand", "dont understand", "do not understand",
    "not understand", "not clear", "unclear", "confused",
    "not ready", "not yet", "wait", "explain again",
)
_READINESS_PROMPT_PATTERNS = (
    re.compile(r"\b(do you|does this|is this|that|it)\s+(feel\s+)?(clear|make sense)\b"),
    re.compile(r"\b(are you|do you feel|feel)\s+ready\b"),
    re.compile(r"\bready\s+(for|to)\s+(practice|try|start|begin)\b"),
    re.compile(r"\bready to try the practice task\b"),
    re.compile(r"\bif\s+(that|this|it)\s+feels\s+clear\b"),
    re.compile(r"\bif\s+you\s+(feel\s+)?(ready|clear)\b"),
    re.compile(r"\bsay\s+['\"]?(ready|yes|okay|ok)['\"]?\b"),
)

_TEACHING_STREAM_FIRST_CHUNK_TIMEOUT_S = 8.0
_TEACHING_STREAM_CHUNK_TIMEOUT_S = 20.0
_FOLLOWUP_STREAM_FIRST_CHUNK_TIMEOUT_S = 8.0
_FOLLOWUP_STREAM_CHUNK_TIMEOUT_S = 20.0


def _patterns(phrases: tuple[str, ...]) -> tuple[re.Pattern[str], ...]:
    return tuple(
        re.compile(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])")
        for phrase in phrases
    )


_READY_RESPONSE_PATTERNS = _patterns(_READY_RESPONSE_PHRASES)
_NON_UNDERSTANDING_PATTERNS = _patterns(_NON_UNDERSTANDING_PHRASES)


@dataclass
class AuthoringAttempt:
    sequence: int
    archetype_id: str
    archetype_name: str
    core_activity: str
    ui_widget: str
    task_content: dict[str, Any]
    status: str = "pending"
    user_response: dict[str, Any] | None = None
    evaluation: dict[str, Any] | None = None
    feedback: dict[str, Any] | None = None


@dataclass
class AuthoringSession:
    session_id: str
    week_number: int
    day_number: int
    day: FileDayRecord
    attempts: list[AuthoringAttempt]
    teacher_instructions: dict[str, Any] | None
    messages: list[dict[str, Any]] = field(default_factory=list)
    phase: str = "teaching"
    current_task_index: int = 0
    user_submission: dict[str, Any] | None = None
    evaluation: dict[str, Any] | None = None
    feedback: dict[str, Any] | None = None
    understanding_confirmed: bool = False


class AuthoringSessionStore:
    """Process-local session store. State is intentionally disposable."""

    def __init__(self) -> None:
        self._sessions: dict[str, AuthoringSession] = {}

    def get(self, session_id: str) -> AuthoringSession | None:
        return self._sessions.get(session_id)

    def save(self, session: AuthoringSession) -> AuthoringSession:
        self._sessions[session.session_id] = session
        return session

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


authoring_store = AuthoringSessionStore()


class AuthoringModeDisabled(Exception):
    """Raised when a dev-only route is called while authoring mode is off."""


class AuthoringSessionNotFound(Exception):
    """Raised when an ephemeral authoring session id is unknown."""


def _guard_authoring_enabled() -> None:
    if not settings.AUTHORING_CHAT_MODE:
        raise AuthoringModeDisabled("AUTHORING_CHAT_MODE is disabled")


def _last_tutor_message(messages: list[dict[str, Any]]) -> str:
    for message in reversed(messages):
        if message.get("role") in ("ai", "assistant"):
            return str(message.get("content") or "").strip()
    return ""


def _tutor_asked_readiness(text: str) -> bool:
    cleaned = (text or "").strip().lower()
    return bool(cleaned) and any(
        pattern.search(cleaned) for pattern in _READINESS_PROMPT_PATTERNS
    )


def _looks_like_ready_response(text: str) -> bool:
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return False
    return cleaned in _READY_RESPONSE_PHRASES or any(
        pattern.search(cleaned) for pattern in _READY_RESPONSE_PATTERNS
    )


def _looks_like_ready_for_practice(
    text: str, *, previous_tutor_message: str = "",
) -> bool:
    cleaned = (text or "").strip().lower()
    if not cleaned:
        return False
    if any(pattern.search(cleaned) for pattern in _NON_UNDERSTANDING_PATTERNS):
        return False
    return (
        _tutor_asked_readiness(previous_tutor_message)
        and _looks_like_ready_response(cleaned)
    )


def _looks_like_understanding(
    text: str, *, previous_tutor_message: str = "",
) -> bool:
    """Backward-compatible name for the practice readiness gate."""
    return _looks_like_ready_for_practice(
        text, previous_tutor_message=previous_tutor_message,
    )


class AuthoringLearningSessionService:
    def __init__(
        self,
        *,
        store: AuthoringSessionStore | None = None,
        evaluator: Evaluator | None = None,
        feedback_generator: FeedbackGenerator | None = None,
        task_generator: TaskGenerator | None = None,
    ) -> None:
        self.store = store or authoring_store
        self.evaluator = evaluator
        self.feedback_generator = feedback_generator
        self.task_generator = task_generator

    def _ensure_agents(self) -> None:
        if (
            self.evaluator is not None
            and self.feedback_generator is not None
            and self.task_generator is not None
        ):
            return
        evaluator, feedback_generator, task_generator = build_default_agents()
        self.evaluator = self.evaluator or evaluator
        self.feedback_generator = self.feedback_generator or feedback_generator
        self.task_generator = self.task_generator or task_generator

    async def start_session(self, *, week: int, day: int) -> StartSessionResponse:
        _guard_authoring_enabled()
        self._ensure_agents()
        session = await self._build_session(
            session_id=uuid.uuid4().hex,
            week=week,
            day=day,
        )
        self.store.save(session)
        return self._start_response(session, "Authoring session ready")

    async def restart_session(self, *, session_id: str) -> StartSessionResponse:
        _guard_authoring_enabled()
        self._ensure_agents()
        current = self._load(session_id)
        refreshed = await self._build_session(
            session_id=session_id,
            week=current.week_number,
            day=current.day_number,
        )
        self.store.save(refreshed)
        return self._start_response(refreshed, "Authoring session restarted")

    async def _build_session(
        self, *, session_id: str, week: int, day: int,
    ) -> AuthoringSession:
        file_day = get_day(week, day - 1)
        teacher_instructions = build_teacher_instructions(file_day)
        if file_day.teacher_agent_behaviour:
            teacher_instructions[SCRIPTED_PLAN_KEY] = list(
                file_day.teacher_agent_behaviour
            )
        archetypes = resolve_archetypes(file_day)
        attempts: list[AuthoringAttempt] = []
        for sequence, archetype in enumerate(archetypes, start=1):
            spec = task_spec_for(file_day, sequence - 1)
            if self.task_generator is None:
                raise RuntimeError("authoring task generator is not configured")
            generated = await self.task_generator.generate(
                archetype=archetype,
                day_topic=file_day.topic,
                explanation_brief=file_day.explanation_brief,
                cefr_level=file_day.cefr_level,
                sub_level=file_day.sub_level_min,
                user_interests=None,
                task_spec=spec or None,
            )
            attempts.append(
                AuthoringAttempt(
                    sequence=sequence,
                    archetype_id=archetype.archetype_id,
                    archetype_name=archetype.name,
                    core_activity=archetype.core_activity,
                    ui_widget=archetype.ui_widget,
                    task_content=dict(generated.content),
                )
            )
        if not attempts:
            raise ValueError(f"week {week} day {day} has no task_archetypes_used")
        return AuthoringSession(
            session_id=session_id,
            week_number=week,
            day_number=day,
            day=file_day,
            attempts=attempts,
            teacher_instructions=teacher_instructions,
        )

    @staticmethod
    def _start_response(
        session: AuthoringSession, message: str,
    ) -> StartSessionResponse:
        first = session.attempts[0]
        return StartSessionResponse(
            session_id=session.session_id,
            daily_session_id=0,
            topic=session.day.topic,
            skill_name=session.day.theme_type,
            task_type=first.core_activity,
            message=message,
        )

    def _load(self, session_id: str) -> AuthoringSession:
        session = self.store.get(session_id)
        if session is None:
            raise AuthoringSessionNotFound(
                f"No authoring session with id={session_id!r}"
            )
        return session

    async def initial_messages_stream(
        self, session_id: str,
    ) -> AsyncIterator[WSOutgoingMessage]:
        session = self._load(session_id)
        if not session.messages:
            async for msg in self._stream_teaching_turn(session):
                yield msg
            return
        async for msg in self.resume_messages_stream(session_id):
            yield msg

    async def resume_messages_stream(
        self, session_id: str,
    ) -> AsyncIterator[WSOutgoingMessage]:
        session = self._load(session_id)
        if session.phase == "practice_task":
            attempt = self._current_attempt(session)
            async for msg in self._deliver_attempt(session, attempt):
                yield msg
            return
        if session.phase in ("feedback", "follow_up", "scorecard"):
            async for msg in self._stream_chat_text(
                "Ready for the next step?",
                actions=self._next_actions(session),
            ):
                yield msg
            return
        if session.phase == "ended":
            async for msg in self._stream_chat_text(
                "This authoring chat is finished.",
                actions=["Go to dashboard"],
            ):
                yield msg
            return
        previous = _last_tutor_message(session.messages)
        async for msg in self._stream_chat_text(
            previous or f"We are working on {session.day.topic}.",
        ):
            yield msg

    async def process_message_stream(
        self, session_id: str, message: WSIncomingMessage,
    ) -> AsyncIterator[WSOutgoingMessage]:
        session = self._load(session_id)
        if message.type == "user_message":
            async for msg in self._handle_user_message(session, message):
                yield msg
            return
        if message.type == "task_submission":
            async for msg in self._handle_task_submission(session, message):
                yield msg
            return
        if message.type == "follow_up_action":
            async for msg in self._handle_follow_up(session, message):
                yield msg
            return
        yield WSOutgoingMessage(
            type="error", content=f"Unknown message type: {message.type!r}",
        )

    async def _handle_user_message(
        self, session: AuthoringSession, message: WSIncomingMessage,
    ) -> AsyncIterator[WSOutgoingMessage]:
        text = message.content or ""
        session.messages.append({"role": "user", "content": text, "type": "chat"})
        if session.phase in ("teaching", None):
            previous = _last_tutor_message(session.messages[:-1])
            ready_for_practice = _looks_like_ready_for_practice(
                text, previous_tutor_message=previous,
            )
            session.understanding_confirmed = (
                session.understanding_confirmed or ready_for_practice
            )
            if ready_for_practice:
                attempt = self._next_pending_attempt(session)
                if attempt is None:
                    async for msg in self._complete_and_announce(session):
                        yield msg
                    return
                async for msg in self._deliver_attempt(session, attempt):
                    yield msg
                return
            async for msg in self._stream_teaching_turn(session):
                yield msg
            return
        if session.phase in ("feedback", "follow_up", "scorecard"):
            async for msg in self._stream_followup_response(session, text):
                yield msg
            return
        async for msg in self._stream_chat_text(
            "Submit your answers using the task above when you're ready."
        ):
            yield msg

    async def _handle_task_submission(
        self, session: AuthoringSession, message: WSIncomingMessage,
    ) -> AsyncIterator[WSOutgoingMessage]:
        answers = message.answers or {}
        attempt = self._current_attempt(session)
        if attempt.status == "evaluated":
            yield WSOutgoingMessage(
                type="error", content="This activity was already submitted.",
            )
            return

        spec = get_archetype(attempt.archetype_id)
        attempt.user_response = answers
        session.user_submission = answers
        if self.evaluator is None or self.feedback_generator is None:
            self._ensure_agents()
        if self.evaluator is None or self.feedback_generator is None:
            raise RuntimeError("authoring evaluator/feedback agents are not configured")
        eval_result = await self.evaluator.evaluate(
            archetype=spec,
            task_content=attempt.task_content,
            user_response=answers,
            evaluator_overrides=session.day.evaluator_overrides,
        )
        course_length = CourseLength(settings.AUTHORING_CHAT_COURSE_LENGTH)
        reward = base_reward(eval_result.raw_score, course_length)
        weighted = distribute(reward, dict(spec.weight_map))
        evaluation_dict = {
            "raw_score": float(eval_result.raw_score),
            "rubric_scores": dict(eval_result.rubric_scores or {}),
            "base_reward": reward,
            "weighted_points": dict(weighted),
            "evaluator_notes": eval_result.evaluator_notes,
        }
        feedback = await self.feedback_generator.generate(
            archetype=spec,
            evaluation=eval_result,
            user_response=answers,
            task_content=attempt.task_content,
            feedback_overrides=session.day.feedback_overrides,
        )
        feedback_dict = self._feedback_dict(feedback)
        attempt.status = "evaluated"
        attempt.evaluation = evaluation_dict
        attempt.feedback = feedback_dict
        session.evaluation = evaluation_dict
        session.feedback = feedback_dict

        meta = {
            "current_task_index": session.current_task_index,
            "total_tasks": len(session.attempts),
            "sequence": attempt.sequence,
            "daily_session_id": 0,
        }
        yield WSOutgoingMessage(
            type="ui_event",
            widget="scorecard",
            payload={
                "overall_score": feedback.score,
                "skill_name": session.day.theme_type,
                "topic": session.day.topic,
                "rubric_scores": evaluation_dict["rubric_scores"],
                "weighted_points": evaluation_dict["weighted_points"],
                "_session": meta,
            },
        )
        yield WSOutgoingMessage(
            type="ui_event",
            widget="feedback_card",
            payload={
                **feedback_dict,
                "widget": normalize_widget_key(
                    str(
                        attempt.task_content.get("widget")
                        or attempt.task_content.get("ui_widget")
                        or spec.ui_widget
                    )
                ),
                "_session": meta,
            },
        )

        summary = feedback.summary or "Response evaluated."
        if feedback.next_tip:
            summary = f"{summary} {feedback.next_tip}"
        async for msg in self._stream_chat_text(
            summary, actions=self._next_actions(session),
        ):
            yield msg
        session.phase = "feedback"
        session.messages.append(
            {"role": "ai", "content": "[scorecard delivered]", "type": "ui_event"}
        )
        session.messages.append(
            {"role": "ai", "content": "[feedback card delivered]", "type": "ui_event"}
        )
        session.messages.append({"role": "ai", "content": summary, "type": "chat"})

    async def _handle_follow_up(
        self, session: AuthoringSession, message: WSIncomingMessage,
    ) -> AsyncIterator[WSOutgoingMessage]:
        action = message.action or message.content or ""
        session.messages.append({"role": "user", "content": action, "type": "chat"})
        async for msg in self._stream_followup_response(session, action):
            yield msg

    async def _stream_followup_response(
        self, session: AuthoringSession, raw_action: str,
    ) -> AsyncIterator[WSOutgoingMessage]:
        action = raw_action.strip().lower()
        if any(sig in action for sig in ("go to dashboard", "end session", "end")):
            async for msg in self._complete_and_announce(session):
                yield msg
            return
        if any(sig in action for sig in ("next activity", "another task", "more")):
            attempt = self._next_pending_attempt(session)
            if attempt is None:
                async for msg in self._complete_and_announce(session):
                    yield msg
                return
            async for msg in self._deliver_attempt(session, attempt):
                yield msg
            return
        if action in ("ask a question", "question", "doubt", "clarif"):
            prompt = "Sure — what would you like to know?"
            session.messages.append({"role": "ai", "content": prompt, "type": "chat"})
            session.phase = "follow_up"
            async for msg in self._stream_chat_text(prompt):
                yield msg
            return
        async for msg in self._stream_followup_answer(session, raw_action):
            yield msg

    async def _deliver_attempt(
        self, session: AuthoringSession, attempt: AuthoringAttempt,
    ) -> AsyncIterator[WSOutgoingMessage]:
        session.current_task_index = max(0, attempt.sequence - 1)
        session.phase = "practice_task"
        state = self._state(session)
        state["task_content"] = dict(attempt.task_content)
        state["task_type"] = self._widget_for_attempt(attempt)
        state["current_sequence"] = attempt.sequence
        update = await task_delivery_node(state)
        session.messages = list(update.get("messages", session.messages))
        for event in update.get("outgoing_events", []):
            if event.get("type") == "chat_message":
                async for msg in self._stream_chat_text(
                    str(event.get("content") or ""),
                    actions=event.get("actions"),
                    role=str(event.get("role") or "assistant"),
                ):
                    yield msg
            else:
                yield WSOutgoingMessage(**event)

    async def _complete_and_announce(
        self, session: AuthoringSession,
    ) -> AsyncIterator[WSOutgoingMessage]:
        farewell = "Authoring session complete. Go back to the dashboard when ready."
        session.phase = "ended"
        session.messages.append({"role": "ai", "content": farewell, "type": "chat"})
        async for msg in self._stream_chat_text(
            farewell, actions=["Go to dashboard"],
        ):
            yield msg

    def _state(self, session: AuthoringSession) -> dict[str, Any]:
        return {
            "session_id": session.session_id,
            "user_id": 0,
            "daily_session_id": 0,
            "daily_session_uuid": session.session_id,
            "task_queue": [
                {
                    "sequence": a.sequence,
                    "archetype_id": a.archetype_id,
                    "is_mandatory": True,
                    "status": a.status,
                }
                for a in session.attempts
            ],
            "current_task_index": session.current_task_index,
            "phase": session.phase,
            "messages": list(session.messages),
            "topic": session.day.topic,
            "skill_name": session.day.theme_type,
            "activity_type": session.attempts[0].core_activity,
            "user_level": session.day.sub_level_min,
            "task_content": self._current_attempt(session).task_content,
            "task_type": self._widget_for_attempt(self._current_attempt(session)),
            "user_submission": session.user_submission,
            "evaluation": session.evaluation,
            "feedback": session.feedback,
            "understanding_confirmed": session.understanding_confirmed,
            "current_activity_order": session.current_task_index + 1,
            "outgoing_events": [],
            "daily_plan": {"teacher_instructions": session.teacher_instructions},
            "learner_profile": self._dev_profile(),
        }

    @staticmethod
    def _dev_profile() -> dict[str, Any]:
        return {
            "interests": "general",
            "primary_goals": "test the curriculum authoring flow",
            "personalisation_context": "",
            "self_assessed_level": "beginner",
            "structured_personalisation": {
                "extraction_source": "authoring",
                "domain": "general",
                "communication_contexts": ["daily practice"],
                "pain_points": [],
                "tone_preference": "direct",
            },
        }

    def _current_attempt(self, session: AuthoringSession) -> AuthoringAttempt:
        index = max(0, min(session.current_task_index, len(session.attempts) - 1))
        return session.attempts[index]

    @staticmethod
    def _widget_for_attempt(attempt: AuthoringAttempt) -> str:
        content = attempt.task_content or {}
        return normalize_widget_key(
            str(content.get("widget") or content.get("ui_widget") or "")
        )

    @staticmethod
    def _feedback_dict(feedback: FeedbackResult) -> dict[str, Any]:
        return {
            "score": feedback.score,
            "summary": feedback.summary,
            "did_well": list(feedback.did_well or []),
            "mistakes": [
                {
                    "issue": m.issue,
                    "user_wrote": m.user_wrote,
                    "correction": m.correction,
                    "rule": m.rule,
                    "sub_skills_affected": list(m.sub_skills_affected),
                }
                for m in feedback.mistakes
            ],
            "next_tip": feedback.next_tip,
            "sub_skill_breakdown": dict(feedback.sub_skill_breakdown or {}),
        }

    def _next_pending_attempt(
        self, session: AuthoringSession,
    ) -> AuthoringAttempt | None:
        for attempt in session.attempts:
            if attempt.status != "evaluated":
                return attempt
        return None

    def _next_actions(self, session: AuthoringSession) -> list[str]:
        if self._next_pending_attempt(session) is None:
            return ["Go to dashboard"]
        return ["Next activity", "Go to dashboard"]

    async def _stream_teaching_turn(
        self, session: AuthoringSession,
    ) -> AsyncIterator[WSOutgoingMessage]:
        stream_id = uuid.uuid4().hex
        yield WSOutgoingMessage(
            type="chat_stream_start", role="assistant", stream_id=stream_id,
        )
        chunks: list[str] = []
        try:
            teacher_instructions, scripted_plan = split_scripted_plan(
                session.teacher_instructions,
            )
            lesson_description = None
            raw_description = teacher_instructions.pop("lesson_description", None)
            if isinstance(raw_description, str) and raw_description.strip():
                lesson_description = raw_description.strip()
            source = stream_teaching_turn(
                topic=session.day.topic,
                sub_skill=session.day.theme_type,
                task_type=self._widget_for_attempt(self._current_attempt(session)),
                user_level=session.day.sub_level_min,
                learner_profile=self._dev_profile(),
                conversation=list(session.messages),
                teacher_instructions=teacher_instructions,
                scripted_plan=scripted_plan,
                lesson_description=lesson_description,
            )
            async for chunk in self._timed_chunks(
                source,
                first_chunk_timeout_s=_TEACHING_STREAM_FIRST_CHUNK_TIMEOUT_S,
                chunk_timeout_s=_TEACHING_STREAM_CHUNK_TIMEOUT_S,
                timeout_message="authoring teaching turn streaming timed out",
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
            logger.exception("authoring teaching turn failed; using fallback")

        content = "".join(chunks).strip()
        if not content:
            content = (
                f"Today we are learning {session.day.topic}. "
                "Say 'ready' when you want the first practice task."
            )
            for chunk in self._split_text_chunks(content):
                yield WSOutgoingMessage(
                    type="chat_stream_delta",
                    role="assistant",
                    stream_id=stream_id,
                    content=chunk,
                )
        session.phase = "teaching"
        session.messages.append({"role": "ai", "content": content, "type": "chat"})
        yield WSOutgoingMessage(
            type="chat_stream_end",
            role="assistant",
            stream_id=stream_id,
            content=content,
        )

    async def _stream_followup_answer(
        self, session: AuthoringSession, question: str,
    ) -> AsyncIterator[WSOutgoingMessage]:
        stream_id = uuid.uuid4().hex
        yield WSOutgoingMessage(
            type="chat_stream_start", role="assistant", stream_id=stream_id,
        )
        chunks: list[str] = []
        async for chunk in self._timed_chunks(
            stream_answer_question(self._state(session), question),
            first_chunk_timeout_s=_FOLLOWUP_STREAM_FIRST_CHUNK_TIMEOUT_S,
            chunk_timeout_s=_FOLLOWUP_STREAM_CHUNK_TIMEOUT_S,
            timeout_message="authoring follow-up streaming timed out",
        ):
            if chunk:
                chunks.append(chunk)
                yield WSOutgoingMessage(
                    type="chat_stream_delta",
                    role="assistant",
                    stream_id=stream_id,
                    content=chunk,
                )
        content = "".join(chunks).strip() or "Sure — what would you like to know?"
        session.phase = "follow_up"
        session.messages.append({"role": "ai", "content": content, "type": "chat"})
        yield WSOutgoingMessage(
            type="chat_stream_end",
            role="assistant",
            stream_id=stream_id,
            content=content,
        )

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
                type="chat_stream_delta", role=role, stream_id=sid, content=chunk,
            )
        yield WSOutgoingMessage(
            type="chat_stream_end", role=role, stream_id=sid,
            content=text, actions=actions,
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
