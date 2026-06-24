"""SessionService submit path: resubmit blocking + response persistence.

Split out of the former monolithic ``test_session_lifecycle.py``.
"""

from __future__ import annotations

import pytest

from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.exceptions import AttemptAlreadySubmitted
from app.modules.sessions.feedback_generator import StubFeedbackGenerator
from app.modules.sessions.models import AttemptStatus
from app.modules.sessions.service import (
    EvaluationPhase,
    FeedbackPhase,
    SessionService,
)
from app.modules.streaks.models import DailyActivity
from app.scoring import CourseLength

from tests.integration.sessions._lifecycle_support import _user_id


class _SpyFeedbackGenerator(StubFeedbackGenerator):
    """Records whether feedback generation has run yet, so a test can assert the
    evaluation phase yields *before* feedback is generated."""

    def __init__(self) -> None:
        self.called = False

    async def generate(self, **kwargs):
        self.called = True
        return await super().generate(**kwargs)


class TestSessionLifecycle:
    async def _start(self, db, tasks_per_day=4, score=7.0, feedback_generator=None):
        service = SessionService(
            db,
            evaluator=StubEvaluator(default_score=score),
            feedback_generator=feedback_generator or StubFeedbackGenerator(),
        )
        session = await service.start_session(
            user_id=_user_id(db),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=tasks_per_day,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        return service, session

    @pytest.mark.asyncio
    async def test_submit_blocks_resubmit(self, db_session):
        service, session = await self._start(db_session, tasks_per_day=2)
        await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"a": "b"},
        )
        with pytest.raises(AttemptAlreadySubmitted):
            await service.submit_activity(
                session_id=session.session_id,
                user_id=session.user_id,
                sequence=1,
                user_response={"a": "b"},
            )

    @pytest.mark.asyncio
    async def test_submitted_response_persists_on_attempt(self, db_session):
        service, session = await self._start(db_session, tasks_per_day=2)
        await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"answer": "yes"},
        )
        refreshed = service.get_session(
            session_id=session.session_id,
            user_id=session.user_id,
        )
        assert refreshed.attempts[0].user_response == {"answer": "yes"}
        assert refreshed.attempts[0].submitted_at is not None

    # ── phased submit (progressive reveal) ─────────────────────────────

    @pytest.mark.asyncio
    async def test_phased_submit_yields_evaluation_before_feedback(self, db_session):
        """The evaluation phase is yielded the instant grading finishes — before
        the feedback generator has run — and the whole submit costs exactly one
        commit and records the streak once."""
        spy = _SpyFeedbackGenerator()
        service, session = await self._start(
            db_session, tasks_per_day=2, feedback_generator=spy
        )

        commits: list[int] = []
        orig_commit = db_session.commit

        def _counting_commit() -> None:
            commits.append(1)
            orig_commit()

        db_session.commit = _counting_commit  # type: ignore[method-assign]

        gen = service.submit_activity_phased(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"a": "b"},
        )

        phase1 = await anext(gen)
        assert isinstance(phase1, EvaluationPhase)
        # Grading is done but feedback has NOT been generated yet, and nothing
        # has been committed at the evaluation-phase boundary.
        assert spy.called is False
        assert commits == []
        assert phase1.evaluation.raw_score == pytest.approx(7.0)
        assert phase1.attempt.status is AttemptStatus.SUBMITTED

        phase2 = await anext(gen)
        assert isinstance(phase2, FeedbackPhase)
        assert spy.called is True
        # Exactly one commit landed across both phases.
        assert commits == [1]
        assert phase2.feedback.score == 7
        assert phase1.attempt.status is AttemptStatus.EVALUATED

        with pytest.raises(StopAsyncIteration):
            await anext(gen)

        # Streak recorded exactly once for this learner's local day.
        db_session.commit = orig_commit  # type: ignore[method-assign]
        activities = (
            db_session.query(DailyActivity)
            .filter(DailyActivity.user_id == session.user_id)
            .all()
        )
        assert len(activities) == 1
        assert activities[0].activity_count == 1

    @pytest.mark.asyncio
    async def test_submit_activity_wrapper_persists_identical_rows(self, db_session):
        """The public ``submit_activity`` wrapper drains the phased generator and
        is behaviourally identical: it returns the triple and persists the eval +
        feedback rows with the attempt flipped to EVALUATED."""
        service, session = await self._start(db_session, tasks_per_day=2)

        attempt, evaluation, feedback = await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"a": "b"},
        )

        assert attempt.status is AttemptStatus.EVALUATED
        assert evaluation.raw_score == pytest.approx(7.0)
        assert feedback.score == 7
        assert evaluation.attempt_id == attempt.id
        assert feedback.attempt_id == attempt.id

        refreshed = service.get_session(
            session_id=session.session_id,
            user_id=session.user_id,
        )
        graded = refreshed.attempts[0]
        assert graded.evaluation is not None
        assert graded.feedback is not None
        assert graded.evaluation.raw_score == pytest.approx(7.0)
