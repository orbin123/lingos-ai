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

### 4. Phase 7 cutover — safe, additive

Status as of Phase 7:
- Backend `use_new_session_flow` default is **True**.
- Frontend `NEXT_PUBLIC_USE_NEW_SESSION_FLOW` default is **true** (in
  `.env.example`; `.env.local` flipped to match).
- Legacy modules (`learning_session/`, `responses/`, `tasks/service.py`,
  `curriculum/rotation.py`) carry a "DEPRECATED — Phase 7" banner in
  their module docstrings. They remain **mounted and functional** as a
  rollback path.
- No tables dropped. `enrollment_skill_history` is still consumed by the
  legacy `tasks/service.py` rotation engine; dropping it now would break
  the rollback contract.
- No code deletions. Phase 8 (true cutover) handles destructive cleanup
  after observation in production.

To roll back: set both flags to False — no redeploy required.

### 5. Phase 4 LLM agents — wired into production

The three sessions agents (`LLMEvaluator`, `LLMFeedbackGenerator`,
`LLMTaskGenerator`) live in `app/ai/sessions/` and are constructed via
`build_default_agents()` in routes. They use ONE parameterized prompt
each rather than the spec's per-archetype prompt files — the archetype's
rubric / weight_map is interpolated at call time.

Failure mode: every agent has a graceful fallback. If the LLM is
unavailable users see degraded but consistent output (mid-range scores,
stub feedback wording, stub task content) rather than a 500. Logged at
WARNING.

---

## Phase 8 backlog (destructive cutover — not done yet)

Sequence carefully, after observing the Phase 7 flag-on flow in
production for at least one full week:

1. **Delete `learning_session/` module** (~2061 LOC). Remove WebSocket
   route, `LearningSession` model + table, all tests.
2. **Delete `responses/` module** (everything outside the legacy admin
   QA review flow). Move admin-facing pieces to `admin/` if needed.
3. **Delete `tasks/service.py`** (1451 LOC of rotation glue) and the
   `/tasks/next` route. Keep `Task` / `UserTask` ORM if anything reads
   them; otherwise drop those tables too.
4. **Delete `curriculum/rotation.py`**, `curriculum/constants.py`
   (the `WEEK_SCHEDULE` half), `curriculum/topics.py`, and the legacy
   `data/courses/topics_*.json` + `beginner_*.json` files.
5. **Drop tables**:
   - `enrollment_skill_history` (orphan once tasks/service.py is gone)
   - `learning_sessions`
   - `user_responses`, `evaluations`, `feedbacks` (after admin QA path
     migrates to `activity_feedback`)
   - Eventually `user_skill_scores` (WMA cache) once stats/dashboard
     migrate to `SkillPoints`.
6. **Drop legacy `task_type_enum` values** that no longer appear in
   `Task` rows.
7. **Delete obsolete tests** (`test_curriculum_rotation`,
   `test_planner_e2e_five_days`, `test_learning_session_readiness`,
   `test_points_calculator`, etc.) — these currently produce the 16
   pre-existing failures.
8. **Remove the feature flag** itself.
9. **Frontend**:
   - Delete `/task/chat/*` routes
   - Delete `useNextTask`, `useSubmitResponse`, `taskStore`
   - Delete legacy `task-widgets/*` set in favour of the new
     `components/sessions/widgets/*` set
   - Wire `DailyTaskPanel` to `/sessions/start` natively (no flag
     branch).
10. **Diagnosis remap** — diagnosis still seeds `UserSkillScore`. Switch
    to `SkillPoints` once the legacy WMA path goes.

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
