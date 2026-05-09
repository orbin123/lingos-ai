"""Unit tests for PointsCalculator — pure logic, no database required."""

from decimal import Decimal

import pytest

from app.modules.progress.service import (
    CourseLength,
    PerformanceRating,
    PointsCalculator,
)


class TestRatePerformance:
    """Verify numeric score → performance tier mapping."""

    def test_excellent_at_9_0(self):
        assert PointsCalculator._rate_performance(Decimal("9.0")) == PerformanceRating.EXCELLENT

    def test_excellent_above_9_0(self):
        assert PointsCalculator._rate_performance(Decimal("9.5")) == PerformanceRating.EXCELLENT

    def test_excellent_max(self):
        assert PointsCalculator._rate_performance(Decimal("10.0")) == PerformanceRating.EXCELLENT

    def test_good_at_7_0(self):
        assert PointsCalculator._rate_performance(Decimal("7.0")) == PerformanceRating.GOOD

    def test_good_above_7_0(self):
        assert PointsCalculator._rate_performance(Decimal("7.5")) == PerformanceRating.GOOD

    def test_good_just_below_excellent(self):
        assert PointsCalculator._rate_performance(Decimal("8.9")) == PerformanceRating.GOOD

    def test_average_at_5_0(self):
        assert PointsCalculator._rate_performance(Decimal("5.0")) == PerformanceRating.AVERAGE

    def test_average_above_5_0(self):
        assert PointsCalculator._rate_performance(Decimal("5.5")) == PerformanceRating.AVERAGE

    def test_average_just_below_good(self):
        assert PointsCalculator._rate_performance(Decimal("6.9")) == PerformanceRating.AVERAGE

    def test_poor_at_3_0(self):
        assert PointsCalculator._rate_performance(Decimal("3.0")) == PerformanceRating.POOR

    def test_poor_above_3_0(self):
        assert PointsCalculator._rate_performance(Decimal("3.5")) == PerformanceRating.POOR

    def test_poor_just_below_average(self):
        assert PointsCalculator._rate_performance(Decimal("4.9")) == PerformanceRating.POOR

    def test_very_poor_below_3_0(self):
        assert PointsCalculator._rate_performance(Decimal("2.9")) == PerformanceRating.VERY_POOR

    def test_very_poor_zero(self):
        assert PointsCalculator._rate_performance(Decimal("0.0")) == PerformanceRating.VERY_POOR


class TestCalculatePoints24Week:
    """Verify point gains for 24-week course."""

    def test_excellent(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("9.5"),
            course_length=CourseLength.WEEKS_24,
            current_skill_score=3.0,
        )
        assert points == 55

    def test_good(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("7.5"),
            course_length=CourseLength.WEEKS_24,
            current_skill_score=3.0,
        )
        assert points == 40

    def test_average(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("5.5"),
            course_length=CourseLength.WEEKS_24,
            current_skill_score=3.0,
        )
        assert points == 25

    def test_poor(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("3.5"),
            course_length=CourseLength.WEEKS_24,
            current_skill_score=3.0,
        )
        assert points == 10

    def test_very_poor(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("1.0"),
            course_length=CourseLength.WEEKS_24,
            current_skill_score=3.0,
        )
        assert points == 0


class TestCalculatePoints48Week:
    """Verify point gains for 48-week course (roughly half of 24w)."""

    def test_excellent(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("9.5"),
            course_length=CourseLength.WEEKS_48,
            current_skill_score=3.0,
        )
        assert points == 28

    def test_good(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("7.5"),
            course_length=CourseLength.WEEKS_48,
            current_skill_score=3.0,
        )
        assert points == 20

    def test_average(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("5.5"),
            course_length=CourseLength.WEEKS_48,
            current_skill_score=3.0,
        )
        assert points == 12

    def test_poor(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("3.5"),
            course_length=CourseLength.WEEKS_48,
            current_skill_score=3.0,
        )
        assert points == 5

    def test_very_poor(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("1.0"),
            course_length=CourseLength.WEEKS_48,
            current_skill_score=3.0,
        )
        assert points == 0


class TestAdvancedSlowdown:
    """At score ≥8.0, points are halved."""

    def test_slowdown_at_exactly_8(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("7.5"),
            course_length=CourseLength.WEEKS_24,
            current_skill_score=8.0,
        )
        assert points == 20  # 40 // 2

    def test_slowdown_above_8(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("9.5"),
            course_length=CourseLength.WEEKS_24,
            current_skill_score=9.0,
        )
        assert points == 27  # 55 * 0.5 = 27

    def test_no_slowdown_below_8(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("9.5"),
            course_length=CourseLength.WEEKS_24,
            current_skill_score=7.9,
        )
        assert points == 55  # Full points

    def test_no_current_score_means_no_slowdown(self):
        points = PointsCalculator.calculate_points(
            score_0_to_10=Decimal("9.5"),
            course_length=CourseLength.WEEKS_24,
            current_skill_score=None,
        )
        assert points == 55


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
