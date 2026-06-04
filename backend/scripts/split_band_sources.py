#!/usr/bin/env python3
"""One-off script: split source_L_A1A2.py monolith into three band files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "app/modules/curriculum/data"
SOURCE = DATA / "source_L_A1A2.py"

IMPORT_HEADER = '''"""Level-band curriculum source data.

Imports blueprint types from ``types.py`` only.
"""

from __future__ import annotations

from .types import (
    ActivityBlueprint,
    DaySource,
    EvaluationBlueprint,
    FeedbackBlueprint,
    TaskBlueprint,
    TeacherBlueprint,
    TeacherStep,
    WeekSource,
)

'''

# Week boundaries from grep: week_number=8@8151, 9@9284, 16@17212, 17@18249, 24@25692
WEEK_LINE_MARKERS = [
    (1, 110),
    (9, 9283),
    (17, 18248),
    (25, 26698),  # end sentinel
]


def _read_lines() -> list[str]:
    return SOURCE.read_text(encoding="utf-8").splitlines(keepends=True)


def _extract_weeks(lines: list[str], start_line: int, end_line: int) -> str:
    """Return WEEKS tuple body from start_line (1-based) to end_line exclusive."""
    chunk = "".join(lines[start_line - 1 : end_line - 1])
    return chunk


def _renumber_weeks(content: str, old_start: int, new_start: int = 1) -> str:
    """Replace week_number=N with renumbered values."""
    for old in range(old_start, old_start + 8):
        new = new_start + (old - old_start)
        content = re.sub(
            rf"week_number={old}\b",
            f"week_number={new}",
            content,
            count=1,
        )
    return content


def _remap_cefr_b1b2(content: str) -> str:
    """Local weeks 5-8: B1+ -> B2, sub_level 5-6 -> 6-7."""
    # After renumbering, old global 13-16 are local 5-8 with B1+
    content = content.replace('cefr_level="B1+"', 'cefr_level="B2"')
    content = content.replace("sub_level_min=5, sub_level_max=6", "sub_level_min=6, sub_level_max=7")
    return content


def _remap_cefr_c1c2(content: str) -> str:
    """Local weeks 1-4: B2->C1; weeks 5-8: C1->C2 (process in order)."""
    parts = re.split(r"(?=    WeekSource\()", content)
    out: list[str] = []
    week_idx = 0
    for part in parts:
        if not part.strip() or "WeekSource(" not in part:
            out.append(part)
            continue
        week_idx += 1
        if week_idx <= 4:
            part = part.replace('cefr_level="B2"', 'cefr_level="C1"', 1)
            part = part.replace("sub_level_min=6, sub_level_max=7", "sub_level_min=8, sub_level_max=8", 1)
        else:
            part = part.replace('cefr_level="C1"', 'cefr_level="C2"', 1)
        out.append(part)
    return "".join(out)


def _write_band(path: Path, export_name: str, weeks_body: str, comment: str) -> None:
    text = IMPORT_HEADER + f"\n{comment}\n\n{export_name}: tuple[WeekSource, ...] = (\n{weeks_body})\n"
    path.write_text(text, encoding="utf-8")
    print(f"Wrote {path} ({len(text)} bytes)")


def main() -> None:
    lines = _read_lines()

    a1a2_body = _extract_weeks(lines, 110, 9282)
    b1b2_body = _extract_weeks(lines, 9283, 18247)
    c1c2_body = _extract_weeks(lines, 18248, 26697)

    b1b2_body = _renumber_weeks(b1b2_body, old_start=9, new_start=1)
    b1b2_body = _remap_cefr_b1b2(b1b2_body)

    c1c2_body = _renumber_weeks(c1c2_body, old_start=17, new_start=1)
    c1c2_body = _remap_cefr_c1c2(c1c2_body)

    _write_band(
        DATA / "source_L_A1A2.py",
        "WEEKS_A1A2",
        a1a2_body,
        "# ── A1A2 band: source weeks 1-8 (A1 wk 1-4, A2 wk 5-8) ──",
    )
    _write_band(
        DATA / "source_L_B1B2.py",
        "WEEKS_B1B2",
        b1b2_body,
        "# ── B1B2 band: source weeks 1-8 (B1 wk 1-4, B2 wk 5-8) ──",
    )
    _write_band(
        DATA / "source_L_C1C2.py",
        "WEEKS_C1C2",
        c1c2_body,
        "# ── C1C2 band: source weeks 1-8 (C1 wk 1-4, C2 wk 5-8) ──",
    )


if __name__ == "__main__":
    main()
