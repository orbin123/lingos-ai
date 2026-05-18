"""Scoring constants — values are well-formed and self-consistent."""

from app.scoring.constants import (
    MAX_POINTS_PER_SUBSKILL,
    POINTS_PER_DASHBOARD_UNIT,
    REWARDS_24W,
    REWARDS_48W,
    SUB_SKILLS,
    SUB_SKILL_ALIASES,
    TIER_BOUNDARIES,
    Tier,
)


class TestSubSkills:
    def test_seven_sub_skills(self):
        assert len(SUB_SKILLS) == 7

    def test_sub_skills_unique(self):
        assert len(set(SUB_SKILLS)) == 7

    def test_uses_legacy_db_names(self):
        # See RESTRUCTURE_DECISIONS.md §2 — keep legacy DB names as identifiers.
        assert "expression" in SUB_SKILLS
        assert "comprehension" in SUB_SKILLS
        assert "tone" in SUB_SKILLS
        # Doc names must NOT appear as identifiers.
        assert "thought_org" not in SUB_SKILLS
        assert "listening" not in SUB_SKILLS
        assert "tone_social" not in SUB_SKILLS

    def test_aliases_resolve_to_legacy_names(self):
        for doc_name, code_name in SUB_SKILL_ALIASES.items():
            assert code_name in SUB_SKILLS, (
                f"alias {doc_name!r} → {code_name!r} but {code_name!r} not in SUB_SKILLS"
            )

    def test_no_alias_collides_with_legacy_name(self):
        assert not (set(SUB_SKILL_ALIASES) & set(SUB_SKILLS))


class TestTiers:
    def test_every_tier_has_a_boundary(self):
        assert set(TIER_BOUNDARIES) == set(Tier)

    def test_boundaries_are_strictly_decreasing(self):
        ordered = [Tier.EXCELLENT, Tier.GOOD, Tier.AVERAGE, Tier.POOR, Tier.VERY_POOR]
        values = [TIER_BOUNDARIES[t] for t in ordered]
        assert values == sorted(values, reverse=True)
        assert len(set(values)) == len(values)  # no duplicates

    def test_boundary_floor_is_zero(self):
        assert TIER_BOUNDARIES[Tier.VERY_POOR] == 0.0


class TestRewardTables:
    def test_every_tier_in_both_tables(self):
        assert set(REWARDS_24W) == set(Tier)
        assert set(REWARDS_48W) == set(Tier)

    def test_24w_rewards_match_decisions(self):
        assert REWARDS_24W == {
            Tier.EXCELLENT: 55,
            Tier.GOOD: 40,
            Tier.AVERAGE: 24,
            Tier.POOR: 10,
            Tier.VERY_POOR: 0,
        }

    def test_48w_rewards_match_decisions(self):
        assert REWARDS_48W == {
            Tier.EXCELLENT: 28,
            Tier.GOOD: 20,
            Tier.AVERAGE: 12,
            Tier.POOR: 5,
            Tier.VERY_POOR: 0,
        }

    def test_24w_rewards_strictly_higher_than_48w_per_tier(self):
        # Same tier should always reward more on the shorter (more intensive) course.
        for tier in (Tier.EXCELLENT, Tier.GOOD, Tier.AVERAGE, Tier.POOR):
            assert REWARDS_24W[tier] > REWARDS_48W[tier]


class TestDashboardConstants:
    def test_dashboard_unit_is_1000(self):
        assert POINTS_PER_DASHBOARD_UNIT == 1000

    def test_max_points_is_10x_dashboard_unit(self):
        assert MAX_POINTS_PER_SUBSKILL == 10 * POINTS_PER_DASHBOARD_UNIT
