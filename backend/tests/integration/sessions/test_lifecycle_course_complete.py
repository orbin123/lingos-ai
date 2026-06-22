"""Course-completion stamping: ``UserCoursePreference.course_completed_at``.

The timestamp is set exactly once — the moment a learner finishes the *final*
day of their course (last week, day 7) and their progress pointer is genuinely
parked there. These tests pin both the happy path and the guards that keep a
preview/override completion of the final day from false-triggering.

In the seeded world only week 9 (24w) exists, so ``max_week`` resolves to 9 and
week 9 / day 7 is the course's final day.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.modules.curriculum.models import CurriculumDay, CurriculumWeek
from app.modules.preferences.models import UserCoursePreference
from app.modules.sessions.evaluator import StubEvaluator
from app.modules.sessions.feedback_generator import StubFeedbackGenerator
from app.modules.sessions.models import DailySession, SessionStatus
from app.modules.sessions.service import SessionService
from app.scoring import CourseLength

from tests.integration.sessions._lifecycle_support import (
    _add_completed_daily_session,
    _add_curriculum_day,
    _user_id,
)


def _set_preference(db, *, user_id: int, week: int, day: int) -> UserCoursePreference:
    pref = UserCoursePreference(
        user_id=user_id,
        course_length="24w",
        tasks_per_day=4,
        allow_read=True,
        allow_write=True,
        allow_listen=True,
        allow_speak=True,
        current_week=week,
        current_day_in_week=day,
        current_day_started_at=datetime.now(timezone.utc),
    )
    db.add(pref)
    db.commit()
    return pref


def _build_session(db, *, user_id: int, day_id: str) -> DailySession:
    """A completed final-day session row to feed the guard directly."""
    return _add_completed_daily_session(db, user_id=user_id, day_id=day_id)


class TestMarkCourseComplete:
    """Direct unit coverage of ``_mark_course_complete_if_final``."""

    def test_final_day_completion_stamps_timestamp(self, db_session):
        user_id = _user_id(db_session)
        week9 = db_session.query(CurriculumWeek).filter_by(week_number=9).one()
        _add_curriculum_day(db_session, week=week9, day_number=7)
        db_session.commit()
        pref = _set_preference(db_session, user_id=user_id, week=9, day=7)
        session = _build_session(db_session, user_id=user_id, day_id="day_24_09_07")

        now = datetime.now(timezone.utc)
        SessionService(db_session)._mark_course_complete_if_final(
            session=session, now=now
        )
        db_session.commit()
        db_session.refresh(pref)

        assert pref.course_completed_at is not None

    def test_non_final_day_does_not_stamp(self, db_session):
        user_id = _user_id(db_session)
        pref = _set_preference(db_session, user_id=user_id, week=9, day=3)
        # day_24_09_03 is seeded by the world builder.
        session = _build_session(db_session, user_id=user_id, day_id="day_24_09_03")

        SessionService(db_session)._mark_course_complete_if_final(
            session=session, now=datetime.now(timezone.utc)
        )
        db_session.commit()
        db_session.refresh(pref)

        assert pref.course_completed_at is None

    def test_preview_of_final_day_with_pointer_elsewhere_does_not_stamp(
        self, db_session
    ):
        """Learner sitting at week 9 / day 3 previews the final day. The session
        is the final day, but the pointer is not — so it must not stamp."""
        user_id = _user_id(db_session)
        week9 = db_session.query(CurriculumWeek).filter_by(week_number=9).one()
        _add_curriculum_day(db_session, week=week9, day_number=7)
        db_session.commit()
        pref = _set_preference(db_session, user_id=user_id, week=9, day=3)
        session = _build_session(db_session, user_id=user_id, day_id="day_24_09_07")

        SessionService(db_session)._mark_course_complete_if_final(
            session=session, now=datetime.now(timezone.utc)
        )
        db_session.commit()
        db_session.refresh(pref)

        assert pref.course_completed_at is None

    def test_completing_earlier_day_while_pointer_at_final_does_not_stamp(
        self, db_session
    ):
        """Pointer is at the final day, but the just-completed session is an
        earlier day (a preview/replay). The session-day check must block it."""
        user_id = _user_id(db_session)
        week9 = db_session.query(CurriculumWeek).filter_by(week_number=9).one()
        _add_curriculum_day(db_session, week=week9, day_number=7)
        db_session.commit()
        pref = _set_preference(db_session, user_id=user_id, week=9, day=7)
        session = _build_session(db_session, user_id=user_id, day_id="day_24_09_03")

        SessionService(db_session)._mark_course_complete_if_final(
            session=session, now=datetime.now(timezone.utc)
        )
        db_session.commit()
        db_session.refresh(pref)

        assert pref.course_completed_at is None

    def test_idempotent_does_not_move_timestamp(self, db_session):
        user_id = _user_id(db_session)
        week9 = db_session.query(CurriculumWeek).filter_by(week_number=9).one()
        _add_curriculum_day(db_session, week=week9, day_number=7)
        db_session.commit()
        pref = _set_preference(db_session, user_id=user_id, week=9, day=7)
        session = _build_session(db_session, user_id=user_id, day_id="day_24_09_07")

        first = datetime.now(timezone.utc) - timedelta(days=1)
        service = SessionService(db_session)
        service._mark_course_complete_if_final(session=session, now=first)
        db_session.commit()
        db_session.refresh(pref)
        stamped = pref.course_completed_at
        assert stamped is not None

        # A second pass (e.g. final-day restart/replay) must leave it untouched.
        service._mark_course_complete_if_final(
            session=session, now=datetime.now(timezone.utc)
        )
        db_session.commit()
        db_session.refresh(pref)
        assert pref.course_completed_at == stamped


class TestCompleteSessionStampsCourseComplete:
    """End-to-end: completing the final-day session via the real complete path
    persists ``course_completed_at`` (proves the guard is wired in)."""

    @staticmethod
    def _add_full_day7(db) -> CurriculumDay:
        week9 = db.query(CurriculumWeek).filter_by(week_number=9).one()
        day = CurriculumDay(
            day_id="day_24_09_07",
            week_id=week9.id,
            day_number=7,
            topic="Final day",
            explanation_brief="Wrap-up practice.",
            default_activities=["read", "write", "listen", "speak"],
            mandatory_activities=["read", "write"],
            suggested_archetypes={
                "read": ["READ_CLOZE", "READ_COMP_MCQ"],
                "write": ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"],
                "listen": ["LISTEN_CLOZE"],
                "speak": ["SPEAK_TIMED"],
            },
        )
        db.add(day)
        db.commit()
        return day

    @pytest.mark.asyncio
    async def test_complete_final_day_session_marks_course_complete(self, db_session):
        user_id = _user_id(db_session)
        self._add_full_day7(db_session)
        pref = _set_preference(db_session, user_id=user_id, week=9, day=7)

        service = SessionService(
            db_session,
            evaluator=StubEvaluator(default_score=8.0),
            feedback_generator=StubFeedbackGenerator(),
        )
        session = await service.start_session(
            user_id=user_id,
            day_id="day_24_09_07",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=4,
            allowed_activities={"read", "write", "listen", "speak"},
        )
        for seq in range(1, 5):
            await service.submit_activity(
                session_id=session.session_id,
                user_id=user_id,
                sequence=seq,
                user_response={"answer": "hello"},
            )

        await service.complete_session(
            session_id=session.session_id,
            user_id=user_id,
        )

        refreshed = service.get_session(session_id=session.session_id, user_id=user_id)
        assert refreshed.status is SessionStatus.COMPLETED
        db_session.refresh(pref)
        assert pref.course_completed_at is not None
