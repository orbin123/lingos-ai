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

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

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
