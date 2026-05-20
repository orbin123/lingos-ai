"""DB-level tests for the v2 curriculum tables and seeder.

Uses an in-memory SQLite engine + `Base.metadata.create_all` (the same
pattern as `test_daily_plan_repository.py`). Migrations themselves are
exercised separately via `alembic upgrade`.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

# Side-effect import: registers every ORM model on Base.metadata.
from app import models  # noqa: F401
from app.core.database import Base
from app.modules.curriculum.models import (
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
    ThemeType,
)
from app.modules.curriculum.repository import (
    CurriculumDayRepository,
    CurriculumWeekRepository,
    TaskArchetypeRepository,
)
from app.scoring import ARCHETYPE_REGISTRY, CourseLength
from scripts.seed_curriculum_v2 import (
    seed_all,
    seed_archetypes,
    seed_course,
)


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
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


# ── Model invariants ───────────────────────────────────────────────


class TestModels:
    def test_week_day_round_trip(self, db_session):
        week = CurriculumWeek(
            week_id="wk_24_99",
            course_length="24w",
            week_number=99,
            theme_type=ThemeType.GRAMMAR,
            title="Test",
            cefr_level="A1",
            sub_level_min=1,
            sub_level_max=2,
            learning_goal="Stay alive.",
        )
        db_session.add(week)
        db_session.flush()
        day = CurriculumDay(
            day_id="day_24_99_01",
            week_id=week.id,
            day_number=1,
            topic="Test topic",
            explanation_brief="Test brief.",
            default_activities=["read", "write"],
            mandatory_activities=["read"],
            suggested_archetypes={"read": ["READ_CLOZE"]},
        )
        db_session.add(day)
        db_session.commit()

        fetched = (
            db_session.query(CurriculumWeek)
            .filter_by(week_id="wk_24_99")
            .one()
        )
        assert len(fetched.days) == 1
        assert fetched.days[0].topic == "Test topic"
        assert fetched.days[0].suggested_archetypes == {"read": ["READ_CLOZE"]}

    def test_unique_week_id(self, db_session):
        db_session.add(CurriculumWeek(
            week_id="wk_24_99",
            course_length="24w",
            week_number=99,
            theme_type=ThemeType.GRAMMAR,
            title="A",
            cefr_level="A1",
            sub_level_min=1, sub_level_max=2,
            learning_goal="x",
        ))
        db_session.flush()
        db_session.add(CurriculumWeek(
            week_id="wk_24_99",  # duplicate
            course_length="24w",
            week_number=100,
            theme_type=ThemeType.GRAMMAR,
            title="B",
            cefr_level="A1",
            sub_level_min=1, sub_level_max=2,
            learning_goal="y",
        ))
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_unique_course_length_week_number(self, db_session):
        db_session.add(CurriculumWeek(
            week_id="wk_24_99",
            course_length="24w",
            week_number=99,
            theme_type=ThemeType.GRAMMAR,
            title="A",
            cefr_level="A1",
            sub_level_min=1, sub_level_max=2,
            learning_goal="x",
        ))
        db_session.flush()
        db_session.add(CurriculumWeek(
            week_id="wk_24_100",
            course_length="24w",
            week_number=99,  # duplicate (course_length, week_number)
            theme_type=ThemeType.GRAMMAR,
            title="B",
            cefr_level="A1",
            sub_level_min=1, sub_level_max=2,
            learning_goal="y",
        ))
        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_cascade_delete_week_removes_days(self, db_session):
        week = CurriculumWeek(
            week_id="wk_24_99",
            course_length="24w",
            week_number=99,
            theme_type=ThemeType.GRAMMAR,
            title="A",
            cefr_level="A1",
            sub_level_min=1, sub_level_max=2,
            learning_goal="x",
        )
        db_session.add(week)
        db_session.flush()
        db_session.add(CurriculumDay(
            day_id="day_24_99_01",
            week_id=week.id,
            day_number=1,
            topic="t",
            explanation_brief="b",
            default_activities=["read"],
            mandatory_activities=["read"],
            suggested_archetypes={"read": ["READ_CLOZE"]},
        ))
        db_session.commit()

        db_session.delete(week)
        db_session.commit()

        assert db_session.query(CurriculumDay).count() == 0


# ── Archetype seeding ──────────────────────────────────────────────


class TestSeedArchetypes:
    def test_inserts_all_archetypes_on_empty_db(self, db_session):
        inserted, updated = seed_archetypes(db_session)
        db_session.commit()
        assert inserted == len(ARCHETYPE_REGISTRY)
        assert updated == 0
        assert db_session.query(TaskArchetype).count() == len(ARCHETYPE_REGISTRY)

    def test_is_idempotent(self, db_session):
        seed_archetypes(db_session)
        db_session.commit()
        inserted_2, updated_2 = seed_archetypes(db_session)
        db_session.commit()
        assert inserted_2 == 0
        assert updated_2 == len(ARCHETYPE_REGISTRY)
        assert db_session.query(TaskArchetype).count() == len(ARCHETYPE_REGISTRY)

    def test_db_weight_maps_match_python_registry(self, db_session):
        seed_archetypes(db_session)
        db_session.commit()
        repo = TaskArchetypeRepository(db_session)
        for spec in ARCHETYPE_REGISTRY.values():
            row = repo.get(spec.archetype_id)
            assert row is not None, spec.archetype_id
            assert row.weight_map == dict(spec.weight_map), spec.archetype_id
            assert row.ui_widget == spec.ui_widget
            assert row.cefr_min == spec.cefr_min
            assert row.cefr_max == spec.cefr_max
            assert row.themes_supported == list(spec.themes_supported)
            assert row.rubric == list(spec.rubric)
            assert row.mvp == spec.mvp

    def test_updates_existing_row_when_registry_changes(self, db_session):
        seed_archetypes(db_session)
        db_session.commit()
        row = db_session.get(TaskArchetype, "WRITE_EMAIL")
        # Simulate a stale row in the DB.
        row.description = "stale description"
        db_session.commit()
        seed_archetypes(db_session)
        db_session.commit()
        refreshed = db_session.get(TaskArchetype, "WRITE_EMAIL")
        assert refreshed.description == ARCHETYPE_REGISTRY["WRITE_EMAIL"].description


# ── Curriculum seeding ─────────────────────────────────────────────


class TestSeedCurriculum:
    def test_seeds_24w_with_correct_counts(self, db_session):
        weeks, days = seed_course(db_session, CourseLength.WEEKS_24)
        db_session.commit()
        assert weeks == 24
        assert days == 168
        assert db_session.query(CurriculumWeek).count() == 24
        assert db_session.query(CurriculumDay).count() == 168

    def test_seeds_48w_with_correct_counts(self, db_session):
        weeks, days = seed_course(db_session, CourseLength.WEEKS_48)
        db_session.commit()
        assert weeks == 48
        assert days == 336
        assert db_session.query(CurriculumWeek).count() == 48
        assert db_session.query(CurriculumDay).count() == 336

    def test_24w_and_48w_coexist(self, db_session):
        seed_course(db_session, CourseLength.WEEKS_24)
        seed_course(db_session, CourseLength.WEEKS_48)
        db_session.commit()
        assert db_session.query(CurriculumWeek).count() == 24 + 48
        assert db_session.query(CurriculumDay).count() == 168 + 336

    def test_is_idempotent(self, db_session):
        seed_course(db_session, CourseLength.WEEKS_24)
        db_session.commit()
        seed_course(db_session, CourseLength.WEEKS_24)
        db_session.commit()
        # Re-running should not duplicate rows.
        assert db_session.query(CurriculumWeek).count() == 24
        assert db_session.query(CurriculumDay).count() == 168

    def test_updates_existing_week_in_place(self, db_session):
        seed_course(db_session, CourseLength.WEEKS_24)
        db_session.commit()
        row = (
            db_session.query(CurriculumWeek)
            .filter_by(week_id="wk_24_01")
            .one()
        )
        row.title = "stale title"
        db_session.commit()
        seed_course(db_session, CourseLength.WEEKS_24)
        db_session.commit()
        refreshed = (
            db_session.query(CurriculumWeek)
            .filter_by(week_id="wk_24_01")
            .one()
        )
        assert refreshed.title == "Being and Belonging"


# ── seed_all integration ───────────────────────────────────────────


class TestSeedAll:
    def test_emits_full_report(self, db_session):
        report = seed_all(db_session)
        db_session.commit()
        assert report == {
            "archetypes": {
                "inserted": len(ARCHETYPE_REGISTRY),
                "updated": 0,
            },
            "weeks_24w": 24, "days_24w": 168,
            "weeks_48w": 48, "days_48w": 336,
        }


# ── Repository smoke ───────────────────────────────────────────────


class TestRepositories:
    def test_week_repo_lookup_by_week_id_and_number(self, db_session):
        seed_course(db_session, CourseLength.WEEKS_24)
        db_session.commit()
        repo = CurriculumWeekRepository(db_session)
        by_id = repo.get_by_week_id("wk_24_05")
        by_num = repo.get_by_number(course_length="24w", week_number=5)
        assert by_id is not None
        assert by_num is not None
        assert by_id.id == by_num.id
        assert by_id.theme_type == ThemeType.GRAMMAR
        assert by_id.title == "What I Did and What I'll Do"

    def test_day_repo_get_by_day_id(self, db_session):
        seed_course(db_session, CourseLength.WEEKS_24)
        db_session.commit()
        repo = CurriculumDayRepository(db_session)
        day = repo.get_by_day_id("day_24_02_01")
        assert day is not None
        assert day.day_number == 1
        assert day.topic.startswith("Name + age")

    def test_archetype_repo_lists_by_activity(self, db_session):
        seed_archetypes(db_session)
        db_session.commit()
        repo = TaskArchetypeRepository(db_session)
        speak_rows = repo.list_by_activity("speak")
        speak_ids = {r.archetype_id for r in speak_rows}
        expected = {
            aid for aid, spec in ARCHETYPE_REGISTRY.items()
            if spec.core_activity == "speak"
        }
        assert speak_ids == expected
