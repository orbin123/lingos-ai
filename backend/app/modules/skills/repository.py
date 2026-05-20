"""Data access for the Skill master table."""

from sqlalchemy.orm import Session

from app.modules.skills.models import Skill


class SkillRepository:
    """Read-only access to the Skill master table.

    Skills are seeded once and rarely change — so no create/update/delete here.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[Skill]:
        """Return all 7 skills, ordered by id (insertion order)."""
        return self.db.query(Skill).order_by(Skill.id).all()

    def get_by_name(self, name: str) -> Skill | None:
        """Look up a skill by its canonical name (e.g. 'grammar')."""
        return self.db.query(Skill).filter(Skill.name == name).first()

    def name_to_id_map(self) -> dict[str, int]:
        """Convenience: {'grammar': 1, 'vocabulary': 2, ...}.

        Used by services that get skill names from LLM/rules and need ids.
        """
        return {s.name: s.id for s in self.get_all()}

    def display_label_map(self) -> dict[str, str]:
        """Convenience: {'grammar': 'Grammar', 'expression': 'Thought Organization', …}.

        Used by services that ship sub-skill payloads to the frontend so the
        UI doesn't need to mirror the label mapping. Falls back to the
        identifier when display_label is empty.
        """
        return {s.name: (s.display_label or s.name) for s in self.get_all()}