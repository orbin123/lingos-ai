"""Skill + SkillPoints factories.

`seed_skills` creates the canonical sub-skill rows (the 7 `SUB_SKILLS`) that
most session/progress tests need; `make_skill_points` attaches a running-total
row for a user. Mirrors the inline seeding in `test_session_lifecycle._seed_world`.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.progress.models import SkillPoints
from app.modules.skills.models import Skill
from app.scoring import SUB_SKILLS


def seed_skills(db: Session) -> dict[str, Skill]:
    """Create the 7 canonical sub-skill rows; return {name: Skill}.

    Idempotent: existing rows (by name) are reused.
    """
    out: dict[str, Skill] = {}
    for sub_skill in SUB_SKILLS:
        skill = db.query(Skill).filter_by(name=sub_skill).first()
        if skill is None:
            skill = Skill(name=sub_skill, description=sub_skill)
            db.add(skill)
        out[sub_skill] = skill
    db.flush()
    return out


def make_skill_points(
    db: Session,
    user,
    *,
    skill: Skill | None = None,
    skill_name: str = "grammar",
    points: int = 3000,
    display_score: float | None = None,
) -> SkillPoints:
    """Persist a `SkillPoints` row for `user` (creates the Skill if needed)."""
    if skill is None:
        skill = db.query(Skill).filter_by(name=skill_name).first()
        if skill is None:
            skill = Skill(name=skill_name, description=skill_name)
            db.add(skill)
            db.flush()
    row = SkillPoints(
        user_id=user.id,
        skill_id=skill.id,
        points=points,
        display_score=display_score if display_score is not None else round(points / 1000, 1),
    )
    db.add(row)
    db.commit()
    return row
