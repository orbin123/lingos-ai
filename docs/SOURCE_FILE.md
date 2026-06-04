Use this as a **fixed preamble** you paste every time. Below it, add your **batch block** (week numbers, topic table, or “mirror topics from spec X”).

---

## Preamble: Author the next 4-week block in a level-band source file

### Role

You are filling in **exactly four consecutive source weeks** in one level-band file for the LingosAI 24-week course. Band files live under `backend/app/modules/curriculum/data/`:

| Global 24w weeks | Band file | Local source weeks | CEFR (24w) |
|------------------|-----------|-------------------|------------|
| 1–8 | `source_L_A1A2.py` | 1–8 | 1–4 A1, 5–8 A2 |
| 9–16 | `source_L_B1B2.py` | 1–8 | 1–4 B1, 5–8 B2 |
| 17–24 | `source_L_C1C2.py` | 1–8 | 1–4 C1, 5–8 C2 |

Runtime assembly is via `composer.py` (48w doubles each day into two consecutive calendar days). `source_24w.py` is a composed re-export for tests and seeders.

This is a **working prototype**: replicate proven structure, change topics and level only. Do not redesign the curriculum system.

---

### Batch I am asking for (filled in below this preamble)

- **Target weeks:** `___` through `___` (must be a block of 4: e.g. 9–12, 13–16).
- **Do not edit** any week outside this range (except fixing syntax errors you introduce).
- **Topic plan:** see the section **immediately below** this preamble.

---

### Course structure (non-negotiable)

- **24 weeks = 6 cycles × 4 theme weeks.** Theme order every cycle: `grammar` → `communication` → `vocabulary` → `confidence`.
- **7 days per week** (`DaySource` × 7). Each day must be fully authored (not empty stubs).
- **File:** the band module for your global week range (see table above). Edit **local** `week_number` 1–8 inside that file only (no registry, scoring, frontend, or 48w `depth_day` unless explicitly asked).

**CEFR on `WeekSource` shells** (band-local week numbers):

| Band | Local weeks | `cefr_level` | `sub_level_min`–`max` |
|------|-------------|--------------|------------------------|
| A1A2 | 1–4 / 5–8 | A1 / A2 | 1–2 / 3 |
| B1B2 | 1–4 / 5–8 | B1 / B2 | 4–5 / 6–7 |
| C1C2 | 1–4 / 5–8 | C1 / C2 | 8 / 8 |

Within your batch, each `WeekSource` must keep its `theme_type`, `cefr_level`, and `sub_level_*` shell values.

---

### Mirror rule (structural copy — saves time)

For **every** target week `W` and day index `D` (0 = Monday … 6 = Sunday):

> **Copy activity structure from week `W − 4`, day `D`.**

- Same four `archetype_id` values in the same order.
- Same `activity` kinds: **`read` → `listen` → `write` → `speak`** (sequences 1–4).
- Same `task_widget`, `evaluator`, `evaluation_widget`, `feedback_widget`, `mandatory`.
- Same **number of teacher steps** and step **roles** (`open` → teaching steps → `wrap_up`) as the mirror day.

**Change only:** `title`, `description`, `focus`, `lesson_goal`, teacher `instruction` text, `activity.id` suffixes, `topic_override`, `generation_instructions`, `widget_requirements` (topic/level wording).

**Do not:** new archetypes, reorder activities, new widgets, or different evaluator types.

**Structural mirror chain:** 5–8 mirror 1–4; 9–12 mirror 5–8; 13–16 mirror 9–12; etc. Earlier weeks in the chain must already be authored before you rely on them.

---

### Teacher behavior (same every cycle — prevents drift)

Teacher steps become the **scripted plan** (one AI turn per step). The live teacher agent requires:

1. **Intro (step 1, `id="open"`):** Greet; explain in **two short sentences** what today’s lesson is about; end with **one open question** (personal example, opinion, or short production). One question only.
2. **Teaching steps (middle):** **One rule/pattern per step.** Use the learner’s last answer when possible. End each step instruction with **one** engagement ask (produce, transform, correct, or share). Open-ended dialogue, but each step’s instruction must imply **one** question mark in the model output.
3. **Exit (final step, `id="wrap_up"`):** After the learner has shown the target pattern at least once, the instruction must say to ask **only:** `Ready to try the practice task?` — no new teaching, no recap, no “any other questions?”

**Authoring rules for `TeacherStep.instruction` text:**

- Mirror the **sentence patterns** of the `W−4` day’s steps; swap in the new topic/grammar only.
- **3 or 4 steps** total (match the mirror day’s count).
- Keep `TeacherBlueprint.readiness_prompt = "Ready to try the practice task?"` unless the mirror day differs.
- Keep `style="strict_kind_a1_friendly"` (used for all levels today).
- Do **not** put the target answer inside the question (no spoiling).
- Do **not** add extra steps (review, doubt-check, second readiness).

The runtime enforces: one message per turn, **at most one `?`**, ~60 words, readiness alone on the last turn. Write instructions so the LLM can comply.

---

### Task generator alignment

For each activity, `generation_instructions` and `widget_requirements` must:

- Target the **new day topic** and **current cycle CEFR** (slightly richer than the previous cycle, not C2).
- Preserve **counts and widget contracts** from the mirror day (e.g. number of blanks, MCQs, errors, passage length bands).

`topic_override` must describe the new day skill, not the mirror week’s topic.

---

### Level progression (topics get harder each cycle)

- **Same day slot, harder content:** Day 1 grammar in cycle 3 should be harder than day 1 grammar in cycle 2, which was harder than cycle 1 — but **same archetype layout** as `W−4`.
- Use the **batch topic table below** when provided; otherwise propose topics that fit the mirror day’s activity types and CEFR band.
- Teacher language stays short and concrete; tasks may be slightly longer at B1+.

---

### Per-day checklist (repeat × 28 days in a 4-week batch)

For target week `W`, day index `D`:

1. Open mirror: `WEEKS_24[W-1].days[D]` and `WEEKS_24[W-5].days[D]` (week `W−4`).
2. Copy mirror `DaySource` skeleton.
3. Update metadata + teacher steps (patterns from mirror, new topic).
4. Update each `ActivityBlueprint` (ids + topic-specific generation text).
5. Confirm: 4 activities, sequences 1–4, order read/listen/write/speak.

---

### Verification before done

```bash
cd backend
uv run python -c "
from app.modules.curriculum import file_source
START, END = ___ , ___   # your batch
for w in range(START, END+1):
  for d in range(7):
    day = file_source.get_day(w, d)
    assert len(day.task_archetypes_used) == 4
    acts = [file_source.task_spec_for(day,i)['activity'] for i in range(4)]
    assert acts == ['read','listen','write','speak'], (w,d+1,acts)
    print(f'W{w} D{d+1}:', day.topic[:50], '->', day.task_archetypes_used)
"
uv run pytest tests/test_file_source.py tests/test_curriculum_v2_data.py -q
```

If a `test_cycle1_day_integrity`-style test exists for your week range, run it too.

---

### Out of scope

- Weeks outside the batch; rewriting prior cycles “for quality.”
- New archetypes, contracts, or teacher system prompts.
- `source_48w.py`, frontend, migrations.

**Deliverable:** Replace empty `DaySource()` stubs in the target weeks with **28 complete days** that pass `file_source.get_day` for every day in the batch.

---

## How to use it

**1. Learn the preamble above.**

**2. Check the batch blocks topics for new batch pasted:**

**3. Rewrite the band source file for the new batch (local weeks 1–8)**

Here’s **17–20** (B2, Cycle 5 — Reasoning). Mirror **13–16** day-for-day for structure (`W17→W13` … `W20→W16`). Topics step up from the **13–16 plan** (and your authored **9–12**).

---

## Week 17 — Grammar (B2) ← mirror Week 13

| Day | Week 13 (B1+) | Week 17 (B2) — topic |
|-----|---------------|----------------------|
| 1 | Past perfect continuous | **Narrative tense control** — mix past simple, past perfect, and past perfect continuous in one story |
| 2 | Third conditional | **Mixed conditionals** — past condition → present result (*If I had…, I would… now*) |
| 3 | Causative have/get | **Impersonal & advanced passive** — *It is said that…, He is believed to have…, The decision was made…* |
| 4 | Reduced & non-defining relatives | **Participle & adverbial clauses** — *Having finished…, Written in 2020…, Although tired,…* |
| 5 | Reporting verbs & patterns | **Stance & distancing in reporting** — *It is argued/claimed/suggested that…, According to…* |
| 6 | Wish & regret | **Inversion for emphasis** — *Never have I…, Had I known…, Not only… but also…* |
| 7 | Formal linkers & nuance | **Academic & professional cohesion** — *thereby, thus, consequently, in light of, with regard to* |

**Progression:** B1+ = advanced patterns; B2 = **control in long discourse, mixed hypotheticals, impersonal style, dense clauses, stance, rhetoric-level grammar**.

---

## Week 18 — Communication (B2) ← mirror Week 14

| Day | Week 14 (B1+) | Week 18 (B2) — topic |
|-----|---------------|----------------------|
| 1 | Conflict resolution & middle ground | **Diplomatic mediation** — two sides, neutral language, workable outcome |
| 2 | Giving constructive feedback | **Upward & sensitive feedback** — to a manager, senior peer, or client |
| 3 | Pros, cons & recommending an option | **Strategic recommendation** — option, risks, mitigation, clear recommendation |
| 4 | Leading a short meeting | **Chairing with disagreement** — keep agenda, manage conflict, assign actions |
| 5 | Handling objections | **Formal advocacy** — defend a position with evidence under challenge |
| 6 | Stakeholder communication | **Executive summary** — compress complex info for different seniority levels |
| 7 | Facilitating discussion | **Panel-style discussion** — multiple views, synthesise, land a shared takeaway |

---

## Week 19 — Vocabulary (B2) ← mirror Week 15

| Day | Week 15 (B1+) | Week 19 (B2) — topic |
|-----|---------------|----------------------|
| 1 | Science & research | **Innovation & future tech** — automation, algorithm, disruption, ethical AI |
| 2 | Arts & creativity | **Law & justice** — legislation, verdict, precedent, plaintiff, appeal |
| 3 | Ethics & global issues | **Politics & governance** — coalition, reform, referendum, mandate, austerity |
| 4 | Business & economics | **Finance & markets (advanced)** — equity, liability, portfolio, volatility, stakeholder |
| 5 | Media literacy | **Psychology & behaviour** — cognitive, perception, motivation, implicit, resilience |
| 6 | Leadership & influence | **Rhetoric & argumentation** — rhetoric, concede, undermine, compelling, nuance |
| 7 | Review & word building | **Review & word building** — consolidate week 19 |

---

## Week 20 — Confidence (B2) ← mirror Week 16

| Day | Week 16 (B1+) | Week 20 (B2) — topic |
|-----|---------------|----------------------|
| 1 | Facilitating difficult conversations | **High-stakes conversations** — pressure, stakes, stay composed |
| 2 | Counterarguments & rebuttals | **Evidence-based debate** — claim, evidence, partial concession, rebuttal |
| 3 | Vision & long-term narrative | **Professional brand story** — arc: past → present → direction |
| 4 | Giving & receiving critical feedback | **Public challenge** — tough question, stay clear, don’t get defensive |
| 5 | Strong close & call to action | **Stakeholder pitch** — problem, solution, proof point, ask |
| 6 | Presentation with brief Q&A | **Keynote-style segment** — ~90s structured talk + one hard question |
| 7 | Full confidence showcase (B1+) | **Full confidence showcase (B2)** — Cycle 5 wrap-up |

---

## Paste block

```markdown
### Batch specifics — weeks 17–20

**Target weeks:** 17–20 | **Mirror structure from:** 13–16 (day-for-day; author 13–16 first)
**CEFR:** B2 | **sub_level:** 6–7

| W | D | Theme | Title / topic |
|---|----|-------|----------------|
| 17 | 1 | grammar | Narrative tense control |
| 17 | 2 | grammar | Mixed conditionals |
| 17 | 3 | grammar | Impersonal & advanced passive |
| 17 | 4 | grammar | Participle & adverbial clauses |
| 17 | 5 | grammar | Stance & distancing in reporting |
| 17 | 6 | grammar | Inversion for emphasis |
| 17 | 7 | grammar | Academic & professional cohesion |
| 18 | 1 | communication | Diplomatic mediation |
| 18 | 2 | communication | Upward & sensitive feedback |
| 18 | 3 | communication | Strategic recommendation |
| 18 | 4 | communication | Chairing with disagreement |
| 18 | 5 | communication | Formal advocacy |
| 18 | 6 | communication | Executive summary |
| 18 | 7 | communication | Panel-style discussion |
| 19 | 1 | vocabulary | Innovation & future tech |
| 19 | 2 | vocabulary | Law & justice |
| 19 | 3 | vocabulary | Politics & governance |
| 19 | 4 | vocabulary | Finance & markets (advanced) |
| 19 | 5 | vocabulary | Psychology & behaviour |
| 19 | 6 | vocabulary | Rhetoric & argumentation |
| 19 | 7 | vocabulary | Review & word building |
| 20 | 1 | confidence | High-stakes conversations |
| 20 | 2 | confidence | Evidence-based debate |
| 20 | 3 | confidence | Professional brand story |
| 20 | 4 | confidence | Public challenge |
| 20 | 5 | confidence | Stakeholder pitch |
| 20 | 6 | confidence | Keynote-style segment |
| 20 | 7 | confidence | Full confidence showcase (B2) |
```

**Note:** Weeks **13–16 are still empty** in the repo — author those before **17–20**, or structurally mirror **9–12** only if you skip 13–16 (not recommended; breaks the `W−4` chain). **21–24** (C1) would mirror **17–20** next.