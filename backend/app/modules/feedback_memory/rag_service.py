"""FeedbackRAGService — orchestrates RAG operations for feedback personalization.

Two main flows:
  1. STORE: After activity evaluation → build memory doc → embed → upsert
  2. RETRIEVE: Before mentor note → query Pinecone → assemble context

Design:
  - All operations are fire-and-forget safe. Failures are logged, never
    propagated to the user.
  - Pinecone namespace isolation keeps feedback vectors separate from
    any existing response vectors.
  - User isolation is enforced via Pinecone metadata filter (user_id).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.ai.embeddings.embedding_generator import OpenAIEmbeddingGenerator
from app.ai.embeddings.exceptions import EmbeddingError
from app.ai.embeddings.service import EmbeddingService
from app.core.config import settings
from app.modules.feedback_memory.memory_builder import (
    build_activity_memory,
    build_session_memory,
)
from app.modules.feedback_memory.models import FeedbackMemoryLog
from app.modules.feedback_memory.repository import FeedbackMemoryRepository

logger = logging.getLogger(__name__)


class FeedbackRAGService:
    """Orchestrates RAG operations for feedback personalization.

    Stateful (holds a DB session) — instantiate per-request.
    """

    def __init__(
        self,
        db: Session,
        *,
        embedding_generator: OpenAIEmbeddingGenerator | None = None,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.db = db
        self._embedder = embedding_generator or OpenAIEmbeddingGenerator()
        self._vector_store = embedding_service or EmbeddingService()
        self._repo = FeedbackMemoryRepository(db)
        self._namespace = settings.PINECONE_FEEDBACK_NAMESPACE

    # ── STORE: activity feedback ───────────────────────────────────

    async def store_activity_feedback(
        self,
        *,
        user_id: int,
        session_id: int,
        attempt_id: int,
        archetype_id: str,
        archetype_name: str,
        day_id: str,
        score: int,
        mistakes: list[dict],
        did_well: list[str],
        next_tip: str | None,
        summary: str,
    ) -> str | None:
        """Build memory doc, embed, upsert to Pinecone, log to Postgres.

        Returns the vector_id on success, None on failure.
        """
        try:
            doc_text = build_activity_memory(
                archetype_id=archetype_id,
                archetype_name=archetype_name,
                day_id=day_id,
                score=score,
                mistakes=mistakes,
                did_well=did_well,
                next_tip=next_tip,
                summary=summary,
            )

            vector = await self._embedder.embed(doc_text)
            vector_id = f"act_{user_id}_{attempt_id}_{uuid4().hex[:8]}"

            metadata: dict[str, Any] = {
                "user_id": user_id,
                "session_id": session_id,
                "attempt_id": attempt_id,
                "memory_type": "activity_feedback",
                "archetype_id": archetype_id,
                "day_id": day_id,
                "score": score,
                "document_text": doc_text[:1000],  # Pinecone metadata size limit
            }

            await self._vector_store.store(
                vector_id=vector_id,
                values=vector,
                metadata=metadata,
                namespace=self._namespace,
            )

            # Log to Postgres
            log = FeedbackMemoryLog(
                user_id=user_id,
                session_id=session_id,
                attempt_id=attempt_id,
                memory_type="activity_feedback",
                vector_id=vector_id,
                document_text=doc_text,
                metadata_json=metadata,
            )
            self._repo.add(log)

            logger.info(
                "Stored activity feedback memory: vector_id=%s user=%d attempt=%d",
                vector_id, user_id, attempt_id,
            )
            return vector_id

        except EmbeddingError:
            logger.warning(
                "Failed to store activity feedback memory for attempt=%d",
                attempt_id, exc_info=True,
            )
            return None
        except Exception:
            logger.warning(
                "Unexpected error storing activity feedback memory for attempt=%d",
                attempt_id, exc_info=True,
            )
            return None

    # ── STORE: session summary ─────────────────────────────────────

    async def store_session_summary(
        self,
        *,
        user_id: int,
        session_id: int,
        day_id: str,
        activities_summary: list[dict],
        points_earned: dict[str, int],
        mentor_note: str,
    ) -> str | None:
        """Store final session summary as a memory.

        Returns the vector_id on success, None on failure.
        """
        try:
            doc_text = build_session_memory(
                day_id=day_id,
                activities_summary=activities_summary,
                points_earned=points_earned,
                mentor_note=mentor_note,
            )

            vector = await self._embedder.embed(doc_text)
            vector_id = f"sess_{user_id}_{session_id}_{uuid4().hex[:8]}"

            metadata: dict[str, Any] = {
                "user_id": user_id,
                "session_id": session_id,
                "memory_type": "session_summary",
                "day_id": day_id,
                "document_text": doc_text[:1000],
            }

            await self._vector_store.store(
                vector_id=vector_id,
                values=vector,
                metadata=metadata,
                namespace=self._namespace,
            )

            log = FeedbackMemoryLog(
                user_id=user_id,
                session_id=session_id,
                attempt_id=None,
                memory_type="session_summary",
                vector_id=vector_id,
                document_text=doc_text,
                metadata_json=metadata,
            )
            self._repo.add(log)

            logger.info(
                "Stored session summary memory: vector_id=%s user=%d session=%d",
                vector_id, user_id, session_id,
            )
            return vector_id

        except EmbeddingError:
            logger.warning(
                "Failed to store session summary memory for session=%d",
                session_id, exc_info=True,
            )
            return None
        except Exception:
            logger.warning(
                "Unexpected error storing session summary for session=%d",
                session_id, exc_info=True,
            )
            return None

    # ── RETRIEVE: context for mentor note ──────────────────────────

    async def retrieve_context_for_feedback(
        self,
        *,
        user_id: int,
        current_mistakes: list[dict],
        current_day_id: str,
    ) -> dict:
        """Retrieve RAG context for generating the mentor note.

        Builds a query from today's mistakes, searches Pinecone for
        semantically similar past feedback, and returns structured context.

        Returns:
            {
                "similar_past_mistakes": [...],
                "previous_session_summaries": [...],
            }

        On any failure, returns empty context (graceful degradation).
        """
        result: dict[str, list] = {
            "similar_past_mistakes": [],
            "previous_session_summaries": [],
        }

        try:
            # Build a query text from today's mistakes
            query_text = self._build_query_text(current_mistakes, current_day_id)
            if not query_text.strip():
                return result

            query_vector = await self._embedder.embed(query_text)

            # Query for similar past activity feedback
            activity_matches = await self._vector_store.query(
                values=query_vector,
                top_k=8,
                filter={
                    "user_id": {"$eq": user_id},
                    "memory_type": {"$eq": "activity_feedback"},
                },
                namespace=self._namespace,
            )
            result["similar_past_mistakes"] = [
                m for m in activity_matches
                # Exclude matches from today's session
                if m.get("metadata", {}).get("day_id") != current_day_id
            ][:5]

            # Query for previous session summaries
            session_matches = await self._vector_store.query(
                values=query_vector,
                top_k=5,
                filter={
                    "user_id": {"$eq": user_id},
                    "memory_type": {"$eq": "session_summary"},
                },
                namespace=self._namespace,
            )
            result["previous_session_summaries"] = session_matches[:3]

        except EmbeddingError:
            logger.warning(
                "RAG retrieval failed for user=%d day=%s",
                user_id, current_day_id, exc_info=True,
            )
        except Exception:
            logger.warning(
                "Unexpected error in RAG retrieval for user=%d day=%s",
                user_id, current_day_id, exc_info=True,
            )

        return result

    # ── Helpers ────────────────────────────────────────────────────

    @staticmethod
    def _build_query_text(mistakes: list[dict], day_id: str) -> str:
        """Build a search query from today's mistakes for similarity search."""
        parts: list[str] = [f"Day: {day_id}"]

        if mistakes:
            parts.append("Mistakes:")
            for m in mistakes[:6]:
                issue = m.get("issue", "")
                user_wrote = m.get("user_wrote") or ""
                correction = m.get("correction") or ""
                line = issue
                if user_wrote and correction:
                    line += f" ('{user_wrote}' → '{correction}')"
                parts.append(f"  {line}")
        else:
            parts.append("No specific mistakes found today.")

        return "\n".join(parts)
