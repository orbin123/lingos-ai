"""Pure-math tests for the scoring engine."""

import pytest

from app.scoring.constants import CourseLength, MAX_POINTS_PER_SUBSKILL, Tier
from app.scoring.engine import (
    aggregate_session,
    apply_to_totals,
    base_reward,
    build_session_aggregation,
    distribute,
    points_to_dashboard,
    tier_for_score,
)
from app.scoring.types import ActivityScore


class TestTierForScore:
    @pytest.mark.parametrize(
        "score,expected",
        [
            # Edges of every tier — boundary inclusive on low side.
            (10.0, Tier.EXCELLENT),
            (8.0, Tier.EXCELLENT),
            (7.99, Tier.GOOD),
            (6.0, Tier.GOOD),
            (5.99, Tier.AVERAGE),
            (4.0, Tier.AVERAGE),
            (3.99, Tier.POOR),
            (2.0, Tier.POOR),
            (1.99, Tier.VERY_POOR),
            (0.0, Tier.VERY_POOR),
        ],
    )
    def test_boundary_rule(self, score, expected):
        assert tier_for_score(score) == expected

    def test_non_integer_score_is_supported(self):
        # Evaluator may return floats (e.g. 7.5). Doc §13.7 allows this.
        assert tier_for_score(7.5) == Tier.GOOD


class TestBaseReward:
    def test_24w_excellent_is_55(self):
        assert base_reward(9.0, CourseLength.WEEKS_24) == 55

    def test_48w_excellent_is_28(self):
        assert base_reward(9.0, CourseLength.WEEKS_48) == 28

    def test_24w_good_is_40(self):
        assert base_reward(7.0, CourseLength.WEEKS_24) == 40

    def test_24w_average_is_24(self):
        assert base_reward(5.0, CourseLength.WEEKS_24) == 24

    def test_24w_poor_is_10(self):
        assert base_reward(3.0, CourseLength.WEEKS_24) == 10

    def test_very_poor_is_zero_in_both_tracks(self):
        assert base_reward(1.0, CourseLength.WEEKS_24) == 0
        assert base_reward(1.0, CourseLength.WEEKS_48) == 0

    def test_boundary_scores_use_higher_tier_reward(self):
        # 8.0 → Excellent (55), not Good (40).
        assert base_reward(8.0, CourseLength.WEEKS_24) == 55


class TestDistribute:
    def test_splits_proportional_to_weights(self):
        result = distribute(40, {"grammar": 0.25, "vocabulary": 0.75})
        assert result == {"grammar": 10.0, "vocabulary": 30.0}

    def test_single_skill_gets_full_reward(self):
        assert distribute(55, {"vocabulary": 1.00}) == {"vocabulary": 55.0}

    def test_rejects_weights_not_summing_to_one(self):
        with pytest.raises(ValueError, match="must be 1.0"):
            distribute(40, {"grammar": 0.5, "vocabulary": 0.4})

    def test_accepts_weights_within_tolerance(self):
        # 0.333..*3 sums to 0.999... within ARCHETYPE_WEIGHT_TOLERANCE.
        weights = {"grammar": 1 / 3, "vocabulary": 1 / 3, "fluency": 1 / 3}
        result = distribute(30, weights)
        assert sum(result.values()) == pytest.approx(30.0)


class TestAggregateSession:
    def test_aggregates_single_activity(self):
        activities = [
            ActivityScore(
                archetype_id="X",
                raw_score=7.0,  # Good → 40 (24w)
                weight_map={"grammar": 0.5, "vocabulary": 0.5},
            ),
        ]
        result = aggregate_session(activities, CourseLength.WEEKS_24)
        assert result == {"grammar": 20, "vocabulary": 20}

    def test_rounds_once_per_subskill_after_summing(self):
        # Three Average (24 pts) activities each contributing 4.8 to grammar
        # and 19.2 to vocab.
        # Per activity rounded: grammar 5, vocab 19 → sum 15/57 ← WRONG.
        # Engine sums first (14.4 / 57.6) then rounds (14 / 58) ← CORRECT.
        activities = [
            ActivityScore(
                archetype_id="X",
                raw_score=4.0,
                weight_map={"grammar": 0.2, "vocabulary": 0.8},
            ),
        ] * 3
        result = aggregate_session(activities, CourseLength.WEEKS_24)
        assert result == {"grammar": 14, "vocabulary": 58}

    def test_empty_activity_list_returns_empty_dict(self):
        assert aggregate_session([], CourseLength.WEEKS_24) == {}

    def test_all_very_poor_yields_zero(self):
        activities = [
            ActivityScore(
                archetype_id="X",
                raw_score=0.5,
                weight_map={"grammar": 1.0},
            ),
        ]
        assert aggregate_session(activities, CourseLength.WEEKS_24) == {"grammar": 0}

    def test_multiple_activities_distribute_across_seven_subskills(self):
        activities = [
            ActivityScore(
                archetype_id="A",
                raw_score=8.0,  # Excellent → 55 (24w)
                weight_map={"grammar": 0.5, "vocabulary": 0.5},
            ),
            ActivityScore(
                archetype_id="B",
                raw_score=5.0,  # Average → 24 (24w)
                weight_map={"fluency": 0.5, "tone": 0.5},
            ),
        ]
        result = aggregate_session(activities, CourseLength.WEEKS_24)
        assert result == {
            "grammar": 28,       # 27.5 → 28
            "vocabulary": 28,    # 27.5 → 28
            "fluency": 12,
            "tone": 12,
        }


class TestApplyToTotals:
    def test_adds_within_range(self):
        new = apply_to_totals({"grammar": 50}, {"grammar": 3800})
        assert new == {"grammar": 3850}

    def test_clamps_at_max(self):
        new = apply_to_totals({"grammar": 200}, {"grammar": 9900})
        assert new == {"grammar": MAX_POINTS_PER_SUBSKILL}

    def test_already_at_cap_stays_at_cap(self):
        new = apply_to_totals({"grammar": 55}, {"grammar": MAX_POINTS_PER_SUBSKILL})
        assert new == {"grammar": MAX_POINTS_PER_SUBSKILL}

    def test_skill_missing_from_current_starts_at_zero(self):
        new = apply_to_totals({"grammar": 50}, {})
        assert new == {"grammar": 50}

    def test_skill_with_no_earning_passes_through_unchanged(self):
        new = apply_to_totals({"vocabulary": 10}, {"grammar": 4000, "vocabulary": 3000})
        assert new == {"grammar": 4000, "vocabulary": 3010}

    def test_does_not_mutate_inputs(self):
        earned = {"grammar": 10}
        current = {"grammar": 100}
        apply_to_totals(earned, current)
        assert earned == {"grammar": 10}
        assert current == {"grammar": 100}


class TestPointsToDashboard:
    @pytest.mark.parametrize(
        "points,expected",
        [
            (0, 0.0),
            (50, 0.1),        # 0.05 → rounds half-up to 0.1
            (949, 0.9),
            (950, 1.0),       # 0.95 → rounds half-up to 1.0
            (999, 1.0),
            (1000, 1.0),
            (1049, 1.0),      # 1.049 → 1.0
            (1050, 1.1),      # 1.05 → rounds half-up to 1.1
            (1499, 1.5),
            (1500, 1.5),      # 1.50 → 1.5
            (3814, 3.8),
            (4155, 4.2),      # 4.155 → 4.2 (deterministic via integer math)
            (10000, 10.0),
        ],
    )
    def test_rounds_half_up_at_one_decimal(self, points, expected):
        assert points_to_dashboard(points) == expected


class TestBuildSessionAggregation:
    def test_without_current_totals_emits_only_earned(self):
        activities = [
            ActivityScore(
                archetype_id="X",
                raw_score=8.0,
                weight_map={"grammar": 1.0},
            ),
        ]
        agg = build_session_aggregation(activities, CourseLength.WEEKS_24)
        assert agg.points_earned == {"grammar": 55}
        assert agg.subskill_totals_after is None
        assert agg.dashboard_after is None

    def test_with_current_totals_emits_full_snapshot(self):
        activities = [
            ActivityScore(
                archetype_id="X",
                raw_score=8.0,
                weight_map={"grammar": 1.0},
            ),
        ]
        agg = build_session_aggregation(
            activities,
            CourseLength.WEEKS_24,
            current_totals={"grammar": 3800},
        )
        assert agg.points_earned == {"grammar": 55}
        assert agg.subskill_totals_after == {"grammar": 3855}
        assert agg.dashboard_after == {"grammar": 3.9}    # 3.855 → half-up → 3.9

    def test_cap_does_not_block_earned_log(self):
        # Even at the cap, the user still sees "+N pts" — totals just stop moving.
        activities = [
            ActivityScore(
                archetype_id="X",
                raw_score=8.0,
                weight_map={"grammar": 1.0},
            ),
        ]
        agg = build_session_aggregation(
            activities,
            CourseLength.WEEKS_24,
            current_totals={"grammar": MAX_POINTS_PER_SUBSKILL},
        )
        assert agg.points_earned == {"grammar": 55}
        assert agg.subskill_totals_after == {"grammar": MAX_POINTS_PER_SUBSKILL}
        assert agg.dashboard_after == {"grammar": 10.0}
