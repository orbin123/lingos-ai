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

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.ai.embeddings.embedding_generator import OpenAIEmbeddingGenerator
from app.ai.embeddings.exceptions import EmbeddingError
from app.ai.embeddings.service import EmbeddingService
from app.core.config import settings
from app.modules.feedback_memory.memory_builder import (
    build_activity_memory,
    build_session_memory,
)
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
            # Deterministic id → re-evaluating an attempt UPDATES its vector
            # in place rather than creating a duplicate.
            vector_id = f"act_{user_id}_{attempt_id}"

            # Pinecone metadata must stay flat (str/num/bool/list[str]); it
            # cannot hold the structured mistakes list.
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

            # Postgres mirror keeps the richer structured payload (mistakes,
            # strengths, tip) used for recurrence analytics. JSONB has no flat
            # constraint, so this is safe.
            log_metadata = {
                **metadata,
                "mistakes": mistakes,
                "did_well": did_well,
                "next_tip": next_tip,
            }
            self._repo.upsert_by_vector_id(
                vector_id=vector_id,
                user_id=user_id,
                session_id=session_id,
                attempt_id=attempt_id,
                memory_type="activity_feedback",
                document_text=doc_text,
                metadata_json=log_metadata,
            )

            logger.info(
                "rag.store.activity vector_id=%s user=%d attempt=%d",
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
            # Deterministic id → re-completing a session UPDATES its summary.
            vector_id = f"sess_{user_id}_{session_id}"

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

            self._repo.upsert_by_vector_id(
                vector_id=vector_id,
                user_id=user_id,
                session_id=session_id,
                attempt_id=None,
                memory_type="session_summary",
                document_text=doc_text,
                metadata_json=metadata,
            )

            logger.info(
                "rag.store.session vector_id=%s user=%d session=%d",
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

    # ── DELETE: keep Pinecone in sync with Postgres ────────────────

    async def delete_for_attempt(self, attempt_id: int) -> None:
        """Delete the activity-feedback vector(s) for an attempt.

        Called when an activity is reset / re-opened so stale feedback
        does not linger in the index. Never raises.
        """
        try:
            logs = self._repo.list_for_attempt(attempt_id)
            vector_ids = [log.vector_id for log in logs]
            await self._delete_vectors(vector_ids)
        except Exception:
            logger.warning(
                "Failed to delete activity memory for attempt=%d",
                attempt_id, exc_info=True,
            )

    async def delete_session_summary(self, session_id: int) -> None:
        """Delete the session-summary vector for a session. Never raises."""
        try:
            log = self._repo.get_session_summary_for_session(session_id)
            if log is not None:
                await self._delete_vectors([log.vector_id])
        except Exception:
            logger.warning(
                "Failed to delete session summary for session=%d",
                session_id, exc_info=True,
            )

    async def _delete_vectors(self, vector_ids: list[str]) -> None:
        """Delete from Pinecone AND the Postgres mirror."""
        if not vector_ids:
            return
        await self._vector_store.delete(
            vector_ids=vector_ids, namespace=self._namespace,
        )
        self._repo.delete_by_vector_ids(vector_ids)
        logger.info("rag.delete count=%d ids=%s", len(vector_ids), vector_ids)

    # ── RETRIEVE: context for mentor note ──────────────────────────

    async def retrieve_context_for_feedback(
        self,
        *,
        user_id: int,
        current_mistakes: list[dict],
        current_day_id: str,
        current_session_id: int | None = None,
    ) -> dict:
        """Retrieve RAG context for generating the mentor note.

        Assembles three layers, primary → reference:
          * ``today_activities`` — today's freshly-indexed activity docs
            (from Postgres, the source of truth — no Pinecone consistency
            race).
          * ``recurring_patterns`` — mistakes that recur across the learner's
            history (exact counts from Postgres, count >= configured min).
          * ``similar_past_mistakes`` / ``previous_session_summaries`` —
            semantic top-K from Pinecone (reference only, de-emphasized).

        On any failure, returns whatever was assembled so far (graceful
        degradation — the note generator handles empty context).
        """
        result: dict[str, list] = {
            "today_activities": [],
            "recurring_patterns": [],
            "similar_past_mistakes": [],
            "previous_session_summaries": [],
        }

        # Today + recurrence come from Postgres and never depend on Pinecone,
        # so compute them first and independently of the vector query.
        if current_session_id is not None:
            result["today_activities"] = self._today_activity_docs(
                current_session_id
            )
        result["recurring_patterns"] = self._compute_recurring_patterns(user_id)

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

    async def retrieve_context_for_activity(
        self,
        *,
        user_id: int,
        archetype_id: str,
        query_text: str,
        top_k: int = 3,
    ) -> str | None:
        """Compact 'learner history' block for per-activity feedback.

        Semantic search over the learner's past activity_feedback docs.
        Advisory only — the caller injects this into the feedback prompt to
        personalize the tip; it never affects scoring. Returns ``None`` when
        there's nothing useful. Never raises.
        """
        if not query_text.strip():
            return None
        try:
            query_vector = await self._embedder.embed(query_text)
            matches = await self._vector_store.query(
                values=query_vector,
                top_k=top_k,
                filter={
                    "user_id": {"$eq": user_id},
                    "memory_type": {"$eq": "activity_feedback"},
                },
                namespace=self._namespace,
            )
            lines = [
                f"- {text[:240]}"
                for m in matches[:top_k]
                if (text := (m.get("metadata") or {}).get("document_text") or "")
            ]
            if not lines:
                return None
            logger.info(
                "rag.retrieve.activity user=%d archetype=%s hits=%d",
                user_id, archetype_id, len(lines),
            )
            return "\n".join(lines)
        except Exception:
            logger.warning(
                "Per-activity RAG retrieval failed user=%d archetype=%s",
                user_id, archetype_id, exc_info=True,
            )
            return None

    # ── Helpers ────────────────────────────────────────────────────

    def _today_activity_docs(self, session_id: int) -> list[dict]:
        """Today's activity memory docs straight from Postgres.

        Returns ``[{"document_text": ...}, ...]`` so it matches the shape the
        mentor prompt expects from Pinecone matches.
        """
        logs = [
            log
            for log in self._repo.list_for_session(session_id)
            if log.memory_type == "activity_feedback"
        ]
        return [{"document_text": log.document_text} for log in logs]

    def _compute_recurring_patterns(
        self, user_id: int, *, min_count: int | None = None
    ) -> list[dict]:
        """Count normalized mistakes across the learner's whole history.

        Reads structured mistakes from ``feedback_memory_logs.metadata_json``
        (Postgres — exact counts, not vector similarity). A pattern is
        "recurring" when it appears in at least ``min_count`` distinct
        activities. One-off quirks are intentionally excluded so the Coach's
        Note does not harp on them.
        """
        threshold = (
            min_count
            if min_count is not None
            else settings.RAG_RECURRENCE_MIN_COUNT
        )
        counts: dict[tuple, int] = {}
        examples: dict[tuple, dict] = {}
        try:
            logs = self._repo.list_for_user(
                user_id, memory_type="activity_feedback"
            )
        except Exception:
            logger.warning(
                "Failed to load logs for recurrence user=%d", user_id,
                exc_info=True,
            )
            return []

        for log in logs:
            mistakes = (log.metadata_json or {}).get("mistakes") or []
            # Count each distinct pattern once per activity so a single
            # activity can't inflate a "recurrence".
            seen_in_activity: set[tuple] = set()
            for m in mistakes:
                key = self._normalize_mistake(m)
                if key is None or key in seen_in_activity:
                    continue
                seen_in_activity.add(key)
                counts[key] = counts.get(key, 0) + 1
                examples.setdefault(key, m)

        patterns = [
            {
                "issue": examples[key].get("issue", ""),
                "rule": examples[key].get("rule") or "",
                "count": n,
                "example": examples[key],
            }
            for key, n in counts.items()
            if n >= threshold
        ]
        patterns.sort(key=lambda p: p["count"], reverse=True)
        return patterns

    def _compute_recurring_strengths(
        self, user_id: int, *, min_count: int = 1
    ) -> list[dict]:
        """Count normalized ``did_well`` themes across the learner's history.

        The mirror image of :meth:`_compute_recurring_patterns`, reading the
        ``did_well`` strings from ``feedback_memory_logs.metadata_json``. Each
        theme is counted once per activity. Strengths are sparser than
        mistakes, so the default threshold is 1 (surface anything that has
        appeared). Returns ``[{"theme": str, "count": int}, ...]`` sorted by
        count, most frequent first.
        """
        counts: dict[str, int] = {}
        labels: dict[str, str] = {}
        try:
            logs = self._repo.list_for_user(
                user_id, memory_type="activity_feedback"
            )
        except Exception:
            logger.warning(
                "Failed to load logs for strengths user=%d", user_id,
                exc_info=True,
            )
            return []

        for log in logs:
            did_well = (log.metadata_json or {}).get("did_well") or []
            seen_in_activity: set[str] = set()
            for item in did_well:
                key = (item or "").strip().lower()
                if not key or key in seen_in_activity:
                    continue
                seen_in_activity.add(key)
                counts[key] = counts.get(key, 0) + 1
                labels.setdefault(key, str(item).strip())

        strengths: list[dict[str, Any]] = [
            {"theme": labels[key], "count": n}
            for key, n in counts.items()
            if n >= min_count
        ]
        strengths.sort(key=lambda s: s["count"], reverse=True)
        return strengths

    def compute_stats_themes(
        self, user_id: int, *, limit: int = 3
    ) -> dict[str, list[str]]:
        """Top recurring strength / focus themes for the stats dashboard.

        Deterministic aggregation over the Postgres feedback-memory mirror —
        the same recurrence layer the Coach's Note uses, reused here as the
        RAG-backed source for the stats page (no LLM, no Pinecone round-trip).
        Returns raw theme phrases; the caller turns them into qualitative,
        number-free coaching copy.
        """
        strengths = [
            s["theme"]
            for s in self._compute_recurring_strengths(user_id)[:limit]
            if s.get("theme")
        ]
        focus = [
            (p.get("issue") or p.get("rule") or "").strip()
            for p in self._compute_recurring_patterns(user_id, min_count=1)[:limit]
        ]
        focus = [f for f in focus if f]
        return {"strengths": strengths, "focus": focus}

    @staticmethod
    def _normalize_mistake(m: dict) -> tuple | None:
        """Normalize a mistake dict to a comparable key.

        Keyed on (issue, rule, correction-token). Lower-cased and stripped so
        cosmetic differences collapse. Returns None when there's nothing to
        key on.
        """
        issue = (m.get("issue") or "").strip().lower()
        rule = (m.get("rule") or "").strip().lower()
        correction = (m.get("correction") or "").strip().lower()
        if not issue and not rule and not correction:
            return None
        return (issue, rule, correction)

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
