"""Pre-deploy smoke: a fresh DB seeded from the band files has both calendars.

This is the operational sibling of `test_curriculum_v2_data` (which only
checks the in-memory records). Here we run the real `seed_curriculum`
seeder against an in-memory SQLite database and assert that:

  - `load_weeks(24w)` and `load_weeks(48w)` import cleanly (no authoring
    drift crashes the seeder),
  - the seeded DB ends up with 24w (24 weeks / 168 days) **and** 48w
    (48 weeks / 336 days) rows,
  - the seeded `topic` for sample authored days matches `file_source`
    (so `GET /api/sessions/today-plan` resolves for both tracks).

If this fails in CI, a deploy would leave a fresh Postgres missing one of
the calendars — exactly the Phase 2 failure mode the master prompt guards.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Register all models on Base.metadata.
from app import models  # noqa: F401
from app.core.database import Base
from app.modules.curriculum import file_source
from app.modules.curriculum.data import load_weeks
from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
)
from app.scoring import CourseLength
from scripts.seed_curriculum import seed_archetypes, seed_course


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            CurriculumWeek.__table__,
            CurriculumDay.__table__,
            TaskArchetype.__table__,
        ],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def test_load_weeks_imports_cleanly_for_both_calendars():
    weeks_24 = load_weeks(CourseLength.WEEKS_24)
    weeks_48 = load_weeks(CourseLength.WEEKS_48)
    assert len(weeks_24) == 24
    assert sum(len(w.days) for w in weeks_24) == 168
    assert len(weeks_48) == 48
    assert sum(len(w.days) for w in weeks_48) == 336


def test_seed_course_populates_both_calendars(db_session):
    seed_archetypes(db_session)
    w24, d24 = seed_course(db_session, CourseLength.WEEKS_24)
    w48, d48 = seed_course(db_session, CourseLength.WEEKS_48)
    db_session.commit()

    assert (w24, d24) == (24, 168)
    assert (w48, d48) == (48, 336)

    assert db_session.query(CurriculumWeek).filter_by(course_length="24w").count() == 24
    assert db_session.query(CurriculumWeek).filter_by(course_length="48w").count() == 48
    assert (
        db_session.query(CurriculumDay)
        .join(CurriculumWeek)
        .filter(CurriculumWeek.course_length == "48w")
        .count()
        == 336
    )


@pytest.mark.parametrize(
    "day_id",
    ["day_24_01_01", "day_48_01_01", "day_48_01_02"],
)
def test_seeded_topic_matches_file_source(db_session, day_id):
    """The DB topic the dashboard falls back to must equal the file topic for
    authored days on both tracks (incl. the 48w even-pass depth day)."""
    seed_archetypes(db_session)
    seed_course(db_session, CourseLength.WEEKS_24)
    seed_course(db_session, CourseLength.WEEKS_48)
    db_session.commit()

    row = db_session.query(CurriculumDay).filter_by(day_id=day_id).one()
    file_day = file_source.get_day_by_id(day_id)
    assert row.topic == file_day.topic
    assert row.topic
