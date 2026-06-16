"""Curriculum/archetype seeding fixtures.

`scripts/seed_curriculum.py` is tracked in git (it predates the `backend/scripts`
.gitignore rule), so it ships in CI and can be reused directly — no need to
vendor the seeding logic into the test tree.
"""

from __future__ import annotations

import pytest

from scripts.seed_curriculum import seed_archetypes as _seed_archetypes
from tests.factories.progress import seed_skills as _seed_skills


@pytest.fixture
def seed_archetypes():
    """Return the archetype seeder; call as `seed_archetypes(db_session)`."""
    return _seed_archetypes


@pytest.fixture
def seed_skills():
    """Return the sub-skill seeder; call as `seed_skills(db_session)`."""
    return _seed_skills


@pytest.fixture
def seeded_db(db_session):
    """A `db_session` with archetypes + the 7 sub-skills already committed."""
    _seed_skills(db_session)
    _seed_archetypes(db_session)
    db_session.commit()
    return db_session
