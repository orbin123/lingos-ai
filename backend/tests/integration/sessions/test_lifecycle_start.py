"""SessionService start path: creation, mandatory attempts, concurrency.

Split out of the former monolithic ``test_session_lifecycle.py``. The shared
``db_session`` fixture lives in ``conftest.py``; seed helpers in
``_lifecycle_support.py``.
"""

from __future__ import annotations

import asyncio

import pytest

from app.modules.curriculum import file_source
from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    ThemeType,
)
from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.exceptions import SessionAlreadyOpen
from app.modules.sessions.models import (
    ActivityAttempt,
    SessionStatus,
)
from app.modules.sessions.service import SessionService
from app.modules.sessions.task_generator import GeneratedTask, StubTaskGenerator
from app.scoring import ARCHETYPE_REGISTRY, CourseLength

from tests.integration.sessions._lifecycle_support import _user_id


# ── start ──────────────────────────────────────────────────────────


class TestStartSession:
    @pytest.mark.asyncio
    async def test_creates_session_with_mandatory_attempts(self, db_session):
        service = SessionService(db_session, evaluator=StubEvaluator(default_score=7.0))
        source_day = file_source.get_day(9, 2)
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        assert session.status is SessionStatus.IN_PROGRESS
        assert session.is_first_attempt is True
        assert len(session.attempts) == 4
        assert [a.archetype_id for a in session.attempts] == list(
            source_day.task_archetypes_used
        )
        assert [a.is_mandatory for a in session.attempts] == [
            c["mandatory"] for c in source_day.activity_contracts
        ]

    @pytest.mark.asyncio
    async def test_authored_w1d1_uses_source_file_content_in_db_mode(
        self,
        db_session,
    ):
        week = CurriculumWeek(
            week_id="wk_24_01",
            course_length="24w",
            week_number=1,
            theme_type=ThemeType.GRAMMAR,
            title="Old DB Week",
            cefr_level="A1",
            sub_level_min=1,
            sub_level_max=2,
            learning_goal="Old DB goal.",
        )
        db_session.add(week)
        db_session.flush()
        db_session.add(
            CurriculumDay(
                day_id="day_24_01_01",
                week_id=week.id,
                day_number=1,
                topic="Old DB family possessives",
                explanation_brief="Old DB brief about family members.",
                default_activities=["read", "write"],
                mandatory_activities=["read"],
                suggested_archetypes={
                    "read": ["READ_COMP_MCQ"],
                    "write": ["WRITE_ERROR_CORR"],
                },
            )
        )
        db_session.commit()

        service = SessionService(db_session)
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_01_01",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write", "listen", "speak"},
        )

        source_day = file_source.get_day_by_id("day_24_01_01")
        assert [a.archetype_id for a in session.attempts] == list(
            source_day.task_archetypes_used
        )
        assert [a.is_mandatory for a in session.attempts] == [True, True, True, True]

        expected_contract = {
            "activity_id": "read_cloze_simple_present",
            "sequence": 1,
            "archetype_id": "READ_CLOZE",
            "activity": "read",
            "task_widget": "fill_blanks",
            "evaluator_type": "rule_plus_llm",
            "evaluation_widget": "read_listen_evaluation",
            "feedback_type": "default",
            "feedback_widget": "read_listen_feedback",
            "mandatory": True,
        }

        # Lazy generation: start persists a placeholder that already carries the
        # deterministic contract (so the blueprint/skeletons resolve) but no
        # real LLM content yet.
        placeholder = session.attempts[0].task_content
        assert "__pending_taskgen" in placeholder
        assert placeholder["activity_contract"] == expected_contract
        assert placeholder["task_widget"] == "fill_blanks"

        # The placeholder is filled with real authored content on delivery.
        await service.ensure_attempt_content(session.attempts[0])
        first_content = session.attempts[0].task_content
        assert "__pending_taskgen" not in first_content
        assert first_content["topic"] == source_day.task_specs[0]["topic_override"]
        assert first_content["explanation_brief"] == source_day.explanation_brief
        assert "family" not in first_content["instructions"].lower()
        assert first_content["activity_contract"] == expected_contract
        assert first_content["task_widget"] == "fill_blanks"
        assert first_content["evaluation_widget"] == "read_listen_evaluation"
        assert first_content["feedback_widget"] == "read_listen_feedback"

    @pytest.mark.asyncio
    async def test_blocks_second_in_progress_session(self, db_session):
        service = SessionService(db_session)
        await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write"},
        )
        with pytest.raises(SessionAlreadyOpen):
            await service.start_session(
                user_id=_user_id(db_session),
                day_id="day_24_09_03",
                course_length=CourseLength.WEEKS_24,
                tasks_per_day=2,
                allowed_activities={"read", "write"},
            )

    @pytest.mark.asyncio
    async def test_attempts_carry_stub_task_content(self, db_session):
        service = SessionService(db_session)
        source_day = file_source.get_day(9, 2)
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write"},
        )
        # Lazy gen: the real stub content only exists once the placeholder is
        # filled on delivery.
        assert "__pending_taskgen" in session.attempts[0].task_content
        await service.ensure_attempt_content(session.attempts[0])
        content = session.attempts[0].task_content
        archetype_id = source_day.task_archetypes_used[0]
        contract = source_day.activity_contracts[0]
        assert "__pending_taskgen" not in content
        assert content["archetype_id"] == archetype_id
        assert content["topic"] == source_day.task_specs[0]["topic_override"]
        assert content["ui_widget"] == ARCHETYPE_REGISTRY[archetype_id].ui_widget
        assert content["activity_contract"]["task_widget"] == contract["task_widget"]
        assert (
            content["activity_contract"]["evaluation_widget"]
            == contract["evaluation_widget"]
        )
        assert (
            content["activity_contract"]["feedback_widget"]
            == contract["feedback_widget"]
        )

    @pytest.mark.asyncio
    async def test_prepare_attempt_for_delivery_fills_placeholder(self, db_session):
        """The on-demand delivery seam fills a placeholder and is idempotent."""
        service = SessionService(db_session)
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write"},
        )
        first = service.next_activity(
            session_id=session.session_id, user_id=_user_id(db_session)
        )
        # next_activity returns the placeholder as persisted at start.
        assert "__pending_taskgen" in first.task_content

        delivered = await service.prepare_attempt_for_delivery(first)
        assert "__pending_taskgen" not in delivered.task_content
        assert delivered.task_content["archetype_id"] == first.archetype_id

        # Idempotent: a second delivery is a no-op (no re-generation).
        filled = dict(delivered.task_content)
        again = await service.prepare_attempt_for_delivery(delivered)
        assert again.task_content == filled


class _OverlapTrackingTaskGenerator:
    """StubTaskGenerator wrapper that records how many generations overlap."""

    def __init__(self) -> None:
        self._inner = StubTaskGenerator()
        self._in_flight = 0
        self.max_in_flight = 0

    async def generate(self, **kwargs) -> GeneratedTask:
        self._in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self._in_flight)
        try:
            # Yield to the event loop so sibling generations can start.
            await asyncio.sleep(0.01)
            return await self._inner.generate(**kwargs)
        finally:
            self._in_flight -= 1


class _FailOnceTaskGenerator:
    """Fails generation for one archetype; succeeds for the rest."""

    def __init__(self, fail_archetype_id: str) -> None:
        self._inner = StubTaskGenerator()
        self._fail_archetype_id = fail_archetype_id

    async def generate(self, *, archetype, **kwargs) -> GeneratedTask:
        await asyncio.sleep(0.01)
        if archetype.archetype_id == self._fail_archetype_id:
            raise RuntimeError("generation blew up")
        return await self._inner.generate(archetype=archetype, **kwargs)


class TestStartSessionConcurrency:
    @pytest.mark.asyncio
    async def test_start_does_not_call_task_llm(self, db_session):
        """Lazy gen: start persists placeholders without invoking the generator."""
        generator = _OverlapTrackingTaskGenerator()
        service = SessionService(db_session, task_generator=generator)
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        assert len(session.attempts) == 4
        # Start never touched the task generator.
        assert generator.max_in_flight == 0
        # Persisted order still follows the plan's sequence, and each attempt
        # carries a pending placeholder with its deterministic contract.
        assert [a.sequence for a in session.attempts] == [1, 2, 3, 4]
        for attempt in session.attempts:
            assert "__pending_taskgen" in attempt.task_content
            assert (
                attempt.task_content["activity_contract"]["archetype_id"]
                == attempt.archetype_id
            )

    @pytest.mark.asyncio
    async def test_background_fill_runs_concurrently(self, db_session):
        generator = _OverlapTrackingTaskGenerator()
        service = SessionService(db_session, task_generator=generator)
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        # The background fill generates all placeholders concurrently under the
        # task-gen semaphore, so at least two must have been in flight at once.
        await service.fill_pending_task_content(
            session_id=session.session_id,
            user_id=_user_id(db_session),
        )
        assert generator.max_in_flight >= 2
        for attempt in session.attempts:
            db_session.refresh(attempt)
            assert "__pending_taskgen" not in attempt.task_content

    @pytest.mark.asyncio
    async def test_failed_background_generation_is_non_fatal(self, db_session):
        """A failing generation in the background fill is logged, not raised.

        Start still persists every attempt as a placeholder, and the failing
        attempt stays a placeholder for the on-demand delivery seam to retry.
        """
        source_day = file_source.get_day(9, 2)
        fail_id = source_day.task_archetypes_used[-1]
        service = SessionService(
            db_session, task_generator=_FailOnceTaskGenerator(fail_id)
        )
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        assert db_session.query(ActivityAttempt).count() == 4
        assert all("__pending_taskgen" in a.task_content for a in session.attempts)

        # Best-effort: does not raise even though one archetype fails.
        await service.fill_pending_task_content(
            session_id=session.session_id,
            user_id=_user_id(db_session),
        )
        for attempt in session.attempts:
            db_session.refresh(attempt)
        unfilled = [
            a for a in session.attempts if "__pending_taskgen" in a.task_content
        ]
        filled = [
            a for a in session.attempts if "__pending_taskgen" not in a.task_content
        ]
        assert [a.archetype_id for a in unfilled] == [fail_id]
        assert len(filled) == 3
