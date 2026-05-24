"""LLM-powered mentor note generator.

Takes RAG context (past mistakes, session summaries) plus today's session
data and produces a concise, personalized coaching paragraph.

The note is additive — it never changes scoring. On LLM failure, the
caller gets ``None`` and the scorecard is still returned without a note.
"""

from __future__ import annotations

import logging

from pydantic import BaseModel, Field

from app.ai.llm.exceptions import LLMError
from app.ai.llm.interface import ILLMClient

logger = logging.getLogger(__name__)


# ── LLM output schema ─────────────────────────────────────────────


class MentorNoteOutput(BaseModel):
    """Structured output from the LLM for the mentor note."""

    mentor_note: str = Field(
        description=(
            "A 2-4 sentence paragraph of personalized coaching feedback. "
            "Must reference specific patterns and give one actionable tip."
        )
    )


# ── System prompt ──────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are a strict but caring English language coach writing a post-session \
note to your student. You have access to their complete learning history.

Your note must be:
- 2-4 sentences maximum. Concise and digestible.
- Specific about mistakes. Name exact error patterns you see.
- If they keep making the same mistake across sessions, call it out directly \
  ("This is the third session where you've confused 'their' and 'there'").
- Include one concrete action item for their next session.
- Mixed tone: acknowledge genuine improvement briefly, but lean corrective. \
  Do NOT give generic praise like "Great job!" or "Keep it up!" or \
  "Well done!". If you mention something positive, be specific about what \
  improved.
- Write as a direct, no-nonsense mentor speaking TO the student (use "you").
- If this is their first session (no history provided), focus only on \
  today's mistakes and give targeted advice.
- Do NOT mention scores, points, or numbers. Focus on language skills.

Write the note as a single flowing paragraph, not bullet points."""


# ── Generator ──────────────────────────────────────────────────────


class MentorNoteGenerator:
    """Generates personalized mentor notes using RAG context + LLM."""

    def __init__(self, llm: ILLMClient, *, temperature: float = 0.5) -> None:
        self.llm = llm
        self.temperature = temperature

    async def generate(
        self,
        *,
        today_activities: list[dict],
        today_mistakes: list[dict],
        rag_context: dict,
        points_earned: dict[str, int],
    ) -> str | None:
        """Generate a mentor note paragraph.

        Returns ``None`` on any LLM failure — the scorecard is still
        returned to the user, just without the mentor note.
        """
        user_prompt = self._build_user_prompt(
            today_activities=today_activities,
            today_mistakes=today_mistakes,
            rag_context=rag_context,
        )

        try:
            output = await self.llm.generate_structured(
                system_prompt=_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                output_model=MentorNoteOutput,
                temperature=self.temperature,
            )
            note = (output.mentor_note or "").strip()
            if not note:
                logger.warning("LLM returned empty mentor note")
                return None
            return note
        except LLMError as exc:
            logger.warning("Mentor note generation failed: %s", exc)
            return None

    @staticmethod
    def _build_user_prompt(
        *,
        today_activities: list[dict],
        today_mistakes: list[dict],
        rag_context: dict,
    ) -> str:
        """Assemble the user prompt from today's data + RAG context."""
        sections: list[str] = []

        # Today's session
        sections.append("=== TODAY'S SESSION ===")
        if today_activities:
            for act in today_activities:
                label = act.get("archetype_label", act.get("archetype_id", "?"))
                score = act.get("raw_score", "?")
                sections.append(f"- {label}: {score}/10")

        if today_mistakes:
            sections.append("\nToday's mistakes:")
            for m in today_mistakes[:8]:  # cap
                issue = m.get("issue", "")
                user_wrote = m.get("user_wrote") or ""
                correction = m.get("correction") or ""
                line = f"  • {issue}"
                if user_wrote and correction:
                    line += f" (wrote '{user_wrote}' → '{correction}')"
                sections.append(line)

        # RAG context — past patterns
        similar_mistakes = rag_context.get("similar_past_mistakes", [])
        previous_summaries = rag_context.get("previous_session_summaries", [])

        if similar_mistakes:
            sections.append("\n=== SIMILAR PAST MISTAKES ===")
            for doc in similar_mistakes[:5]:
                text = doc.get("document_text") or doc.get("metadata", {}).get(
                    "document_text", ""
                )
                if text:
                    sections.append(f"- {text[:300]}")

        if previous_summaries:
            sections.append("\n=== PREVIOUS SESSION NOTES ===")
            for doc in previous_summaries[:3]:
                text = doc.get("document_text") or doc.get("metadata", {}).get(
                    "document_text", ""
                )
                if text:
                    sections.append(f"- {text[:300]}")

        if not similar_mistakes and not previous_summaries:
            sections.append(
                "\n(This is the student's first session — no history available.)"
            )

        sections.append(
            "\nWrite a concise mentor note (2-4 sentences) addressing "
            "the patterns you see."
        )

        return "\n".join(sections)
