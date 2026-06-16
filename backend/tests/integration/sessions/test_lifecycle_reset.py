"""Per-activity reset: clear eval/feedback, reopen day, drop scorecard.

Split out of the former monolithic ``test_session_lifecycle.py``.
"""

from __future__ import annotations

import pytest

from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.feedback_generator import StubFeedbackGenerator
from app.modules.sessions.models import (
    ActivityEvaluation,
    ActivityFeedback,
    AttemptStatus,
    SessionScorecard,
    SessionStatus,
)
from app.modules.sessions.service import SessionService
from app.scoring import CourseLength

from tests.integration.sessions._lifecycle_support import _user_id


class TestResetActivity:
    """Per-activity reset: clear eval/feedback, reopen day, drop scorecard."""

    async def _start(self, db, tasks_per_day=2, score=8.0):
        service = SessionService(
            db,
            evaluator=StubEvaluator(default_score=score),
            feedback_generator=StubFeedbackGenerator(),
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
    async def test_reset_clears_attempt_payload(self, db_session):
        service, session = await self._start(db_session)
        await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"answer": "first try"},
        )

        attempt = await service.reset_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
        )

        assert attempt.status is AttemptStatus.PENDING
        assert attempt.user_response is None
        assert attempt.submitted_at is None
        # No evaluation/feedback rows remain for the reset attempt.
        assert (
            db_session.query(ActivityEvaluation)
            .filter_by(attempt_id=attempt.id)
            .count()
            == 0
        )
        assert (
            db_session.query(ActivityFeedback)
            .filter_by(attempt_id=attempt.id)
            .count()
            == 0
        )

    @pytest.mark.asyncio
    async def test_reset_allows_resubmit_without_error(self, db_session):
        service, session = await self._start(db_session)
        await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"answer": "first"},
        )
        await service.reset_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
        )

        # Re-submitting the reset activity must not raise AttemptAlreadySubmitted.
        attempt, evaluation, feedback = await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"answer": "retry"},
        )
        assert attempt.status is AttemptStatus.EVALUATED
        assert attempt.user_response == {"answer": "retry"}
        assert evaluation is not None
        assert feedback is not None

    @pytest.mark.asyncio
    async def test_reset_reopens_completed_day_and_clears_scorecard(self, db_session):
        service, session = await self._start(db_session, tasks_per_day=2, score=8.0)
        for seq in (1, 2):
            await service.submit_activity(
                session_id=session.session_id,
                user_id=session.user_id,
                sequence=seq,
                user_response={"a": "b"},
            )
        scorecard, _ = await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert scorecard is not None
        completed = service.get_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert completed.status is SessionStatus.COMPLETED

        await service.reset_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
        )

        reopened = service.get_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert reopened.status is SessionStatus.IN_PROGRESS
        assert reopened.completed_at is None
        # The stale scorecard is gone (rebuilt on the next complete).
        assert (
            db_session.query(SessionScorecard)
            .filter_by(session_id=reopened.id)
            .count()
            == 0
        )
        assert reopened.attempts[0].status is AttemptStatus.PENDING
        assert reopened.attempts[1].status is AttemptStatus.EVALUATED

    @pytest.mark.asyncio
    async def test_get_scorecard_returns_none_after_reset_reopens_day(
        self, db_session,
    ):
        """After a reset reopens a completed day, the scorecard is gone, so
        the day-level read returns None until the day is completed again."""
        service, session = await self._start(db_session, tasks_per_day=2, score=8.0)
        for seq in (1, 2):
            await service.submit_activity(
                session_id=session.session_id,
                user_id=session.user_id,
                sequence=seq,
                user_response={"a": "b"},
            )
        await service.complete_session(
            session_id=session.session_id, user_id=session.user_id,
        )
        assert service.get_scorecard(
            session_id=session.session_id, user_id=session.user_id,
        ) is not None

        await service.reset_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
        )

        assert service.get_scorecard(
            session_id=session.session_id, user_id=session.user_id,
        ) is None
