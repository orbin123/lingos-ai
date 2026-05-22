"""Compatibility re-export for curriculum v2 loader helpers.

The curriculum data module was flattened from `app/data/courses/curriculum_v2/`
into `app/data/courses/`. Tests and one runtime caller still import from the
old path, so this shim re-exports the public records plus the private theme
pools the data-shape tests inspect.
"""

from app.data.courses.loader import (
    DayRecord,
    WeekRecord,
    _CANDIDATES_BY_THEME,
    _MANDATORY_BY_THEME,
    load_weeks,
)

__all__ = [
    "DayRecord",
    "WeekRecord",
    "_CANDIDATES_BY_THEME",
    "_MANDATORY_BY_THEME",
    "load_weeks",
]
