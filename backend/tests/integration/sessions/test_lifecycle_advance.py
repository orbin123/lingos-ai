"""Day advancement + session ownership/not-found.

Split out of the former monolithic ``test_session_lifecycle.py``.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    ThemeType,
)
from app.modules.preferences.models import UserCoursePreference
from app.modules.sessions.exceptions import (
    SessionAdvanceBlocked,
    SessionNotFound,
)
from app.modules.sessions.models import SessionStatus
from app.modules.sessions.service import SessionService
from app.scoring import CourseLength

from tests.integration.sessions._lifecycle_support import (
    _add_completed_daily_session,
    _add_curriculum_day,
    _user_id,
)


class TestAdvanceDay:
    def _set_preference(self, db, *, user_id: int, week: int, day: int):
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

    def test_advance_day_after_completed_current_day(self, db_session):
        user_id = _user_id(db_session)
        self._set_preference(db_session, user_id=user_id, week=9, day=3)
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_24_09_03",
        )

        service = SessionService(db_session)
        week, day = service.advance_day(user_id=user_id)

        assert (week, day) == (9, 4)
        pref = db_session.query(UserCoursePreference).filter_by(user_id=user_id).one()
        assert pref.current_week == 9
        assert pref.current_day_in_week == 4
        assert pref.last_completed_on is not None

    def test_advance_day_blocks_when_current_day_is_not_completed(self, db_session):
        user_id = _user_id(db_session)
        self._set_preference(db_session, user_id=user_id, week=9, day=3)
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_24_09_03",
            status=SessionStatus.IN_PROGRESS,
        )

        service = SessionService(db_session)
        with pytest.raises(SessionAdvanceBlocked):
            service.advance_day(user_id=user_id)

    def test_advance_day_rolls_day_7_into_next_week(self, db_session):
        user_id = _user_id(db_session)
        week9 = db_session.query(CurriculumWeek).filter_by(week_number=9).one()
        _add_curriculum_day(db_session, week=week9, day_number=7)
        week10 = CurriculumWeek(
            week_id="wk_24_10",
            course_length="24w",
            week_number=10,
            theme_type=ThemeType.VOCABULARY,
            title="Next week",
            cefr_level="A2",
            sub_level_min=3,
            sub_level_max=3,
            learning_goal="More practice.",
        )
        db_session.add(week10)
        db_session.flush()
        _add_curriculum_day(db_session, week=week10, day_number=1)
        db_session.commit()
        self._set_preference(db_session, user_id=user_id, week=9, day=7)
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_24_09_07",
        )

        service = SessionService(db_session)
        assert service.advance_day(user_id=user_id) == (10, 1)

    def test_advance_day_blocks_at_course_end(self, db_session):
        user_id = _user_id(db_session)
        week5 = db_session.query(CurriculumWeek).filter_by(week_number=9).one()
        _add_curriculum_day(db_session, week=week5, day_number=7)
        self._set_preference(db_session, user_id=user_id, week=9, day=7)
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_24_09_07",
        )

        service = SessionService(db_session)
        with pytest.raises(SessionAdvanceBlocked):
            service.advance_day(user_id=user_id)

    def test_advance_day_moves_48w_learner_to_depth_day(self, db_session):
        """A 48w learner who finishes week-1 day-1 (`day_48_01_01`) must land on
        the even-pass depth day `day_48_01_02`, not skip it."""
        user_id = _user_id(db_session)
        week1_48 = CurriculumWeek(
            week_id="wk_48_01",
            course_length="48w",
            week_number=1,
            theme_type=ThemeType.GRAMMAR,
            title="Simple Present (base)",
            cefr_level="A1",
            sub_level_min=1,
            sub_level_max=2,
            learning_goal="Simple present subject-verb agreement.",
        )
        db_session.add(week1_48)
        db_session.flush()
        for day_number, day_id in ((1, "day_48_01_01"), (2, "day_48_01_02")):
            db_session.add(
                CurriculumDay(
                    day_id=day_id,
                    week_id=week1_48.id,
                    day_number=day_number,
                    topic=f"48w day {day_number}",
                    explanation_brief="brief",
                    default_activities=["read", "write"],
                    mandatory_activities=["read"],
                    suggested_archetypes={"read": ["READ_CLOZE"]},
                )
            )
        db_session.commit()

        pref = UserCoursePreference(
            user_id=user_id,
            course_length="48w",
            tasks_per_day=4,
            allow_read=True,
            allow_write=True,
            allow_listen=True,
            allow_speak=True,
            current_week=1,
            current_day_in_week=1,
            current_day_started_at=datetime.now(timezone.utc),
        )
        db_session.add(pref)
        db_session.commit()
        _add_completed_daily_session(
            db_session,
            user_id=user_id,
            day_id="day_48_01_01",
        )

        service = SessionService(db_session)
        assert service.advance_day(user_id=user_id) == (1, 2)
        pref = db_session.query(UserCoursePreference).filter_by(user_id=user_id).one()
        assert pref.course_length == "48w"
        assert (pref.current_week, pref.current_day_in_week) == (1, 2)


class TestOwnership:
    def test_unknown_session_raises_not_found(self, db_session):
        # next_activity is sync (no LLM); a plain sync test is fine.
        service = SessionService(db_session)
        with pytest.raises(SessionNotFound):
            service.next_activity(session_id="does-not-exist", user_id=_user_id(db_session))

    @pytest.mark.asyncio
    async def test_other_users_session_is_invisible(self, db_session):
        service = SessionService(db_session)
        session = await service.start_session(
            user_id=_user_id(db_session),
            day_id="day_24_09_03",
            course_length=CourseLength.WEEKS_24,
            tasks_per_day=2,
            allowed_activities={"read", "write"},
        )
        with pytest.raises(SessionNotFound):
            service.next_activity(session_id=session.session_id, user_id=99999)
