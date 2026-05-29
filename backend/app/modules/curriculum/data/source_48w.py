"""48-week curriculum source data — empty day placeholders.

Extends the 24-week plan to 48 weeks using the same 6-cycle × 4-theme
structure, but each cycle now spans 8 weeks instead of 4.  The four
themes cycle twice within every cycle:
    grammar → communication → vocabulary → confidence  (× 2)

Cycles:
    Cycle 1 (weeks  1– 8): A1   sub_level 1–2
    Cycle 2 (weeks  9–16): A2   sub_level 3–3
    Cycle 3 (weeks 17–24): B1   sub_level 4–5
    Cycle 4 (weeks 25–32): B1+  sub_level 5–6
    Cycle 5 (weeks 33–40): B2   sub_level 6–7
    Cycle 6 (weeks 41–48): C1   sub_level 8–8

All ``DaySource`` entries are blank — no title, description, or tasks.
Content will be filled in as the curriculum is authored.
"""

from __future__ import annotations

from .source_24w import DaySource, WeekSource

_EMPTY_DAYS = (
    DaySource(),
    DaySource(),
    DaySource(),
    DaySource(),
    DaySource(),
    DaySource(),
    DaySource(),
)

_THEMES = ("grammar", "communication", "vocabulary", "confidence")

_CYCLES: tuple[tuple[str, int, int], ...] = (
    # (cefr_level, sub_level_min, sub_level_max)
    ("A1",  1, 2),
    ("A2",  3, 3),
    ("B1",  4, 5),
    ("B1+", 5, 6),
    ("B2",  6, 7),
    ("C1",  8, 8),
)

WEEKS_48: tuple[WeekSource, ...] = (
    # ── Cycle 1 — Foundation (A1) ─────────────────────────────────
    WeekSource(
        week_number=1,
        theme_type="grammar",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=2,
        theme_type="communication",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=3,
        theme_type="vocabulary",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=4,
        theme_type="confidence",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=5,
        theme_type="grammar",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=6,
        theme_type="communication",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=7,
        theme_type="vocabulary",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=8,
        theme_type="confidence",
        cefr_level="A1",
        sub_level_min=1, sub_level_max=2,
        days=_EMPTY_DAYS,
    ),

    # ── Cycle 2 — Daily Life (A2) ─────────────────────────────────
    WeekSource(
        week_number=9,
        theme_type="grammar",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=10,
        theme_type="communication",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=11,
        theme_type="vocabulary",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=12,
        theme_type="confidence",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=13,
        theme_type="grammar",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=14,
        theme_type="communication",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=15,
        theme_type="vocabulary",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=16,
        theme_type="confidence",
        cefr_level="A2",
        sub_level_min=3, sub_level_max=3,
        days=_EMPTY_DAYS,
    ),

    # ── Cycle 3 — Functioning (B1) ────────────────────────────────
    WeekSource(
        week_number=17,
        theme_type="grammar",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=18,
        theme_type="communication",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=19,
        theme_type="vocabulary",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=20,
        theme_type="confidence",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=21,
        theme_type="grammar",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=22,
        theme_type="communication",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=23,
        theme_type="vocabulary",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=24,
        theme_type="confidence",
        cefr_level="B1",
        sub_level_min=4, sub_level_max=5,
        days=_EMPTY_DAYS,
    ),

    # ── Cycle 4 — Connecting (B1+) ────────────────────────────────
    WeekSource(
        week_number=25,
        theme_type="grammar",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=26,
        theme_type="communication",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=27,
        theme_type="vocabulary",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=28,
        theme_type="confidence",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=29,
        theme_type="grammar",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=30,
        theme_type="communication",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=31,
        theme_type="vocabulary",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=32,
        theme_type="confidence",
        cefr_level="B1+",
        sub_level_min=5, sub_level_max=6,
        days=_EMPTY_DAYS,
    ),

    # ── Cycle 5 — Reasoning (B2) ──────────────────────────────────
    WeekSource(
        week_number=33,
        theme_type="grammar",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=34,
        theme_type="communication",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=35,
        theme_type="vocabulary",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=36,
        theme_type="confidence",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=37,
        theme_type="grammar",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=38,
        theme_type="communication",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=39,
        theme_type="vocabulary",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=40,
        theme_type="confidence",
        cefr_level="B2",
        sub_level_min=6, sub_level_max=7,
        days=_EMPTY_DAYS,
    ),

    # ── Cycle 6 — Polishing (C1) ──────────────────────────────────
    WeekSource(
        week_number=41,
        theme_type="grammar",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=42,
        theme_type="communication",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=43,
        theme_type="vocabulary",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=44,
        theme_type="confidence",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=45,
        theme_type="grammar",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=46,
        theme_type="communication",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=47,
        theme_type="vocabulary",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        days=_EMPTY_DAYS,
    ),
    WeekSource(
        week_number=48,
        theme_type="confidence",
        cefr_level="C1",
        sub_level_min=8, sub_level_max=8,
        days=_EMPTY_DAYS,
    ),
)
