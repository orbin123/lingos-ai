"""Compatibility shim — re-exports v2 curriculum ORM models.

New code should import directly from ``app.modules.curriculum.models``.
This module exists so that test files and future tooling can use the
``v2_models`` namespace without a separate physical module.
"""

from app.modules.curriculum.models import (  # noqa: F401
    CoreActivity,
    CurriculumDay,
    CurriculumWeek,
    TaskArchetype,
    ThemeType,
)
