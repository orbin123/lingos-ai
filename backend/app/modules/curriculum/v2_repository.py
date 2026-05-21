"""Compatibility shim — re-exports v2 curriculum repositories.

New code should import directly from ``app.modules.curriculum.repository``.
This module exists so that callers using the ``v2_repository`` namespace
continue to work without a separate physical module.
"""

from app.modules.curriculum.repository import (  # noqa: F401
    CurriculumDayRepository,
    CurriculumWeekRepository,
    TaskArchetypeRepository,
)
