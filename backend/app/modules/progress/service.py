"""Score updater — applies WMA to user skill scores and logs history.
 
Triggered AFTER feedback is generated. Given an evaluation_id:
  1. Walk back: Evaluation → UserResponse → UserTask → Task → TaskSkill[]
  2. For each targeted skill, compute new score (weighted moving average)
  3. Upsert UserSkillScore (current cached value)
  4. Insert ProgressLog (append-only history)
  5. Commit once
 
Skills NOT in the task's TaskSkill list are NEVER touched.
"""

import logging
from decimal import Decimal
from enum import Enum

from sqlalchemy.orm import Session

from app.modules.curriculum.repository import UserEnrollmentRepository
from app.modules.progress.exceptions import (
    EvaluationNotFound,
    TaskHasNoTargetSkills,
)
from app.modules.progress.models import SkillPoints
from app.modules.progress.repository import (
    ProgressLogRepository,
    SkillPointsLogRepository,
    SkillPointsRepository,
)
from app.modules.responses.repository import EvaluationRepository
from app.modules.skills.models import UserSkillScore
from app.modules.skills.repository import UserSkillScoreRepository
from app.modules.tasks.models import UserTask


logger = logging.getLogger(__name__)


# Learning rate — how strongly ONE task can shift a score.
# 0.2 = 20% new task, 80% old score → smooth, noise-resistant drift.
ALPHA = Decimal("0.2")

# Default starting score for a brand-new (user, skill) pair.
# Should rarely be hit — diagnosis seeds these — but we're defensive.
DEFAULT_SCORE = Decimal("3.0")


class ScoreUpdaterService:
    """Applies a single evaluation's outcome to the user's skill scores."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.evaluation_repo = EvaluationRepository(db)
        self.skill_score_repo = UserSkillScoreRepository(db)
        self.progress_log_repo = ProgressLogRepository(db)

    @staticmethod
    def _compute_new_score(
        *,
        old_score: Decimal,
        task_score: Decimal,
        skill_weight: Decimal,
    ) -> Decimal:
        """Weighted moving average for ONE skill.

        Formula:
            effective_alpha = ALPHA * skill_weight
            new = effective_alpha * task_score + (1 - effective_alpha) * old_score

        Result is clamped to [0.0, 10.0] and rounded to 1 decimal place
        to match Numeric(3, 1).
        """
        effective_alpha = ALPHA * skill_weight
        new_score = (
            effective_alpha * task_score
            + (Decimal("1") - effective_alpha) * old_score
        )
        new_score = max(Decimal("0.0"), min(Decimal("10.0"), new_score))
        return new_score.quantize(Decimal("0.1"))

    def apply(self, evaluation_id: int) -> list[UserSkillScore]:
        """Apply one evaluation's outcome to all targeted skills.

        Returns the list of updated UserSkillScore rows.
        Skills NOT targeted by this task are NEVER touched.
        """
        # 1. Load the evaluation
        evaluation = self.evaluation_repo.get_by_id(evaluation_id)
        if evaluation is None:
            raise EvaluationNotFound(
                f"Evaluation {evaluation_id} does not exist"
            )

        # 2. Walk back: Evaluation → UserResponse → UserTask → Task → TaskSkill[]
        response = evaluation.response
        user_task = self.db.get(UserTask, response.user_task_id)
        task = user_task.task
        target_skills = task.task_skills

        if not target_skills:
            raise TaskHasNoTargetSkills(
                f"Task {task.id} has no TaskSkill rows — cannot update scores"
            )

        # 3. Convert evaluation percentage (0–100) → 0–10 scale.
        task_score = Decimal(evaluation.percentage) / Decimal("10")

        # 4. For each targeted skill: WMA → upsert → log.
        updated_rows: list[UserSkillScore] = []

        for ts in target_skills:
            existing = self.skill_score_repo.get_one(
                user_id=user_task.user_id,
                skill_id=ts.skill_id,
            )
            old_score = (
                Decimal(existing.score) if existing is not None else DEFAULT_SCORE
            )

            new_score = self._compute_new_score(
                old_score=old_score,
                task_score=task_score,
                skill_weight=Decimal(ts.weight),
            )

            # 4a. Upsert the cached current score.
            updated = self.skill_score_repo.upsert_score(
                user_id=user_task.user_id,
                skill_id=ts.skill_id,
                score=float(new_score),
                is_estimated=False,
            )
            updated_rows.append(updated)

            # 4b. Append-only history row.
            self.progress_log_repo.create(
                user_id=user_task.user_id,
                skill_id=ts.skill_id,
                score=float(new_score),
                user_task_id=user_task.id,
            )

        # 5. One commit — atomic across all skills.
        self.db.commit()
        for row in updated_rows:
            self.db.refresh(row)

        return updated_rows


# ── Points-based scoring (gamification layer) ──────────────────────


class CourseLength(str, Enum):
    """24-week or 48-week curriculum."""
    WEEKS_24 = "24w"
    WEEKS_48 = "48w"


class PerformanceRating(str, Enum):
    """Task performance tier."""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    VERY_POOR = "very_poor"


# Points gained per skill per performance tier for each course length.
# 48-week courses yield ~half the points of 24-week to stretch progression.
POINTS_TABLE: dict[CourseLength, dict[PerformanceRating, int]] = {
    CourseLength.WEEKS_24: {
        PerformanceRating.EXCELLENT: 55,
        PerformanceRating.GOOD: 40,
        PerformanceRating.AVERAGE: 24,
        PerformanceRating.POOR: 10,
        PerformanceRating.VERY_POOR: 0,
    },
    CourseLength.WEEKS_48: {
        PerformanceRating.EXCELLENT: 28,
        PerformanceRating.GOOD: 20,
        PerformanceRating.AVERAGE: 12,
        PerformanceRating.POOR: 5,
        PerformanceRating.VERY_POOR: 0,
    },
}


class PointsCalculator:
    """Determine points earned based on task performance and course length."""

    @staticmethod
    def _rate_performance(score_0_to_10: Decimal) -> PerformanceRating:
        """Map numeric score (0.0–10.0) to performance tier."""
        if score_0_to_10 >= Decimal("8.0"):
            return PerformanceRating.EXCELLENT
        elif score_0_to_10 >= Decimal("6.0"):
            return PerformanceRating.GOOD
        elif score_0_to_10 >= Decimal("4.0"):
            return PerformanceRating.AVERAGE
        elif score_0_to_10 >= Decimal("2.0"):
            return PerformanceRating.POOR
        else:
            return PerformanceRating.VERY_POOR

    @staticmethod
    def calculate_points(
        score_0_to_10: Decimal,
        course_length: CourseLength,
        current_skill_score: float | None = None,
    ) -> int:
        """Calculate points earned for one skill update.

        Args:
            score_0_to_10: Task score (0.0–10.0).
            course_length: Curriculum length (24w or 48w).
            current_skill_score: User's current display score for slowdown logic.

        Returns:
            Points to add (integer).
        """
        rating = PointsCalculator._rate_performance(score_0_to_10)
        base_points = POINTS_TABLE[course_length][rating]

        # Advanced slowdown: at 8.0+, halve the points gain
        if current_skill_score is not None and current_skill_score >= 8.0:
            base_points = int(base_points * 0.5)

        return base_points


class PointsUpdaterService:
    """Updates SkillPoints after task evaluation (parallel to WMA)."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.evaluation_repo = EvaluationRepository(db)
        self.points_repo = SkillPointsRepository(db)
        self.points_log_repo = SkillPointsLogRepository(db)
        self.enrollment_repo = UserEnrollmentRepository(db)

    def apply(
        self,
        evaluation_id: int,
        course_length: CourseLength | None = None,
    ) -> list[SkillPoints]:
        """Apply points gain for an evaluation across all targeted skills.

        Args:
            evaluation_id: The evaluation to process.
            course_length: User's curriculum length. If None, auto-detected
                from UserEnrollment. Defaults to 24w if not enrolled.

        Returns:
            List of updated SkillPoints rows.
        """
        # 1. Load evaluation
        evaluation = self.evaluation_repo.get_by_id(evaluation_id)
        if evaluation is None:
            raise EvaluationNotFound(
                f"Evaluation {evaluation_id} does not exist"
            )

        # 2. Walk back: Evaluation → UserResponse → UserTask → Task → TaskSkill[]
        response = evaluation.response
        user_task = self.db.get(UserTask, response.user_task_id)
        task = user_task.task
        target_skills = task.task_skills

        if not target_skills:
            raise TaskHasNoTargetSkills(
                f"Task {task.id} has no TaskSkill rows — cannot update points"
            )

        # 3. Auto-detect course length from enrollment if not provided
        if course_length is None:
            enrollment = self.enrollment_repo.get_for_user(user_task.user_id)
            if enrollment is not None:
                course_length = (
                    CourseLength.WEEKS_24
                    if enrollment.course.duration_weeks == 24
                    else CourseLength.WEEKS_48
                )
            else:
                # No enrollment yet — default to 24-week pace
                course_length = CourseLength.WEEKS_24

        # 4. Convert percentage (0–100) → 0–10 scale
        task_score = Decimal(evaluation.percentage) / Decimal("10")

        # 5. For each targeted skill: calculate → upsert → log
        updated_rows: list[SkillPoints] = []

        for ts in target_skills:
            existing = self.points_repo.get_one(
                user_id=user_task.user_id,
                skill_id=ts.skill_id,
            )
            old_points = existing.points if existing is not None else 3000
            old_score = old_points / 1000.0

            # Calculate points earned
            points_earned = PointsCalculator.calculate_points(
                score_0_to_10=task_score,
                course_length=course_length,
                current_skill_score=old_score,
            )

            # Upsert
            new_points = old_points + points_earned
            updated = self.points_repo.upsert_points(
                user_id=user_task.user_id,
                skill_id=ts.skill_id,
                points=new_points,
            )
            updated_rows.append(updated)

            # Log the gain
            rating_value = PointsCalculator._rate_performance(task_score).value
            reason = f"{rating_value}_task_{course_length.value}"
            self.points_log_repo.create(
                user_id=user_task.user_id,
                skill_id=ts.skill_id,
                points_earned=points_earned,
                reason=reason,
                user_task_id=user_task.id,
            )

        # 6. Atomic commit
        self.db.commit()
        for row in updated_rows:
            self.db.refresh(row)

        return updated_rows