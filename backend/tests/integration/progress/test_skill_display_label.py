"""Tests for the display_label column on Skill (Phase 5).

Backend keeps `name` as the internal identifier (legacy: grammar / vocabulary
/ pronunciation / fluency / expression / comprehension / tone) and ships
`display_label` as the user-facing string the frontend renders.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Register all models on Base.metadata.
from app import models  # noqa: F401
from app.core.database import Base
from app.modules.skills.models import Skill
from app.modules.skills.repository import SkillRepository


_SEED: tuple[tuple[str, str], ...] = (
    ("grammar", "Grammar"),
    ("vocabulary", "Vocabulary"),
    ("pronunciation", "Pronunciation"),
    ("fluency", "Fluency"),
    ("expression", "Thought Organization"),
    ("comprehension", "Listening"),
    ("tone", "Tone & Social"),
)


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[Skill.__table__])
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    db = Session()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _seed_all(db) -> None:
    for name, label in _SEED:
        db.add(Skill(name=name, description="", display_label=label))
    db.commit()


# ── Model ──────────────────────────────────────────────────────────


class TestSkillModel:
    def test_display_label_column_round_trips(self, db_session):
        db_session.add(Skill(name="expression", display_label="Thought Organization"))
        db_session.commit()
        row = db_session.query(Skill).filter_by(name="expression").one()
        assert row.display_label == "Thought Organization"

    def test_display_label_defaults_to_empty_when_omitted(self, db_session):
        db_session.add(Skill(name="grammar"))
        db_session.commit()
        row = db_session.query(Skill).filter_by(name="grammar").one()
        assert row.display_label == ""


# ── Repository ─────────────────────────────────────────────────────


class TestDisplayLabelMap:
    def test_returns_display_labels_for_all_skills(self, db_session):
        _seed_all(db_session)
        labels = SkillRepository(db_session).display_label_map()
        assert labels == {
            "grammar": "Grammar",
            "vocabulary": "Vocabulary",
            "pronunciation": "Pronunciation",
            "fluency": "Fluency",
            "expression": "Thought Organization",
            "comprehension": "Listening",
            "tone": "Tone & Social",
        }

    def test_falls_back_to_name_when_label_empty(self, db_session):
        db_session.add(Skill(name="grammar", display_label=""))
        db_session.add(Skill(name="expression", display_label="Thought Organization"))
        db_session.commit()
        labels = SkillRepository(db_session).display_label_map()
        assert labels == {
            "grammar": "grammar",  # fell back
            "expression": "Thought Organization",  # explicit
        }

    def test_uses_legacy_identifiers_not_doc_aliases(self, db_session):
        """Identifiers stay as legacy DB names — display_label is the only
        thing that uses the friendlier spec wording."""
        _seed_all(db_session)
        labels = SkillRepository(db_session).display_label_map()
        # Identifiers (keys) MUST be legacy.
        assert "expression" in labels and "thought_org" not in labels
        assert "comprehension" in labels and "listening" not in labels
        # Tone keeps its identifier; only the label changes.
        assert "tone" in labels and "tone_social" not in labels
        # Labels (values) use the friendlier spec wording.
        assert labels["expression"] == "Thought Organization"
        assert labels["comprehension"] == "Listening"
        assert labels["tone"] == "Tone & Social"
