# LingosAI Restructure — Phase 0 Decisions

This file captures the binding decisions for the LingosAI restructure. Numbers
and identifiers in this file are the contract — when a question comes up later
(`why is starting points 0?` / `why are we still saying "expression"?`), the
answer lives here first, and only here.

> Revisit per phase. Update inline (don't append a "v2" — let git track history).
> Reference this file from PR descriptions for any change that touches scoring,
> curriculum naming, or session lifecycle.

---

## Locked (Phase 0 — applied in Phase 1+)

### 1. Initial sub-skill points

**Diagnosis is the source of initial points.** A user who completes diagnosis
is seeded between **2.0–4.0 / 10 per sub-skill** (i.e. 2000–4000 internal
points), using the conversion `1.0 score = 1000 points`.

The scoring engine itself does **not** own a default starting value — it only
computes per-session deltas. Users who somehow reach the session pipeline
without completing diagnosis are an edge case handled at the session boundary
(default to 0; force them through diagnosis before they can earn points).

This means no `DEFAULT_STARTING_POINTS` constant in `app/scoring/`. The
diagnosis module owns the seed value, not the scoring engine.

### 2. Sub-skill names

**Keep the legacy DB names** as the canonical identifiers throughout the
codebase:

```
grammar, vocabulary, pronunciation, fluency, expression, comprehension, tone
```

The restructuring spec uses friendlier names (`thought_org`, `listening`,
`tone_social`). These are **labels, not identifiers** — they may show up in
prompt text, UI strings, and the spec itself, but they never appear in DB
rows, model code, archetype weight maps, scoring outputs, or test fixtures.

Alias map for the doc → code translation (declared in
`app/scoring/constants.py` as `SUB_SKILL_ALIASES`):

| Doc name      | Code name      |
| ------------- | -------------- |
| `thought_org` | `expression`   |
| `listening`   | `comprehension`|
| `tone_social` | `tone`         |

A hard rename is deferred (was Phase 5 in the original plan). If it ever
lands, this section is the only thing that changes — the alias map disappears,
and every other reference is already a legacy name.

### 3. No slowdown rule

The current production code halves earnings at score ≥ 8.0. **The new engine
does not.** Match the doc's deterministic reward table verbatim.

Cap behaviour:
- A sub-skill's **internal total** caps at `MAX_POINTS_PER_SUBSKILL` (10000).
- The **displayed dashboard score** caps at 10.0.
- The **`points_earned` delta** stays uncapped — the "+55 pts" notification
  still fires when a user at the cap completes an excellent activity, even
  though their visible score does not move.

This split is implemented in `app/scoring/engine.py` as two separate
functions: `aggregate_session()` returns uncapped earnings;
`apply_to_totals()` clamps the totals.

---

## Deferred (revisit at the listed phase)

### Replay rule scope — Phase 3
Open: is "first attempt today counts" keyed on `(user, day_id)` or on
`(user, day_id, archetype_id)`? Working default: `(user, day_id)`. Only one
session per day awards points; subsequent attempts produce feedback but no
new earnings.

### LearningSession replacement — Phase 3
Open: replace the existing `learning_session/` module outright, or repurpose
it as the session-state envelope. Working default: build a clean
`sessions/` module and retire `learning_session/` in Phase 7.

### Diagnosis seed target — Phase 8
Open: diagnosis currently seeds `UserSkillScore` (the WMA cache). Decision: it
will seed `SkillPoints` directly under the new flow. Confirm at Phase 8.

### Feature flag granularity — Phase 3 / 6
Open: single `USE_NEW_SESSION_FLOW` flag vs. one-per-concern (scoring,
sessions, curriculum). Working default: single flag, named
`USE_NEW_SESSION_FLOW`.

---

## Reference

- Restructure spec: see the original brief used as input to this plan.
- Scoring math, archetype IDs, weight maps: `app/scoring/`.
- Phase-by-phase file map: see prior planning output (kept out of this repo
  to avoid drift — recreate from `app/scoring/` + this file as needed).
