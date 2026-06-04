# Curriculum source files

How LingosAI curriculum is authored, stored, and assembled at runtime.

---

## What changed (old vs current)

| Before | Now |
|--------|-----|
| One monolithic authored file (`source_24w.py` with `WEEKS_24` as **source of truth**) | **Three level-band modules** are the source of truth; `source_24w.py` / `source_48w.py` are **composed shims** |
| 24 calendar weeks authored directly (weeks 1–24 in one tuple) | Each band holds **8 local source weeks**; `composer.py` maps them onto 24w or 48w calendars |
| One `DaySource` per slot — 48w reused the same content twice | Each parent `DaySource` has an optional nested **`depth_day`**; 48w **pass 2** uses `depth_day` when present |
| Authoring batches targeted global weeks (e.g. 9–12, 13–16) in one file | Authoring targets **one band file** and **local** `week_number` 1–8 only |

**Do not edit** `source_24w.py` or `source_48w.py` for content — they call `compose_weeks()` and re-export the result. All content changes go into the band files under `backend/app/modules/curriculum/data/`.

---

## Three-level architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Level 1 — Schema (`types.py`)                                  │
│  DaySource, WeekSource, ActivityBlueprint, TeacherBlueprint, … │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  Level 2 — Canonical band sources (YOU EDIT THESE)              │
│  source_L_A1A2.py  →  WEEKS_A1A2  (8 local weeks)             │
│  source_L_B1B2.py   →  WEEKS_B1B2  (8 local weeks)             │
│  source_L_C1C2.py   →  WEEKS_C1C2  (8 local weeks)             │
│  Each DaySource: base fields + optional depth_day=DaySource(…)  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│  Level 3 — Runtime assembly (read-only for authors)             │
│  composer.py      → resolve_day / compose_weeks                 │
│  source_24w.py    → WEEKS_24 = compose_weeks(WEEKS_24)          │
│  source_48w.py    → WEEKS_48 = compose_weeks(WEEKS_48)          │
│  file_source.py   → day IDs, hydration for sessions             │
│  loader.py        → WeekRecord / DayRecord for seeders          │
│  blueprint_adapter.py → DaySource → session runtime shape       │
└─────────────────────────────────────────────────────────────────┘
```

**Rule of thumb:** import types from `types.py` only inside band files; never import `WEEKS_24` / `WEEKS_48` when authoring.

---

## Band files and global calendar mapping

Each band covers **two CEFR halves** (lower + upper) × **four theme weeks** = **8 local weeks**.

| Band file | Tuple | Global 24w weeks | Global 48w calendar weeks | Local weeks | CEFR (24w) |
|-----------|-------|------------------|---------------------------|-------------|------------|
| `source_L_A1A2.py` | `WEEKS_A1A2` | 1–8 | 1–16 | 1–8 | 1–4 A1, 5–8 A2 |
| `source_L_B1B2.py` | `WEEKS_B1B2` | 9–16 | 17–32 | 1–8 | 1–4 B1, 5–8 B2 |
| `source_L_C1C2.py` | `WEEKS_C1C2` | 17–24 | 33–48 | 1–8 | 1–4 C1, 5–8 C2 |

Within every band, **local weeks 1–4** use the lower CEFR label on `WeekSource`; **local weeks 5–8** use the upper label (see CEFR table below).

### Theme cycle (every band, every half)

Local weeks 1–4 and 5–8 each repeat the same theme order:

| Local week mod 4 | `theme_type` |
|------------------|--------------|
| 1 | `grammar` |
| 2 | `communication` |
| 3 | `vocabulary` |
| 4 | `confidence` |

So local weeks 5–8 mirror the theme *types* of 1–4 at a higher CEFR band.

---

## `DaySource`: base day and `depth_day`

A **parent** `DaySource` in a band file is the **base day**. An optional sibling field attaches 48w depth content:

```python
DaySource(
    title="...",           # BASE — seen on 24w and 48w pass 1 (pass_index=0)
    description=(...),
    focus="...",
    teacher=TeacherBlueprint(...),
    activities=(...),      # exactly 4 activities, sequences 1–4
    final_review=FinalReviewBlueprint(...),  # defaults OK
    depth_day=DaySource(   # DEPTH — 48w pass 2 only (pass_index=1)
        title="...",       # must differ from base title
        description=(...),
        focus="...",
        teacher=TeacherBlueprint(...),
        activities=(...),  # same archetype order/widgets as parent
        # no nested depth_day
    ),
),
```

### Who sees what

| Course | Calendar slot | Content used | CEFR |
|--------|---------------|--------------|------|
| **24w** | any day | **base** `DaySource` only | from `_cefr_for_24w` |
| **48w** | odd pass (day 1, 3, 5… within each source pair) | **base** | see 48w table below |
| **48w** | even pass (day 2, 4, 6…) | **`depth_day`** if set, else base (logged fallback) | see 48w table below |

24w learners **never** see `depth_day`. If `depth_day` is missing on a parent, 48w pass 2 falls back to base content (debug log only — all 168 depth slots are authored in production data).

### 48w mapping (two calendar days per source day)

For each band, calendar weeks `BAND_START_48 … BAND_START_48+15` map onto local source weeks 1–8. **Each source day becomes two consecutive calendar days:**

- **Pass 0** (`pass_index=0`): base `DaySource`
- **Pass 1** (`pass_index=1`): `parent.depth_day`

Example (A1A2): `day_48_01_01` = base simple present agreement (A1); `day_48_01_02` = depth “Questions, Negatives & Short Answers” (A2).

### 48w CEFR on depth pass

| Local source week | Base pass CEFR | Depth pass CEFR |
|-------------------|----------------|-----------------|
| 1–4 | Lower (A1 / B1 / C1) | **Upper** (A2 / B2 / C2) |
| 5–8 | Upper (A2 / B2 / C2) | **Same label** — content must go **deeper**, not a new code |

Depth topic plans live in [`docs/depth_topic_table.md`](depth_topic_table.md) (56 rows per band).

---

## Datamodel reference (`types.py`)

| Type | Role |
|------|------|
| `WeekSource` | `week_number`, `theme_type`, `cefr_level`, `sub_level_min/max`, `days` (7× `DaySource`) |
| `DaySource` | `title`, `description`, `focus`, `tags`, `teacher`, `activities`, `final_review`, `depth_day?` |
| `TeacherBlueprint` | `style`, `lesson_goal`, `steps`, `readiness_prompt` |
| `TeacherStep` | `id`, `goal`, `instruction`, `stop_after` |
| `ActivityBlueprint` | `id`, `sequence` (1–4), `task`, `evaluation`, `feedback`, `mandatory` |
| `TaskBlueprint` | `archetype_id`, `activity`, `task_widget`, `topic_override`, `generation_instructions`, `widget_requirements`, `static_payload?` |
| `EvaluationBlueprint` | `evaluator`, `evaluation_widget`, `rubric`, `overrides` |
| `FeedbackBlueprint` | `generator`, `feedback_widget`, `overrides` |
| `FinalReviewBlueprint` | `scorecard_widget`, `rag_feedback_widget` |

Activity order at runtime is **`read` → `listen` → `write` → `speak`** (sequences 1–4). This is enforced in tests and `blueprint_adapter._ordered_activities`.

---

## CEFR on `WeekSource` shells

Set on each `WeekSource` in the band file (composer may override on composed calendar weeks):

| Band | Local weeks | `cefr_level` | `sub_level_min`–`max` |
|------|-------------|--------------|------------------------|
| A1A2 | 1–4 / 5–8 | A1 / A2 | 1–2 / 3 |
| B1B2 | 1–4 / 5–8 | B1 / B2 | 4–5 / 6–7 |
| C1C2 | 1–4 / 5–8 | C1 / C2 | 8 / 8 |

---

## Authoring base days

### Mirror rule (within a band)

For **local week W ≥ 5**, day index **D** (0 = Monday … 6 = Sunday):

> Copy **activity structure** from **local week W − 4**, same day **D**.

- Same four `archetype_id` values, same order, same widgets, evaluators, feedback widgets.
- Same teacher **step count** and step **ids** (`open` → … → `wrap_up`).
- **Change:** titles, descriptions, focus, teacher instructions, activity ids, `topic_override`, generation text.

Local weeks **1–4** are authored from scratch (or from an external spec); **5–8 mirror 1–4** structurally with harder topics.

### Teacher behaviour (all levels today)

1. **Step 1 (`open`):** Greet; two short sentences on today’s focus; **one** open question.
2. **Middle steps:** One pattern per step; use the learner’s answer when possible; **one** `?` per step instruction (~60 words).
3. **Final step (`wrap_up`):** After the learner has shown the pattern once, instruction must ask **only:** `Ready to try the practice task?`

Defaults: `readiness_prompt = "Ready to try the practice task?"`, `style = "strict_kind_a1_friendly"`.

Teacher steps become the **scripted plan** at runtime (`teacher_instructions["teacher_steps"]` via `blueprint_adapter`).

### Task generator alignment

- `generation_instructions` / `widget_requirements` target the **new day topic** and **current CEFR**.
- Preserve **counts and widget contracts** from the mirror day (blanks, MCQs, durations, etc.).
- `topic_override` describes **this** day’s skill, not the mirror week’s topic.

---

## Authoring `depth_day`

Add **`depth_day=DaySource(...)`** on the **parent** only — never nest `depth_day` inside `depth_day`.

| Field | Base | Depth |
|-------|------|-------|
| `title` | Intro topic | **Distinct** title (same topic family, deeper angle) |
| `description` / `focus` | First exposure | What **extra** depth the learner gets |
| `teacher` | Teach from zero | Assume learner **saw base yesterday** (48w) |
| `activities` | 4 slots | **Same** archetypes/widgets as parent; new ids (e.g. `_depth` suffix) |
| Content tone | Base CEFR | Depth pass CEFR (see table above) |

Each depth day should include at least one of: error spotting, contrast with a neighbour structure, longer production, register / “when it sounds wrong”.

Full 56-row plans per band: [`docs/depth_topic_table.md`](depth_topic_table.md).

Optional one-off injectors live in `backend/scripts/` (e.g. `inject_depth_w*_a1a2.py`, `patch_b1b2_depth_w*.py`, `patch_c1c2_depth_w*.py`). Prefer editing the band file directly for small fixes; scripts are for bulk/reproducible inserts.

**Patch-script note:** when inserting `depth_day` before `WeekSource` boundaries, scope regex per week — week-ending days close with extra `),` layers; blind global patches break at week 2+.

---

## Day IDs and runtime access

| Pattern | Meaning |
|---------|---------|
| `day_24_WW_DD` | 24w course, calendar week `WW`, day `DD` (1–7) |
| `day_48_WW_DD` | 48w course, calendar week `WW`, day `DD` (1–7) |

```python
from app.modules.curriculum import file_source
from app.scoring import CourseLength

day = file_source.get_day(1, 0, course_length=CourseLength.WEEKS_48)  # week 1, Monday
day = file_source.get_day_by_id("day_48_01_02")
```

`file_source` resolves through `composer.resolve_day`, then `blueprint_adapter.adapt_day_source` flattens into task specs, teacher script, and override dicts for the session engine.

---

## Verification

### One band — all `depth_day` present

```bash
cd backend
uv run python -c "
from app.modules.curriculum.data.source_L_A1A2 import WEEKS_A1A2  # or B1B2 / C1C2
missing = []
for w in WEEKS_A1A2:
    for di, d in enumerate(w.days):
        if d.depth_day is None:
            missing.append((w.week_number, di+1))
        elif len(d.depth_day.activities) != 4:
            missing.append((w.week_number, di+1, 'incomplete depth'))
assert not missing, missing
print('depth_day count:', sum(1 for w in WEEKS_A1A2 for d in w.days if d.depth_day))
"
```

### 48w — depth topic ≠ previous calendar day

```bash
cd backend
uv run python -c "
from app.modules.curriculum import file_source
from app.modules.curriculum.data.composer import resolve_day
from app.scoring import CourseLength

BAND_START = 1  # A1A2=1, B1B2=17, C1C2=33
dupes = []
for cw in range(BAND_START, BAND_START + 16):
    for di in range(7):
        r = resolve_day(CourseLength.WEEKS_48, cw, di)
        if r.pass_index != 1:
            continue
        day = file_source.get_day(cw, di, course_length=CourseLength.WEEKS_48)
        prev = file_source.get_day(cw, di-1, course_length=CourseLength.WEEKS_48) if di else file_source.get_day(cw-1, 6, course_length=CourseLength.WEEKS_48)
        if day.topic == prev.topic:
            dupes.append((cw, di+1))
assert not dupes, dupes
print('48w depth topics distinct OK')
"
```

### Base-day batch (local weeks in one band)

```bash
cd backend
uv run python -c "
from app.modules.curriculum import file_source
from app.scoring import CourseLength

# Example: global 24w weeks 1–4 → band A1A2, local weeks 1–4
GLOBAL_START, GLOBAL_END = 1, 4
for gw in range(GLOBAL_START, GLOBAL_END + 1):
    for d in range(7):
        day = file_source.get_day(gw, d, course_length=CourseLength.WEEKS_24)
        assert len(day.task_archetypes_used) == 4
        acts = [file_source.task_spec_for(day, i)['activity'] for i in range(4)]
        assert acts == ['read','listen','write','speak'], (gw, d+1, acts)
        print(f'W{gw} D{d+1}:', day.topic[:50])
"

uv run pytest tests/test_composer.py tests/test_file_source.py tests/test_curriculum_v2_data.py -q
```

Cycle integrity tests (`test_cycle1_day_integrity.py`, etc.) read composed `WEEKS_24` — they still validate structure after band edits.

---

## Out of scope for source authoring

- `composer.py`, `loader.py`, `blueprint_adapter.py` (unless changing assembly logic deliberately)
- Archetype registry / session contracts (new activity **kinds** need code changes elsewhere)
- Frontend, DB migrations, scoring math
- Editing `source_24w.py` / `source_48w.py` content (shims only)

---

## Agent brief: author a 4-week base batch in one band

Use this block when asking an agent to fill **local weeks** in a single band file.

**Assignment template**

```markdown
Band file: `backend/app/modules/curriculum/data/source_L_B1B2.py`
Tuple: `WEEKS_B1B2`
Local weeks: 5–8 (mirror structure from local weeks 1–4, new topics)
Do NOT edit other bands or `depth_day` unless asked.
Topic plan: [table or link]
```

**Non-negotiable**

- 7 fully authored `DaySource` rows per week (no empty stubs).
- 4 activities per day: read → listen → write → speak.
- Mirror **local W−4** for weeks 5–8 (same archetypes/widgets/evaluators).
- Teacher: 3–4 steps, one `?` per step, wrap_up = readiness only.
- Deliverable: `file_source.get_day` succeeds for every global week in the batch (24w).

For **depth** batches, use [`docs/depth_topic_table.md`](depth_topic_table.md) and attach `depth_day=DaySource(...)` on existing parents only — do not rewrite base fields except fixing syntax you introduce.
