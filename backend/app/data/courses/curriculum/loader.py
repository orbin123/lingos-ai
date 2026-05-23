"""Hydrate WeekSource rows into fully-shaped WeekRecord / DayRecord values.

`load_weeks(course_length)` is the only thing seeders, tests, and runtime
code should call. The two underlying source modules (`source_24w.py` and the
derived 48w via `stretch.py`) are implementation details.

Each hydrated day carries:
  - a stable `day_id` (`day_<24|48>_<week>_<day>`)
  - the theme's `mandatory_activities`
  - `suggested_archetypes` filtered to those whose CEFR range covers the
    week's CEFR level, so the planner can't pick an archetype the user isn't
    ready for.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.data.courses.curriculum_v2.source_24w import WEEKS_24, WeekSource
from app.data.courses.stretch import stretch_to_48w
from app.scoring import CourseLength, get_archetype


# ── Hydrated records (what consumers see) ──────────────────────────


@dataclass(frozen=True)
class DayRecord:
    day_id: str
    day_number: int
    topic: str
    explanation_brief: str
    default_activities: tuple[str, ...]
    mandatory_activities: tuple[str, ...]
    suggested_archetypes: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class WeekRecord:
    week_id: str
    course_length: CourseLength
    week_number: int
    theme_type: str
    title: str
    cefr_level: str
    sub_level_min: int
    sub_level_max: int
    learning_goal: str
    days: tuple[DayRecord, ...]


# ── Theme conventions ──────────────────────────────────────────────


_DEFAULT_ACTIVITIES: tuple[str, ...] = ("read", "write", "listen", "speak")

# Which two activities every day MUST contain. The remainder are "optional"
# and surface only when the user picks tasks_per_day > 2.
_MANDATORY_BY_THEME: dict[str, tuple[str, ...]] = {
    "grammar":       ("read", "write"),
    "communication": ("write", "speak"),
    "vocabulary":    ("read", "write"),
    "confidence":    ("listen", "speak"),
}

# Per-theme archetype pools, ordered loosely from simplest to richest. The
# loader filters these against the week's CEFR level. Pool contents are
# chosen so every (theme, mandatory_activity) has at least one A1 option —
# tests assert this.
_CANDIDATES_BY_THEME: dict[str, dict[str, tuple[str, ...]]] = {
    "grammar": {
        "read":   ("READ_CLOZE", "READ_COMP_MCQ", "READ_ERROR_SPOT"),
        "write":  ("WRITE_OPEN_SENT", "WRITE_SENT_TRANS", "WRITE_ERROR_CORR", "WRITE_VOICE_CONV", "WRITE_PARA"),
        "listen": ("LISTEN_MCQ", "LISTEN_CLOZE", "LISTEN_DICTATION"),
        "speak":  ("SPEAK_READ_ALOUD", "SPEAK_TIMED"),
    },
    "communication": {
        "read":   ("READ_COMP_MCQ", "READ_TFNG", "READ_STRUCTURE_ID"),
        "write":  ("WRITE_SENT_TRANS", "WRITE_EMAIL", "WRITE_PARA",
                   "WRITE_PARAPHRASE", "WRITE_BULLETS_TO_PARA", "WRITE_IDEA_PARA"),
        "listen": ("LISTEN_MCQ", "LISTEN_INFER", "LISTEN_RETELL"),
        "speak":  ("SPEAK_PIC_DESC", "SPEAK_ROLEPLAY", "SPEAK_INTERVIEW", "SPEAK_OPINION"),
    },
    "vocabulary": {
        "read":   ("READ_WORD_MATCH", "READ_CONTEXT_MCQ"),
        "write":  ("WRITE_SENT_TRANS", "WRITE_WORD_UPGRADE", "WRITE_PARA", "WRITE_PARAPHRASE"),
        "listen": ("LISTEN_MCQ", "LISTEN_DICTATION"),
        "speak":  ("SPEAK_PIC_DESC", "SPEAK_TIMED"),
    },
    "confidence": {
        "read":   ("READ_COMP_MCQ", "READ_TONE_ID"),
        "write":  ("WRITE_SENT_TRANS", "WRITE_TIMED"),
        "listen": ("LISTEN_SHADOW", "LISTEN_MCQ", "LISTEN_TONE"),
        "speak":  ("SPEAK_READ_ALOUD", "SPEAK_TIMED", "SPEAK_PIC_DESC",
                   "SPEAK_SMALLTALK", "SPEAK_PRESENT", "SPEAK_DEBATE"),
    },
}


# CEFR levels mapped to a comparable rank. The "+" variants share rank with
# their base level — B1+ and B1 are treated as equivalent for archetype
# eligibility. Sub-levels (1–10) handle finer-grained difficulty inside the
# Task Generator.
_CEFR_RANK: dict[str, int] = {
    "A1": 1, "A2": 2, "B1": 3, "B1+": 3, "B2": 4, "B2+": 4, "C1": 5, "C2": 6,
}


def _cefr_compatible(archetype_id: str, week_cefr: str) -> bool:
    spec = get_archetype(archetype_id)
    return _CEFR_RANK[spec.cefr_min] <= _CEFR_RANK[week_cefr] <= _CEFR_RANK[spec.cefr_max]


def _suggested_archetypes(theme_type: str, cefr_level: str) -> dict[str, tuple[str, ...]]:
    pool = _CANDIDATES_BY_THEME[theme_type]
    return {
        activity: tuple(aid for aid in ids if _cefr_compatible(aid, cefr_level))
        for activity, ids in pool.items()
    }


# ── ID generation ──────────────────────────────────────────────────


def _course_prefix(course_length: CourseLength) -> str:
    return "24" if course_length is CourseLength.WEEKS_24 else "48"


def _week_id(course_length: CourseLength, week_number: int) -> str:
    return f"wk_{_course_prefix(course_length)}_{week_number:02d}"


def _day_id(course_length: CourseLength, week_number: int, day_number: int) -> str:
    return f"day_{_course_prefix(course_length)}_{week_number:02d}_{day_number:02d}"


# ── Hydration ──────────────────────────────────────────────────────


def _hydrate(week: WeekSource, course_length: CourseLength) -> WeekRecord:
    mandatory = _MANDATORY_BY_THEME[week.theme_type]
    suggested = _suggested_archetypes(week.theme_type, week.cefr_level)
    days = tuple(
        DayRecord(
            day_id=_day_id(course_length, week.week_number, day_number),
            day_number=day_number,
            topic=topic,
            explanation_brief=brief,
            default_activities=_DEFAULT_ACTIVITIES,
            mandatory_activities=mandatory,
            suggested_archetypes=suggested,
        )
        for day_number, (topic, brief) in enumerate(week.days, start=1)
    )
    return WeekRecord(
        week_id=_week_id(course_length, week.week_number),
        course_length=course_length,
        week_number=week.week_number,
        theme_type=week.theme_type,
        title=week.title,
        cefr_level=week.cefr_level,
        sub_level_min=week.sub_level_min,
        sub_level_max=week.sub_level_max,
        learning_goal=week.learning_goal,
        days=days,
    )


def load_weeks(course_length: CourseLength) -> tuple[WeekRecord, ...]:
    """Return all hydrated WeekRecord rows for `course_length`."""
    if course_length is CourseLength.WEEKS_24:
        return tuple(_hydrate(w, course_length) for w in WEEKS_24)
    return tuple(_hydrate(w, course_length) for w in stretch_to_48w(WEEKS_24))
