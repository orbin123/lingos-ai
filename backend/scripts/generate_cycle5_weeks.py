"""Generate weeks 17-20 (Cycle 5, B2) by mirroring weeks 13-16 structure."""

from __future__ import annotations

import dataclasses
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_C4_PATH = Path(__file__).resolve().parent / "generate_cycle4_weeks.py"
_spec = importlib.util.spec_from_file_location("generate_cycle4_weeks", _C4_PATH)
c4 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
sys.modules["generate_cycle4_weeks"] = c4
_spec.loader.exec_module(c4)

_C5_SPECS_PATH = Path(__file__).resolve().parent / "cycle5_day_specs.py"
_spec5 = importlib.util.spec_from_file_location("cycle5_day_specs", _C5_SPECS_PATH)
c5s = importlib.util.module_from_spec(_spec5)
assert _spec5.loader is not None
sys.modules["cycle5_day_specs"] = c5s
_spec5.loader.exec_module(c5s)

DaySpec = c4.DaySpec
WeekSource = c4.WeekSource
WEEKS_24 = c4.WEEKS_24
_build_day = c4._build_day
_emit_day = c4._emit_day
_week_days = c4._week_days
DAY_SPECS = c5s.DAY_SPECS

MIRROR_OFFSET = 4


def _mirror_day(week: int, day_index: int) -> c4.DaySource:
    return _week_days(week - MIRROR_OFFSET)[day_index]


def build_week(week: int) -> WeekSource:
    shell = next(w for w in WEEKS_24 if w.week_number == week)
    days = []
    for d in range(7):
        mirror = _mirror_day(week, d)
        spec = DAY_SPECS[(week, d)]
        days.append(_build_day(mirror, spec))
    return dataclasses.replace(shell, days=tuple(days))


def emit_cycle5() -> str:
    lines = [
        "    # ── Cycle 5 — Reasoning (B2) ──────────────────────────────────",
    ]
    for week in (17, 18, 19, 20):
        w = build_week(week)
        lines.append("    WeekSource(")
        lines.append(f"        week_number={w.week_number},")
        lines.append(f'        theme_type="{w.theme_type}",')
        lines.append(f'        cefr_level="{w.cefr_level}",')
        lines.append(
            f"        sub_level_min={w.sub_level_min}, sub_level_max={w.sub_level_max},"
        )
        lines.append("        days=(")
        for day in w.days:
            lines.extend(_emit_day(day, "            "))
        lines.append("        ),")
        lines.append("    ),")
    return "\n".join(lines)


def patch_source_file() -> None:
    path = Path(__file__).resolve().parents[1] / "app/modules/curriculum/data/source_L_C1C2.py"
    text = path.read_text()
    start = text.index("    # ── Cycle 5 —")
    end = text.index("    # ── Cycle 6 —")
    path.write_text(text[:start] + emit_cycle5() + "\n\n" + text[end:])
    print(f"Patched {path} (weeks 17-20)")


if __name__ == "__main__":
    patch_source_file()
