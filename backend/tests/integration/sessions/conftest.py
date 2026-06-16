"""Shared ``db_session`` fixture for the split SessionService lifecycle tests.

Only the ``test_lifecycle_*.py`` files rely on this fixture. The other tests in
this directory (``test_session_routes``, ``test_session_dashboard_routes``) use
no ``db_session``; ``test_sessions_start_today``, ``test_pass_mark_gating`` and
``test_session_replay_and_scoring`` define their own ``db_session`` locally,
which shadows this one — so adding it here is collision-safe.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Register all models on Base.metadata.
from app import models  # noqa: F401
from app.core.database import Base
from app.modules.auth.models import User, UserProfile
from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
)
from app.modules.preferences.models import UserCoursePreference
from app.modules.progress.models import SkillPoints, SkillPointsLog
from app.modules.sessions.models import (
    ActivityAttempt,
    ActivityEvaluation,
    ActivityFeedback,
    DailySession,
    SessionScorecard,
)
from app.modules.skills.models import Skill
from app.modules.streaks.models import DailyActivity, StreakFreezeUsage

from tests.integration.sessions._lifecycle_support import _seed_world


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            Skill.__table__,
            SkillPoints.__table__,
            SkillPointsLog.__table__,
            CurriculumWeek.__table__,
            CurriculumDay.__table__,
            TaskArchetype.__table__,
            DailySession.__table__,
            ActivityAttempt.__table__,
            ActivityEvaluation.__table__,
            ActivityFeedback.__table__,
            SessionScorecard.__table__,
            UserCoursePreference.__table__,
            UserProfile.__table__,
            DailyActivity.__table__,
            StreakFreezeUsage.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        _seed_world(db)
        yield db
    finally:
        db.close()
        engine.dispose()
