"""SessionService submit path: resubmit blocking + response persistence.

Split out of the former monolithic ``test_session_lifecycle.py``.
"""

from __future__ import annotations

import pytest

from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.exceptions import AttemptAlreadySubmitted
from app.modules.sessions.feedback_generator import StubFeedbackGenerator
from app.modules.sessions.service import SessionService
from app.scoring import CourseLength

from tests.integration.sessions._lifecycle_support import _user_id


class TestSessionLifecycle:
    async def _start(self, db, tasks_per_day=4, score=7.0):
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
            session_id=session.session_id, user_id=session.user_id,
        )
        assert refreshed.attempts[0].user_response == {"answer": "yes"}
        assert refreshed.attempts[0].submitted_at is not None
