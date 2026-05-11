"""Business logic for course enrollment.

Routes call this. Repos do the data work. Service decides:
  - Does the course exist? (404)
  - Is the user already enrolled? (409 — MVP: one enrollment per user)
  - When to commit
"""

from sqlalchemy.orm import Session

from app.modules.curriculum.exceptions import (
    AlreadyEnrolled,
    CourseNotFound,
    NotEnrolled,
)
from app.modules.curriculum.models import UserEnrollment
from app.modules.curriculum.repository import (
    CourseRepository,
    UserEnrollmentRepository,
)


class EnrollmentService:
    """Manages a user's enrollment in a course."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.course_repo = CourseRepository(db)
        self.enrollment_repo = UserEnrollmentRepository(db)

    def enroll(self, *, user_id: int, course_slug: str) -> UserEnrollment:
        """Enroll a user in the course identified by slug.

        Raises:
            CourseNotFound: slug doesn't match any course.
            AlreadyEnrolled: user already has an enrollment (MVP rule).
        """
        course = self.course_repo.get_by_slug(course_slug)
        if course is None:
            raise CourseNotFound(f"No course with slug={course_slug!r}")

        existing = self.enrollment_repo.get_for_user(user_id)
        if existing is not None:
            raise AlreadyEnrolled(
                f"User {user_id} already enrolled in {existing.course.slug!r}"
            )

        enrollment = self.enrollment_repo.create(
            user_id=user_id,
            course_id=course.id,
        )
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def get_for_user(self, user_id: int) -> UserEnrollment | None:
        """Return the user's current enrollment, or None if not enrolled.

        Pure read — no commit. Useful for /me/enrollment endpoints later.
        """
        return self.enrollment_repo.get_for_user(user_id)

    def update_settings(
        self,
        *,
        user_id: int,
        tasks_per_day: int | None = None,
        allow_reading: bool | None = None,
        allow_writing: bool | None = None,
        allow_listening: bool | None = None,
        allow_speaking: bool | None = None,
    ) -> UserEnrollment:
        """Update daily practice preferences for the active enrollment.

        Daily task count is 2..4. The learner must keep at least two core
        activity types active so the rotation engine always has room to vary.
        """
        enrollment = self.enrollment_repo.get_for_user(user_id)
        if enrollment is None:
            raise NotEnrolled(f"User {user_id} is not enrolled in any course")

        proposed = {
            "allow_reading": (
                enrollment.allow_reading if allow_reading is None else allow_reading
            ),
            "allow_writing": (
                enrollment.allow_writing if allow_writing is None else allow_writing
            ),
            "allow_listening": (
                enrollment.allow_listening
                if allow_listening is None
                else allow_listening
            ),
            "allow_speaking": (
                enrollment.allow_speaking if allow_speaking is None else allow_speaking
            ),
        }
        if sum(1 for enabled in proposed.values() if enabled) < 2:
            raise ValueError("At least two core activities must stay enabled")

        if tasks_per_day is not None:
            if not 2 <= tasks_per_day <= 4:
                raise ValueError("Daily task count must be between 2 and 4")
            enrollment.tasks_per_day = tasks_per_day
        enrollment.allow_reading = proposed["allow_reading"]
        enrollment.allow_writing = proposed["allow_writing"]
        enrollment.allow_listening = proposed["allow_listening"]
        enrollment.allow_speaking = proposed["allow_speaking"]

        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment
