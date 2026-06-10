"""LLM-as-judge for learner-facing feedback quality (Part B Phase 2).

``FeedbackJudge`` runs a separate, stronger model over a piece of produced
feedback and scores it 0–10 on accuracy / relevance / helpfulness /
correctness. It reuses ``ILLMClient.generate_structured`` (provider-swappable,
exactly like the agents) and forces temperature 0.0 — judges must be
deterministic.

Privacy: the judge prompt receives the learner's actual answer, but only the
scores + a short rationale are persisted by the caller — never the raw text.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

from app.ai.agents.prompt_loader import load_prompt
from app.ai.llm.interface import ILLMClient


class JudgeScores(BaseModel):
    """Structured judge output. All axes 0–10; rationale is one sentence."""

    rationale: str = Field(
        default="",
        description="One-sentence justification, written BEFORE the scores.",
    )
    accuracy: float = Field(ge=0.0, le=10.0)
    relevance: float = Field(ge=0.0, le=10.0)
    helpfulness: float = Field(ge=0.0, le=10.0)
    correctness: float = Field(ge=0.0, le=10.0)


def _as_text(value: Any) -> str:
    """Render a task / answer / feedback payload as compact JSON for the prompt."""
    if value is None:
        return "(none)"
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False, indent=2, default=str)
    except (TypeError, ValueError):
        return str(value)


class MentorNoteScores(JudgeScores):
    """Judge output for a RAG mentor note — adds the RAG-specific axis.

    Inherits the four general axes (and rationale-first ordering) from
    ``JudgeScores`` and adds ``faithfulness``: does the note only assert
    patterns that the *retrieved* RAG context actually supports? This is the
    single most important RAG metric — it catches a note inventing a
    "recurring mistake" that the retrieval never returned.
    """

    faithfulness: float = Field(ge=0.0, le=10.0)


class FeedbackJudge:
    """Score one piece of learner-facing feedback for quality."""

    def __init__(self, llm: ILLMClient) -> None:
        self.llm = llm

    async def score(
        self,
        *,
        task: Any,
        user_answer: Any,
        feedback: Any,
    ) -> JudgeScores:
        system_prompt = load_prompt("eval/feedback_judge")
        user_prompt = (
            f"TASK:\n{_as_text(task)}\n\n"
            f"LEARNER ANSWER:\n{_as_text(user_answer)}\n\n"
            f"AI FEEDBACK (the thing you are scoring):\n{_as_text(feedback)}"
        )
        return await self.llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=JudgeScores,
            temperature=0.0,
        )


class MentorNoteJudge:
    """Score one RAG mentor note (Coach's Note) — adds faithfulness.

    The note is generated from retrieved past-feedback context, so the judge
    is given that *same retrieved context* alongside the note and asked whether
    every pattern the note asserts is grounded in it (Part B Phase 3).
    """

    def __init__(self, llm: ILLMClient) -> None:
        self.llm = llm

    async def score(
        self,
        *,
        note: Any,
        rag_context: Any,
        today_activities: Any = None,
    ) -> MentorNoteScores:
        system_prompt = load_prompt("eval/mentor_note_judge")
        user_prompt = (
            f"TODAY'S ACTIVITIES:\n{_as_text(today_activities)}\n\n"
            f"RETRIEVED CONTEXT (the only evidence the note may rely on):\n"
            f"{_as_text(rag_context)}\n\n"
            f"MENTOR NOTE (the thing you are scoring):\n{_as_text(note)}"
        )
        return await self.llm.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_model=MentorNoteScores,
            temperature=0.0,
        )
