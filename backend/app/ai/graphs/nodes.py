"""LangGraph node implementations for the learning session loop.

Each node is async, receives the current `LearningSessionState`, and
returns a partial state dict that LangGraph merges back in. The nodes
are intentionally small — heavy lifting lives in the existing agents
(TaskGeneratorAgent, EvaluationService, generate_feedback).
"""

from __future__ import annotations

import logging
import re
from typing import Any

from app.ai.agents.evaluator import EvaluationService
from app.ai.agents.feedback import generate_feedback
from app.ai.graphs.state import LearningSessionState
from app.ai.llm import get_default_llm_client

logger = logging.getLogger(__name__)


_TEACH_SYSTEM_PROMPT = (
    "You are a friendly, encouraging English tutor who chats one-on-one. "
    "Reply ONLY with the chat messages the learner should see, separated by "
    "the literal delimiter '<<<MSG>>>'. Do not include numbering, headers, "
    "or markdown — just plain conversational sentences."
)


def _split_teaching_messages(raw: str) -> list[str]:
    """Split LLM output on the delimiter, falling back to paragraph splits."""
    if "<<<MSG>>>" in raw:
        chunks = [c.strip() for c in raw.split("<<<MSG>>>")]
    else:
        chunks = [c.strip() for c in re.split(r"\n\s*\n", raw)]
    chunks = [c for c in chunks if c]
    if not chunks:
        chunks = [raw.strip()] if raw.strip() else []
    return chunks[:3] if len(chunks) > 3 else chunks


async def teach_node(state: LearningSessionState) -> dict[str, Any]:
    """Produce 2-3 conversational teaching messages about `state['topic']`."""
    topic = state.get("topic") or "today's English topic"
    user_level = int(state.get("user_level", 5))

    user_prompt = (
        f"Teach the concept '{topic}' to a learner at English sub-level "
        f"{user_level}/10 (1=A1 beginner, 10=C2 expert). Use 2 to 3 short "
        "chat messages. Be conversational and warm. Use one or two simple "
        "examples. End with a question that asks if they are ready to "
        "practice. Separate each chat message with '<<<MSG>>>' on its own "
        "line."
    )

    client = get_default_llm_client()
    try:
        raw = await client.generate_text(
            system_prompt=_TEACH_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.6,
        )
    except Exception:
        logger.exception("teach_node LLM call failed; using fallback messages")
        raw = (
            f"Today we'll work on {topic}. <<<MSG>>> "
            "I'll show a quick example and then we'll practice together. "
            "<<<MSG>>> Ready to try a short task?"
        )

    chat_messages = _split_teaching_messages(raw) or [
        f"Today we'll work on {topic}.",
        "Ready to try a short task?",
    ]

    outgoing = [
        {"type": "chat_message", "role": "assistant", "content": msg}
        for msg in chat_messages
    ]

    new_messages = list(state.get("messages", []))
    for msg in chat_messages:
        new_messages.append({"role": "ai", "content": msg, "type": "chat"})

    return {
        "phase": "teaching",
        "outgoing_events": outgoing,
        "messages": new_messages,
    }


async def task_delivery_node(state: LearningSessionState) -> dict[str, Any]:
    """Hand the pre-generated task to the frontend as a UI widget."""
    task_content = state.get("task_content") or {}
    task_type = state.get("task_type") or "fill_in_blanks"

    intro = "Great! Here is your practice task."

    outgoing = [
        {"type": "chat_message", "role": "assistant", "content": intro},
        {
            "type": "ui_event",
            "widget": task_type,
            "payload": task_content,
        },
    ]

    new_messages = list(state.get("messages", []))
    new_messages.append({"role": "ai", "content": intro, "type": "chat"})
    new_messages.append(
        {
            "role": "ai",
            "content": f"[task delivered: {task_type}]",
            "type": "ui_event",
        }
    )

    return {
        "phase": "practice_task",
        "outgoing_events": outgoing,
        "messages": new_messages,
    }


async def evaluation_node(state: LearningSessionState) -> dict[str, Any]:
    """Score the user's submission and emit a scorecard widget."""
    task_content = state.get("task_content") or {}
    user_submission = state.get("user_submission") or {}
    task_type = state.get("task_type") or "fill_in_blanks"
    skill_name = state.get("skill_name", "")
    topic = state.get("topic", "")

    evaluator = EvaluationService()
    evaluation = evaluator.evaluate(
        activity_type=task_type,
        task_content=task_content,
        user_answers=user_submission,
    )

    overall_score = int(round(float(evaluation.get("percentage", 0.0))))
    payload = {
        "overall_score": overall_score,
        "skill_name": skill_name,
        "topic": topic,
        "total": evaluation.get("total", 0),
        "correct_count": evaluation.get("correct_count", 0),
        "questions": evaluation.get("questions", {}),
    }

    outgoing = [
        {
            "type": "ui_event",
            "widget": "scorecard",
            "payload": payload,
        }
    ]

    new_messages = list(state.get("messages", []))
    new_messages.append(
        {
            "role": "ai",
            "content": f"[scorecard delivered: {overall_score}%]",
            "type": "ui_event",
        }
    )

    return {
        "phase": "scorecard",
        "evaluation": evaluation,
        "outgoing_events": outgoing,
        "messages": new_messages,
    }


async def feedback_node(state: LearningSessionState) -> dict[str, Any]:
    """Generate corrective feedback, emit a feedback card + follow-up CTA."""
    task_content = state.get("task_content") or {}
    user_submission = state.get("user_submission") or {}
    evaluation = state.get("evaluation") or {}
    score = int(round(float(evaluation.get("percentage", 0.0))))

    try:
        feedback_obj = await generate_feedback(
            task_content=task_content,
            user_answers=user_submission,
            evaluation_report=evaluation,
            score=score,
        )
        feedback_dict = feedback_obj.model_dump()
    except Exception:
        logger.exception("feedback_node LLM call failed; using fallback feedback")
        feedback_dict = {
            "overall_message": (
                "Good effort. Review the highlighted answers and try the "
                "task again to lock in the rule."
            ),
            "errors": [],
            "score": score,
            "overall_level": "okay",
            "practice_suggestion": "Write 5 sentences using today's pattern.",
        }

    overall_message = feedback_dict.get("overall_message", "")
    follow_up_actions = ["Try another task", "Ask a question", "End session"]

    outgoing: list[dict] = [
        {
            "type": "ui_event",
            "widget": "feedback_card",
            "payload": feedback_dict,
        },
        {
            "type": "chat_message",
            "role": "assistant",
            "content": overall_message,
            "actions": follow_up_actions,
        },
    ]

    new_messages = list(state.get("messages", []))
    new_messages.append(
        {
            "role": "ai",
            "content": "[feedback card delivered]",
            "type": "ui_event",
        }
    )
    if overall_message:
        new_messages.append(
            {"role": "ai", "content": overall_message, "type": "chat"}
        )

    return {
        "phase": "feedback",
        "feedback": feedback_dict,
        "outgoing_events": outgoing,
        "messages": new_messages,
    }


async def followup_node(state: LearningSessionState) -> dict[str, Any]:
    """Branch on the user's follow-up choice."""
    messages = list(state.get("messages", []))
    last_user = next(
        (m for m in reversed(messages) if m.get("role") == "user"),
        None,
    )
    raw_action = (last_user or {}).get("content", "") or ""
    action = raw_action.strip().lower()

    end_signals = ("end session", "end", "stop", "bye", "goodbye")
    another_signals = ("try another task", "another task", "next task", "more")
    question_signals = ("ask a question", "question", "doubt", "clarif")

    if any(sig in action for sig in end_signals):
        farewell = "Great work today! See you tomorrow."
        new_messages = messages + [
            {"role": "ai", "content": farewell, "type": "chat"}
        ]
        return {
            "phase": "ended",
            "outgoing_events": [
                {"type": "chat_message", "role": "assistant", "content": farewell}
            ],
            "messages": new_messages,
        }

    if any(sig in action for sig in another_signals):
        prompt_msg = (
            "Awesome — want to keep practicing the same topic, or move to "
            "the next concept?"
        )
        new_messages = messages + [
            {"role": "ai", "content": prompt_msg, "type": "chat"}
        ]
        return {
            "phase": "teaching",
            "outgoing_events": [
                {"type": "chat_message", "role": "assistant", "content": prompt_msg}
            ],
            "messages": new_messages,
        }

    if any(sig in action for sig in question_signals) and not raw_action.strip():
        prompt_msg = "Sure — what would you like to know?"
        new_messages = messages + [
            {"role": "ai", "content": prompt_msg, "type": "chat"}
        ]
        return {
            "phase": "follow_up",
            "outgoing_events": [
                {"type": "chat_message", "role": "assistant", "content": prompt_msg}
            ],
            "messages": new_messages,
        }

    answer = await _answer_question(state, raw_action)
    new_messages = messages + [
        {"role": "ai", "content": answer, "type": "chat"}
    ]
    return {
        "phase": "follow_up",
        "outgoing_events": [
            {"type": "chat_message", "role": "assistant", "content": answer}
        ],
        "messages": new_messages,
    }


async def _answer_question(state: LearningSessionState, question: str) -> str:
    """Free-form Q&A grounded in the current topic."""
    topic = state.get("topic") or "the current English topic"
    user_level = int(state.get("user_level", 5))

    if not question.strip():
        return "Sure — what would you like to know?"

    system = (
        "You are a friendly English tutor answering a learner's follow-up "
        f"question about '{topic}'. The learner is at sub-level {user_level}/10. "
        "Reply with a short, clear chat message (1-3 sentences). Use simple "
        "language and one example if helpful."
    )
    try:
        client = get_default_llm_client()
        return await client.generate_text(
            system_prompt=system,
            user_prompt=question,
            temperature=0.4,
        )
    except Exception:
        logger.exception("followup Q&A LLM call failed; using fallback")
        return (
            "Good question — let's revisit that next session when I can pull "
            "up extra examples."
        )
