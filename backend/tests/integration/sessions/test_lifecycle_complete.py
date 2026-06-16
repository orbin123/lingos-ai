"""SessionService complete path: scorecard, streak timing, replay rescoring.

Split out of the former monolithic ``test_session_lifecycle.py``.
"""

from __future__ import annotations

import pytest

from app.modules.auth.models import UserProfile
from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.feedback_generator import StubFeedbackGenerator
from app.modules.sessions.models import AttemptStatus, SessionStatus
from app.modules.sessions.service import SessionService
from app.modules.progress.models import SkillPoints
from app.modules.streaks.models import DailyActivity
from app.modules.streaks.service import StreakService
from app.scoring import ARCHETYPE_REGISTRY, CourseLength

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
    async def test_full_happy_path(self, db_session):
        service, session = await self._start(db_session, tasks_per_day=4, score=8.0)

        # Walk through all 4 activities.
        for expected_seq in range(1, 5):
            attempt = service.next_activity(
                session_id=session.session_id,
                user_id=session.user_id,
            )
            assert attempt.sequence == expected_seq
            attempt, evaluation, feedback = await service.submit_activity(
                session_id=session.session_id,
                user_id=session.user_id,
                sequence=attempt.sequence,
                user_response={"answer": "hello"},
            )
            assert attempt.status is AttemptStatus.EVALUATED
            assert float(evaluation.raw_score) == 8.0
            assert evaluation.base_reward == 55  # 24w Excellent
            assert sum(evaluation.weighted_points.values()) == pytest.approx(55.0)
            assert feedback.score == 8

        # Complete the session.
        scorecard, report = await service.complete_session(
            session_id=session.session_id,
            user_id=session.user_id,
        )
        assert report.applied is True
        assert scorecard.points_applied is True
        assert sum(scorecard.points_earned.values()) > 0

        # Per-activity breakdown: one entry per submitted attempt, in plan order,
        # each with the fields the end-of-session UI consumes.
        assert scorecard.activities is not None
        assert len(scorecard.activities) == 4
        sequences = [a["sequence"] for a in scorecard.activities]
        assert sequences == [1, 2, 3, 4]
        for entry in scorecard.activities:
            assert entry["raw_score"] == pytest.approx(8.0)
            assert entry["tier"] == "excellent"
            assert entry["base_reward"] == 55
            assert entry["archetype_id"]
            assert entry["archetype_label"]
            assert sum(entry["weighted_points"].values()) == pytest.approx(55.0)

        # Session must now be COMPLETED.
        refreshed = service.get_session(
            session_id=session.session_id,
            user_id=session.user_id,
        )
        assert refreshed.status is SessionStatus.COMPLETED
        assert refreshed.completed_at is not None

    @pytest.mark.asyncio
    async def test_complete_is_idempotent(self, db_session):
        service, session = await self._start(db_session, tasks_per_day=2, score=8.0)
        for seq in (1, 2):
            await service.submit_activity(
                session_id=session.session_id,
                user_id=session.user_id,
                sequence=seq,
                user_response={"a": "b"},
            )
        first, report1 = await service.complete_session(
            session_id=session.session_id,
            user_id=session.user_id,
        )
        second, report2 = await service.complete_session(
            session_id=session.session_id,
            user_id=session.user_id,
        )
        assert first.id == second.id
        assert report1.applied is True
        assert report2.applied is False
        assert report2.reason == "session already completed"

    @pytest.mark.asyncio
    async def test_streak_on_first_submit_not_on_complete(self, db_session):
        """Streak is awarded on activity submit; complete does not double-award."""
        service, session = await self._start(db_session, tasks_per_day=2, score=8.0)
        await service.submit_activity(
            session_id=session.session_id,
            user_id=session.user_id,
            sequence=1,
            user_response={"a": "b"},
        )
        uid = session.user_id
        profile = db_session.query(UserProfile).filter_by(user_id=uid).one()
        assert profile.current_streak == 1
        assert profile.last_animation_type == "rekindle"
        rows = db_session.query(DailyActivity).filter_by(user_id=uid).all()
        assert len(rows) == 1
        assert rows[0].streak_awarded is True
        assert rows[0].activity_count == 1

        await service.complete_session(
            session_id=session.session_id,
            user_id=session.user_id,
        )
        db_session.refresh(profile)
        assert profile.current_streak == 1
        rows_after = db_session.query(DailyActivity).filter_by(user_id=uid).all()
        assert len(rows_after) == 1
        assert rows_after[0].activity_count == 1

        streak_data = StreakService(db_session).get_streak_data(user_id=uid)
        assert streak_data.today_streak_awarded is True


class TestRestartRescoring:
    """Re-completing a day after a per-activity retry must reflect the new
    score WITHOUT awarding points a second time."""

    async def _start(self, db, score=8.0):
        service = SessionService(
            db,
            evaluator=StubEvaluator(default_score=score),
            feedback_generator=StubFeedbackGenerator(),
        )
        session = await service.start_session(
            user_id=_user_id(db),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        return service, session

    @staticmethod
    def _total_points(db, user_id: int) -> int:
        return sum(
            int(row.points)
            for row in db.query(SkillPoints).filter_by(user_id=user_id).all()
        )

    @pytest.mark.asyncio
    async def test_retry_speaking_rescore_does_not_double_apply_points(
        self,
        db_session,
    ):
        service, session = await self._start(db_session, score=8.0)
        uid = session.user_id

        # Complete the day with all activities scored 8.0.
        for seq in (1, 2, 3, 4):
            await service.submit_activity(
                session_id=session.session_id,
                user_id=uid,
                sequence=seq,
                user_response={"a": "b"},
            )
        scorecard1, report1 = await service.complete_session(
            session_id=session.session_id,
            user_id=uid,
        )
        assert report1.applied is True
        assert scorecard1.points_applied is True
        points_after_first = self._total_points(db_session, uid)
        assert points_after_first > 0

        # Speaking is the 4th activity (SPEAK_TIMED). Retry it with a new,
        # lower score via a second service wired with a different evaluator.
        speaking = next(
            a
            for a in service.get_session(
                session_id=session.session_id,
                user_id=uid,
            ).attempts
            if ARCHETYPE_REGISTRY[a.archetype_id].core_activity == "speak"
        )
        await service.reset_activity(
            session_id=session.session_id,
            user_id=uid,
            sequence=speaking.sequence,
        )

        service2 = SessionService(
            db_session,
            evaluator=StubEvaluator(default_score=3.0),
            feedback_generator=StubFeedbackGenerator(),
        )
        await service2.submit_activity(
            session_id=session.session_id,
            user_id=uid,
            sequence=speaking.sequence,
            user_response={"a": "redo"},
        )
        scorecard2, report2 = await service2.complete_session(
            session_id=session.session_id,
            user_id=uid,
        )

        # The rebuilt scorecard reflects the NEW speaking score.
        speaking_entry = next(
            a for a in scorecard2.activities if a["sequence"] == speaking.sequence
        )
        assert speaking_entry["raw_score"] == pytest.approx(3.0)

        # Points were applied exactly once — the retry/re-complete must not
        # award a second batch.
        assert report2.applied is False
        assert scorecard2.points_applied is True
        assert self._total_points(db_session, uid) == points_after_first
