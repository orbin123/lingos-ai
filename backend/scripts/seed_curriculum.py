"""Idempotent seeder for curriculum + archetype tables.

Usage:
    uv run python -m scripts.seed_curriculum

Source of truth:
  - Curriculum: `app.modules.curriculum.data.load_weeks(...)`
  - Archetypes: `app.scoring.ARCHETYPE_REGISTRY`

Safe to re-run. Existing rows are updated in place; missing rows are
inserted. Rows that exist in the DB but not in the source are left alone
(use a separate `wipe_curriculum` script if you want a hard reset).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Allow `uv run python scripts/seed_curriculum.py` from anywhere.
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))

from sqlalchemy.orm import Session  # noqa: E402

from app.core.database import SessionLocal  # noqa: E402
from app.modules.curriculum.data import load_weeks  # noqa: E402
from app.modules.curriculum.models import (  # noqa: E402
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
    ThemeType,
    CoreActivity,
)
from app.modules.skills.models import Skill  # noqa: E402
from app.modules.skills.seed_data import SKILL_SEED  # noqa: E402
from app.scoring import ARCHETYPE_REGISTRY, CourseLength  # noqa: E402


logger = logging.getLogger(__name__)


# ── Skill seeding ──────────────────────────────────────────────────


def seed_skills(db: Session) -> tuple[int, int]:
    """Upsert the 7 canonical sub-skill master rows. Returns (inserted, updated).

    The authoritative fix for the empty-`skills` table lives in the Alembic data
    migration; this is defense-in-depth so a freshly seeded environment has
    skills even if the seeder is run without migrations. Idempotent.
    """
    inserted = updated = 0
    for name, description, display_label in SKILL_SEED:
        row = db.query(Skill).filter_by(name=name).one_or_none()
        if row is None:
            db.add(
                Skill(name=name, description=description, display_label=display_label)
            )
            inserted += 1
        else:
            row.description = description
            row.display_label = display_label
            updated += 1
    db.flush()
    return inserted, updated


# ── Archetype seeding ──────────────────────────────────────────────


def seed_archetypes(db: Session) -> tuple[int, int]:
    """Upsert every archetype from the Python registry. Returns (inserted, updated)."""
    inserted = updated = 0
    for spec in ARCHETYPE_REGISTRY.values():
        row = db.get(TaskArchetype, spec.archetype_id)
        payload = dict(
            name=spec.name,
            core_activity=CoreActivity(spec.core_activity),
            description=spec.description,
            ui_widget=spec.ui_widget,
            themes_supported=list(spec.themes_supported),
            cefr_min=spec.cefr_min,
            cefr_max=spec.cefr_max,
            weight_map=dict(spec.weight_map),
            rubric=list(spec.rubric),
            mvp=spec.mvp,
        )
        if row is None:
            db.add(TaskArchetype(archetype_id=spec.archetype_id, **payload))
            inserted += 1
        else:
            for field, value in payload.items():
                setattr(row, field, value)
            updated += 1
    db.flush()
    return inserted, updated


# ── Curriculum seeding ─────────────────────────────────────────────


def _upsert_week(db: Session, course_length: CourseLength, week_record) -> CurriculumWeek:
    row = db.query(CurriculumWeek).filter_by(week_id=week_record.week_id).one_or_none()
    payload = dict(
        course_length=course_length.value,
        week_number=week_record.week_number,
        theme_type=ThemeType(week_record.theme_type),
        title=week_record.title,
        cefr_level=week_record.cefr_level,
        sub_level_min=week_record.sub_level_min,
        sub_level_max=week_record.sub_level_max,
        learning_goal=week_record.learning_goal,
    )
    if row is None:
        row = CurriculumWeek(week_id=week_record.week_id, **payload)
        db.add(row)
        db.flush()
        return row
    for field, value in payload.items():
        setattr(row, field, value)
    db.flush()
    return row


def _upsert_day(db: Session, week_pk: int, day_record) -> CurriculumDay:
    row = db.query(CurriculumDay).filter_by(day_id=day_record.day_id).one_or_none()
    payload = dict(
        week_id=week_pk,
        day_number=day_record.day_number,
        topic=day_record.topic,
        explanation_brief=day_record.explanation_brief,
        default_activities=list(day_record.default_activities),
        mandatory_activities=list(day_record.mandatory_activities),
        suggested_archetypes={
            activity: list(ids)
            for activity, ids in day_record.suggested_archetypes.items()
        },
    )
    if row is None:
        row = CurriculumDay(day_id=day_record.day_id, **payload)
        db.add(row)
        return row
    for field, value in payload.items():
        setattr(row, field, value)
    return row


def seed_course(db: Session, course_length: CourseLength) -> tuple[int, int]:
    """Upsert all weeks + days for one course length. Returns (weeks, days)."""
    weeks_written = days_written = 0
    for week_record in load_weeks(course_length):
        week_row = _upsert_week(db, course_length, week_record)
        weeks_written += 1
        for day_record in week_record.days:
            _upsert_day(db, week_row.id, day_record)
            days_written += 1
    db.flush()
    return weeks_written, days_written


def seed_all(db: Session) -> dict:
    skill_ins, skill_upd = seed_skills(db)
    arch_ins, arch_upd = seed_archetypes(db)
    w24, d24 = seed_course(db, CourseLength.WEEKS_24)
    w48, d48 = seed_course(db, CourseLength.WEEKS_48)
    return {
        "skills": {"inserted": skill_ins, "updated": skill_upd},
        "archetypes": {"inserted": arch_ins, "updated": arch_upd},
        "weeks_24w": w24, "days_24w": d24,
        "weeks_48w": w48, "days_48w": d48,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    with SessionLocal() as db:
        try:
            report = seed_all(db)
            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Seed failed — rolled back")
            raise
    logger.info("Seed complete: %s", report)


if __name__ == "__main__":
    main()
