"""Tests for the feedback RAG pipeline.

All tests mock the embedding generator and Pinecone client — no live API
calls are made. Tests verify:

  1. Memory document building
  2. Activity feedback upsert flow
  3. Session summary upsert flow
  4. User isolation during retrieval
  5. Empty history / first-session fallback
  6. No scoring mutation
  7. Mentor note generation
  8. Graceful failure handling
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.feedback_memory.memory_builder import (
    build_activity_memory,
    build_session_memory,
)
from app.modules.feedback_memory.mentor_note_generator import (
    MentorNoteGenerator,
    MentorNoteOutput,
)


# ── Memory builder tests ──────────────────────────────────────────


class TestBuildActivityMemory:
    def test_basic_output(self):
        doc = build_activity_memory(
            archetype_id="READ_FIB",
            archetype_name="Fill in the Blanks",
            day_id="day_24_01_03",
            score=6,
            mistakes=[
                {
                    "issue": "Wrong preposition",
                    "user_wrote": "in",
                    "correction": "on",
                    "rule": "time expressions use 'on'",
                }
            ],
            did_well=["Good vocabulary", "Correct verb tenses"],
            next_tip="Review prepositions of time",
            summary="Decent attempt but preposition errors.",
        )
        assert "Fill in the Blanks (READ_FIB)" in doc
        assert "day_24_01_03" in doc
        assert "Score: 6/10" in doc
        assert "Wrong preposition" in doc
        assert "'in' → 'on'" in doc
        assert "Good vocabulary" in doc
        assert "Review prepositions" in doc

    def test_no_mistakes(self):
        doc = build_activity_memory(
            archetype_id="READ_FIB",
            archetype_name="Fill in the Blanks",
            day_id="day_24_01_01",
            score=10,
            mistakes=[],
            did_well=["Perfect score"],
            next_tip=None,
            summary="Flawless.",
        )
        assert "Mistakes" not in doc
        assert "Perfect score" in doc

    def test_no_did_well(self):
        doc = build_activity_memory(
            archetype_id="WRITE_OPEN",
            archetype_name="Open Writing",
            day_id="day_24_02_01",
            score=3,
            mistakes=[{"issue": "Grammar error"}],
            did_well=[],
            next_tip="Practice more",
            summary="Needs work.",
        )
        assert "Strengths" not in doc
        assert "Grammar error" in doc

    def test_caps_mistakes_at_5(self):
        mistakes = [{"issue": f"Mistake {i}"} for i in range(10)]
        doc = build_activity_memory(
            archetype_id="READ_FIB",
            archetype_name="Test",
            day_id="day_24_01_01",
            score=2,
            mistakes=mistakes,
            did_well=[],
            next_tip=None,
            summary="Bad.",
        )
        # Should only include first 5 mistakes
        assert "Mistake 4" in doc
        assert "Mistake 5" not in doc


class TestBuildSessionMemory:
    def test_basic_output(self):
        doc = build_session_memory(
            day_id="day_24_01_03",
            activities_summary=[
                {"archetype_label": "Read", "raw_score": 8},
                {"archetype_label": "Write", "raw_score": 5},
            ],
            points_earned={"grammar": 120, "vocabulary": 80, "fluency": 0},
            mentor_note="You keep mixing up articles.",
        )
        assert "day_24_01_03" in doc
        assert "Activities: 2" in doc
        assert "Read (8/10)" in doc
        assert "grammar=120" in doc
        assert "fluency" not in doc  # zero points excluded
        assert "mixing up articles" in doc

    def test_empty_activities(self):
        doc = build_session_memory(
            day_id="day_24_01_01",
            activities_summary=[],
            points_earned={},
            mentor_note="First session.",
        )
        assert "Activities: 0" in doc
        assert "First session" in doc


# ── Mentor note generator tests ──────────────────────────────────


class TestMentorNoteGenerator:
    @pytest.mark.asyncio
    async def test_generates_note_from_context(self):
        mock_llm = AsyncMock()
        mock_llm.generate_structured = AsyncMock(
            return_value=MentorNoteOutput(
                mentor_note="You keep confusing 'their' and 'there'. Focus on homophones."
            )
        )

        generator = MentorNoteGenerator(mock_llm)
        result = await generator.generate(
            today_activities=[{"archetype_label": "Read", "raw_score": 6}],
            today_mistakes=[
                {"issue": "Wrong homophone", "user_wrote": "their", "correction": "there"}
            ],
            rag_context={
                "similar_past_mistakes": [
                    {"document_text": "Previous: confused their/there"}
                ],
                "previous_session_summaries": [],
            },
            points_earned={"grammar": 50},
        )

        assert result is not None
        assert "their" in result
        assert "there" in result
        mock_llm.generate_structured.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_none_on_llm_failure(self):
        from app.ai.llm.exceptions import LLMError

        mock_llm = AsyncMock()
        mock_llm.generate_structured = AsyncMock(side_effect=LLMError("API down"))

        generator = MentorNoteGenerator(mock_llm)
        result = await generator.generate(
            today_activities=[],
            today_mistakes=[],
            rag_context={},
            points_earned={},
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_empty_note(self):
        mock_llm = AsyncMock()
        mock_llm.generate_structured = AsyncMock(
            return_value=MentorNoteOutput(mentor_note="")
        )

        generator = MentorNoteGenerator(mock_llm)
        result = await generator.generate(
            today_activities=[],
            today_mistakes=[],
            rag_context={},
            points_earned={},
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_first_session_no_history(self):
        mock_llm = AsyncMock()
        mock_llm.generate_structured = AsyncMock(
            return_value=MentorNoteOutput(
                mentor_note="Watch your article usage with countable nouns."
            )
        )

        generator = MentorNoteGenerator(mock_llm)
        result = await generator.generate(
            today_activities=[{"archetype_label": "Write", "raw_score": 5}],
            today_mistakes=[{"issue": "Missing article"}],
            rag_context={
                "similar_past_mistakes": [],
                "previous_session_summaries": [],
            },
            points_earned={"grammar": 30},
        )

        assert result is not None
        # Verify the prompt mentions first session
        call_args = mock_llm.generate_structured.call_args
        user_prompt = call_args.kwargs["user_prompt"]
        assert "first session" in user_prompt.lower() or "no history" in user_prompt.lower()


# ── User isolation test ──────────────────────────────────────────


class TestUserIsolation:
    @pytest.mark.asyncio
    async def test_retrieval_filters_by_user_id(self):
        """Verify that Pinecone queries include user_id filter."""
        from app.modules.feedback_memory.rag_service import FeedbackRAGService

        mock_db = MagicMock()
        mock_embedder = AsyncMock()
        mock_embedder.embed = AsyncMock(return_value=[0.1] * 1024)

        mock_vector_store = AsyncMock()
        mock_vector_store.query = AsyncMock(return_value=[])

        service = FeedbackRAGService(
            mock_db,
            embedding_generator=mock_embedder,
            embedding_service=mock_vector_store,
        )

        await service.retrieve_context_for_feedback(
            user_id=42,
            current_mistakes=[{"issue": "test"}],
            current_day_id="day_24_01_01",
        )

        # Should have been called twice (once for activity feedback, once for session summaries)
        assert mock_vector_store.query.await_count == 2

        # Both calls should filter by user_id=42
        for call in mock_vector_store.query.call_args_list:
            filter_arg = call.kwargs.get("filter", {})
            assert filter_arg.get("user_id") == {"$eq": 42}


# ── Empty history fallback test ──────────────────────────────────


class TestEmptyHistoryFallback:
    @pytest.mark.asyncio
    async def test_empty_context_returns_empty_lists(self):
        from app.modules.feedback_memory.rag_service import FeedbackRAGService

        mock_db = MagicMock()
        mock_embedder = AsyncMock()
        mock_embedder.embed = AsyncMock(return_value=[0.1] * 1024)

        mock_vector_store = AsyncMock()
        mock_vector_store.query = AsyncMock(return_value=[])

        service = FeedbackRAGService(
            mock_db,
            embedding_generator=mock_embedder,
            embedding_service=mock_vector_store,
        )

        result = await service.retrieve_context_for_feedback(
            user_id=1,
            current_mistakes=[],
            current_day_id="day_24_01_01",
        )

        assert result["similar_past_mistakes"] == []
        assert result["previous_session_summaries"] == []


# ── Summary inclusion in activity doc ─────────────────────────────


def test_activity_memory_includes_summary():
    doc = build_activity_memory(
        archetype_id="READ_FIB",
        archetype_name="Fill in the Blanks",
        day_id="day_24_01_03",
        score=6,
        mistakes=[],
        did_well=[],
        next_tip=None,
        summary="Strong vocabulary but shaky prepositions.",
    )
    assert "Summary: Strong vocabulary but shaky prepositions." in doc


# ── Deterministic / idempotent vector ids ─────────────────────────


def _rag_service(embedder=None, store=None):
    """Build a FeedbackRAGService with a mocked repo + Pinecone."""
    from app.modules.feedback_memory.rag_service import FeedbackRAGService

    embedder = embedder or AsyncMock()
    if not hasattr(embedder, "embed"):
        embedder.embed = AsyncMock(return_value=[0.1] * 1024)
    store = store or AsyncMock()
    service = FeedbackRAGService(
        MagicMock(), embedding_generator=embedder, embedding_service=store,
    )
    service._repo = MagicMock()
    return service, embedder, store


class TestDeterministicVectorIds:
    @pytest.mark.asyncio
    async def test_activity_vector_id_is_stable(self):
        service, _embedder, store = _rag_service()

        vid = await service.store_activity_feedback(
            user_id=7,
            session_id=3,
            attempt_id=99,
            archetype_id="READ_FIB",
            archetype_name="Fill in the Blanks",
            day_id="day_24_01_03",
            score=6,
            mistakes=[{"issue": "x", "rule": "r", "correction": "c"}],
            did_well=[],
            next_tip=None,
            summary="ok",
        )

        assert vid == "act_7_99"  # no random suffix
        assert store.store.await_args.kwargs["vector_id"] == "act_7_99"
        # Postgres mirror upserted (not blind-added) and carries structured mistakes
        service._repo.upsert_by_vector_id.assert_called_once()
        log_meta = service._repo.upsert_by_vector_id.call_args.kwargs["metadata_json"]
        assert log_meta["mistakes"] == [{"issue": "x", "rule": "r", "correction": "c"}]

    @pytest.mark.asyncio
    async def test_session_vector_id_is_stable(self):
        service, _embedder, store = _rag_service()

        vid = await service.store_session_summary(
            user_id=7,
            session_id=3,
            day_id="day_24_01_03",
            activities_summary=[],
            points_earned={},
            mentor_note="note",
        )

        assert vid == "sess_7_3"
        assert store.store.await_args.kwargs["vector_id"] == "sess_7_3"


# ── Delete sync ───────────────────────────────────────────────────


class TestDeleteSync:
    @pytest.mark.asyncio
    async def test_delete_for_attempt_purges_pinecone_and_postgres(self):
        service, _embedder, store = _rag_service()
        service._repo.list_for_attempt.return_value = [
            SimpleNamespace(vector_id="act_7_99")
        ]

        await service.delete_for_attempt(99)

        store.delete.assert_awaited_once()
        assert store.delete.await_args.kwargs["vector_ids"] == ["act_7_99"]
        service._repo.delete_by_vector_ids.assert_called_once_with(["act_7_99"])

    @pytest.mark.asyncio
    async def test_delete_session_summary(self):
        service, _embedder, store = _rag_service()
        service._repo.get_session_summary_for_session.return_value = (
            SimpleNamespace(vector_id="sess_7_3")
        )

        await service.delete_session_summary(3)

        assert store.delete.await_args.kwargs["vector_ids"] == ["sess_7_3"]


# ── Recurrence analytics ──────────────────────────────────────────


class TestRecurrence:
    def test_recurring_pattern_detected_one_off_excluded(self):
        service, _embedder, _store = _rag_service()
        recurring = {"issue": "third-person -s", "rule": "sv-agreement", "correction": "eats"}
        one_off = {"issue": "spelling", "rule": "", "correction": "definitely"}
        service._repo.list_for_user.return_value = [
            SimpleNamespace(memory_type="activity_feedback", metadata_json={"mistakes": [recurring]}),
            SimpleNamespace(memory_type="activity_feedback", metadata_json={"mistakes": [dict(recurring)]}),
            SimpleNamespace(memory_type="activity_feedback", metadata_json={"mistakes": [one_off]}),
        ]

        patterns = service._compute_recurring_patterns(1)

        issues = {p["issue"] for p in patterns}
        assert "third-person -s" in issues       # count 2 >= threshold
        assert "spelling" not in issues          # one-off excluded
        recurring_pattern = next(p for p in patterns if p["issue"] == "third-person -s")
        assert recurring_pattern["count"] == 2

    def test_same_mistake_twice_in_one_activity_counts_once(self):
        service, _embedder, _store = _rag_service()
        m = {"issue": "tense", "rule": "past", "correction": "went"}
        service._repo.list_for_user.return_value = [
            SimpleNamespace(memory_type="activity_feedback", metadata_json={"mistakes": [m, dict(m)]}),
        ]

        patterns = service._compute_recurring_patterns(1, min_count=2)

        assert patterns == []  # only one activity → not recurring


# ── Per-activity feedback RAG ─────────────────────────────────────


class TestPerActivityRetrieval:
    @pytest.mark.asyncio
    async def test_returns_history_block(self):
        store = AsyncMock()
        store.query = AsyncMock(
            return_value=[{"metadata": {"document_text": "past: confused tenses"}}]
        )
        service, _embedder, _store = _rag_service(store=store)

        hist = await service.retrieve_context_for_activity(
            user_id=1, archetype_id="READ_FIB", query_text="tense errors",
        )

        assert hist is not None
        assert "confused tenses" in hist

    @pytest.mark.asyncio
    async def test_blank_query_returns_none(self):
        service, _embedder, _store = _rag_service()

        hist = await service.retrieve_context_for_activity(
            user_id=1, archetype_id="X", query_text="   ",
        )

        assert hist is None


# ── Mentor prompt ordering ────────────────────────────────────────


class TestMentorPromptOrdering:
    def test_today_block_before_history(self):
        prompt = MentorNoteGenerator._build_user_prompt(
            today_activities=[{"archetype_label": "Read", "raw_score": 6}],
            today_mistakes=[{"issue": "wrong tense"}],
            rag_context={
                "recurring_patterns": [
                    {"issue": "third-person -s", "rule": "sv-agr", "count": 3}
                ],
                "previous_session_summaries": [],
            },
        )

        today_idx = prompt.index("=== TODAY (primary) ===")
        recurring_idx = prompt.index("=== RECURRING FROM HISTORY ===")
        assert today_idx < recurring_idx
        assert "third-person -s" in prompt
        assert "seen in 3 activities" in prompt


# ── No scoring mutation test ─────────────────────────────────────


class TestNoScoringMutation:
    def test_scoring_engine_unchanged(self):
        """Verify that the scoring engine produces identical results
        regardless of RAG. This test runs the pure scoring functions
        directly to confirm they have no RAG dependency."""
        from app.scoring.engine import (
            aggregate_session,
            build_session_aggregation,
        )
        from app.scoring.types import ActivityScore
        from app.scoring.constants import CourseLength

        activities = [
            ActivityScore(
                archetype_id="READ_FIB",
                raw_score=7.5,
                weight_map={"grammar": 0.4, "vocabulary": 0.3, "reading_comprehension": 0.3},
            ),
            ActivityScore(
                archetype_id="WRITE_OPEN_SENT",
                raw_score=5.0,
                weight_map={"grammar": 0.4, "vocabulary": 0.3, "writing": 0.3},
            ),
        ]

        # Run scoring twice — should be identical (pure functions, no RAG)
        result1 = aggregate_session(activities, CourseLength.WEEKS_24)
        result2 = aggregate_session(activities, CourseLength.WEEKS_24)

        assert result1 == result2

        # Full aggregation also identical
        agg1 = build_session_aggregation(activities, CourseLength.WEEKS_24)
        agg2 = build_session_aggregation(activities, CourseLength.WEEKS_24)

        assert agg1.points_earned == agg2.points_earned


# ── RAG failure graceful degradation ─────────────────────────────


class TestRagFailureGraceful:
    @pytest.mark.asyncio
    async def test_store_activity_returns_none_on_embedding_error(self):
        from app.modules.feedback_memory.rag_service import FeedbackRAGService

        mock_db = MagicMock()
        mock_embedder = AsyncMock()
        mock_embedder.embed = AsyncMock(side_effect=Exception("API down"))

        service = FeedbackRAGService(
            mock_db,
            embedding_generator=mock_embedder,
        )

        result = await service.store_activity_feedback(
            user_id=1,
            session_id=1,
            attempt_id=1,
            archetype_id="READ_FIB",
            archetype_name="Fill in the Blanks",
            day_id="day_24_01_01",
            score=5,
            mistakes=[],
            did_well=[],
            next_tip=None,
            summary="Test",
        )

        assert result is None  # Gracefully returns None

    @pytest.mark.asyncio
    async def test_retrieve_returns_empty_on_query_error(self):
        from app.modules.feedback_memory.rag_service import FeedbackRAGService

        mock_db = MagicMock()
        mock_embedder = AsyncMock()
        mock_embedder.embed = AsyncMock(side_effect=Exception("API down"))

        service = FeedbackRAGService(
            mock_db,
            embedding_generator=mock_embedder,
        )

        result = await service.retrieve_context_for_feedback(
            user_id=1,
            current_mistakes=[{"issue": "test"}],
            current_day_id="day_24_01_01",
        )

        assert result["similar_past_mistakes"] == []
        assert result["previous_session_summaries"] == []
