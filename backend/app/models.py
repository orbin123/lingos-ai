"""
Central model registry.

Importing every model here ensures SQLAlchemy's class registry is fully
populated before any mapper is configured. This:
  1. Resolves string-based relationship() references across modules
  2. Lets Alembic discover all tables via Base.metadata
  3. Gives one canonical import line for app startup and tooling

Add every new model to this file as you create it.
"""

from app.modules.auth.models import (  # noqa: F401
    OAuthAccount,
    Permission,
    Role,
    RolePermission,
    User,
    UserProfile,
    UserRole,
)
from app.modules.admin.models import AdminAuditLog, AIRequestLog  # noqa: F401
from app.modules.skills.models import Skill, UserSkillScore  # noqa: F401
from app.modules.curriculum.models import (  # noqa: F401
    Course, UserEnrollment, EnrollmentSkillHistory, DailyPlan,
)
from app.modules.curriculum.v2_models import (  # noqa: F401
    CurriculumDay, CurriculumWeek, TaskArchetype,
)
from app.modules.challenges.models import (  # noqa: F401
    Challenge,
    ChallengeAttempt,
    ChallengeLevel,
)
from app.modules.tasks.models import Task, TaskSkill, UserTask  # noqa: F401
from app.modules.responses.models import (  # noqa: F401
    UserResponse, Evaluation, Feedback,
)
from app.modules.progress.models import ProgressLog, SkillPoints, SkillPointsLog  # noqa: F401
from app.modules.subscriptions.models import Payment, Purchase, Subscription  # noqa: F401
from app.modules.learning_session.models import LearningSession  # noqa: F401
from app.modules.sessions.models import (  # noqa: F401
    ActivityAttempt,
    ActivityEvaluation,
    ActivityFeedback,
    DailySession,
    SessionScorecard,
)
