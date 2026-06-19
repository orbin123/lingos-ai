"""Guard the canonical skill seed list against the scoring source of truth.

These rows MUST exist in every environment — an empty `skills` table is what
caused the production `KeyError: 'grammar'` on `/diagnosis/submit`. The seed
list feeds both the Alembic seed migration and `scripts/seed_curriculum.py`, so
keeping it in lock-step with `SUB_SKILLS` here catches a future sub-skill added
without a matching seed row/label.
"""

from app.modules.skills.seed_data import SKILL_SEED
from app.scoring import SUB_SKILLS


class TestSkillSeed:
    def test_covers_every_sub_skill(self):
        seeded_names = {name for name, _description, _label in SKILL_SEED}
        assert seeded_names == set(SUB_SKILLS)

    def test_no_duplicate_names(self):
        names = [name for name, _description, _label in SKILL_SEED]
        assert len(names) == len(set(names)) == len(SUB_SKILLS)

    def test_every_row_has_a_nonempty_display_label(self):
        for name, _description, display_label in SKILL_SEED:
            assert display_label, f"missing display_label for {name!r}"

    def test_description_mirrors_name(self):
        for name, description, _label in SKILL_SEED:
            assert description == name
