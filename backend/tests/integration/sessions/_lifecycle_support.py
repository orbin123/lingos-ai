"""Shared seed helpers for the split SessionService lifecycle tests.

Extracted verbatim from the former monolithic ``test_session_lifecycle.py`` so
the ``test_lifecycle_*.py`` files share one world-builder. The ``db_session``
fixture in ``conftest.py`` calls :func:`_seed_world`; the test files call the
``_add_*`` / ``_user_id`` helpers.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.modules.auth.models import User, UserProfile
from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    ThemeType,
)
from app.modules.sessions.models import DailySession, SessionStatus
from app.modules.skills.models import Skill
from app.scoring import SUB_SKILLS
from scripts.seed_curriculum import seed_archetypes


def _seed_world(db):
    """Seed users, the 7 skills, archetypes, and one curriculum week+day."""
    user = User(email="learner@example.com", password_hash="x", name="L")
    db.add(user)
    db.flush()
    db.add(UserProfile(user_id=user.id, timezone="Asia/Kolkata"))
    for sub_skill in SUB_SKILLS:
        db.add(Skill(name=sub_skill, description=sub_skill))
    db.flush()
    seed_archetypes(db)
    week = CurriculumWeek(
        week_id="wk_24_09",
        course_length="24w",
        week_number=9,
        theme_type=ThemeType.GRAMMAR,
        title="What I Did and What I'll Do",
        cefr_level="A2",
        sub_level_min=3,
        sub_level_max=3,
        learning_goal="Past simple + future with will/going to.",
    )
    db.add(week)
    db.flush()
    day = CurriculumDay(
        day_id="day_24_09_03",
        week_id=week.id,
        day_number=3,
        topic="Past negative and questions",
        explanation_brief="didn't + base; did you/she …",
        default_activities=["read", "write", "listen", "speak"],
        mandatory_activities=["read", "write"],
        suggested_archetypes={
            "read":   ["READ_CLOZE", "READ_COMP_MCQ"],
            "write":  ["WRITE_SENT_TRANS", "WRITE_ERROR_CORR"],
            "listen": ["LISTEN_CLOZE"],
            "speak":  ["SPEAK_TIMED"],
        },
    )
    db.add(day)
    db.commit()
    return user, day


def _user_id(db) -> int:
    return db.query(User).first().id


def _add_curriculum_day(
    db,
    *,
    week: CurriculumWeek,
    day_number: int,
) -> CurriculumDay:
    day = CurriculumDay(
        day_id=f"day_24_{week.week_number:02d}_{day_number:02d}",
        week_id=week.id,
        day_number=day_number,
        topic=f"Day {day_number}",
        explanation_brief="Practice brief.",
        default_activities=["read", "write"],
        mandatory_activities=["read"],
        suggested_archetypes={
            "read": ["READ_CLOZE"],
            "write": ["WRITE_SENT_TRANS"],
        },
    )
    db.add(day)
    db.flush()
    return day


def _add_completed_daily_session(
    db,
    *,
    user_id: int,
    day_id: str,
    status: SessionStatus = SessionStatus.COMPLETED,
) -> DailySession:
    session = DailySession(
        session_id=f"session-{day_id}-{status.value}",
        user_id=user_id,
        day_id=day_id,
        course_length="24w",
        status=status,
        is_first_attempt=True,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc)
        if status is SessionStatus.COMPLETED
        else None,
    )
    db.add(session)
    db.commit()
    return session
