# Master prompt: 24w / 48w file-authored curriculum in production chat

Use this document as the **single implementation brief** for agents and engineers. Goal: after all phases, **24-week and 48-week learners** get the same **chat-session quality** that weeks 1–4 had under the old monolithic `source_24w.py` — scripted teaching, four deterministic activities, file-backed task specs, eval/feedback contracts — across the **full** calendar, with 48w **depth days** on the even pass.

Related docs: [`SOURCE_FILE.md`](SOURCE_FILE.md), [`depth_topic_table.md`](depth_topic_table.md), [`CLAUDE.md`](../CLAUDE.md).

---

## North star (acceptance)

A learner on **either** track can:

1. Open the dashboard → see **today’s real topic** and **four activities** matching the band file (not stale DB placeholders).
2. Start or continue today’s session → `DailySession` + chat `LearningSession` use **file source** for that `day_id`.
3. Experience teaching → scripted `__scripted_plan` steps, readiness handoff, then tasks in order **read → listen → write → speak** with authored `topic_override` / `generation_instructions` / static payloads where defined.
4. Complete evaluation and feedback using **file overrides** and score with the correct **24w vs 48w** reward table.
5. Advance day/week; pointer stays consistent with `day_{24|48}_WW_DD` IDs.

**48w-specific:** On **even** calendar days within each source pair (`pass_index=1`), chat uses **`depth_day`** content (distinct title, A2/B2/C2 depth where applicable), and copy can reflect “builds on yesterday” where product wants it.

**Parity reference:** `backend/tests/test_learning_session_file_mode.py` (W1D1 blueprint + persona), `backend/tests/test_session_lifecycle.py::test_authored_w1d1_uses_source_file_content_in_db_mode`, `backend/tests/test_file_source.py` (48w W1D1/D2 depth).

---

## Gold standard — what “like old source_24w weeks 1–4” means

The old flow for authored global weeks 1–4 was **not** “DB planner picks archetypes.” It was:

| Layer | Behavior |
|-------|----------|
| **Identity** | Stable `day_24_01_01` … `day_24_04_07` IDs |
| **Session start** | Four activities, fixed archetype order from file; all mandatory in file mode |
| **Task materialisation** | `task_specs` + `activity_contracts` from `blueprint_adapter` |
| **Teaching chat** | `topic`, `lesson_description`, `teacher_style`, `lesson_goal`, `__scripted_plan` from file |
| **WebSocket** | `session_blueprint` event aligned with authored teacher + activity contracts |
| **Overrides** | Per-activity evaluator/feedback overrides from `DaySource` |
| **DB** | Rows existed for FK/navigation; **runtime content overrode** seeded `suggested_archetypes` |

That behavior must hold for:

- **24w:** all **168** days (`day_24_*`), content = base `DaySource` only.
- **48w:** all **336** days (`day_48_*`), content = base on odd pass, `depth_day` on even pass (`composer.resolve_day`).

---

## Current state (baseline)

### Already working

- Band files + `composer.py` + `depth_day` assembly (`source_L_A1A2`, `B1B2`, `C1C2`).
- `file_source.get_day_by_id` for `day_24_*` and `day_48_*`.
- `SessionService.start_session` prefers file when day resolves.
- `LearningSessionService._persona_from_file` + scripted plan for file `day_id`s.
- Dashboard preview **activities** from file (`_preview_activities_for_day`).
- Stale unstarted session repair when file archetypes change.
- Tests: composer, file_source 48w depth, curriculum_v2_data counts, cycle integrity on composed `WEEKS_24`.

### Gaps to close (why this plan exists)

| Gap | Impact |
|-----|--------|
| Dashboard `topic` from **DB** only | Title can lag after band edits until re-seed |
| No API field for 48w **pass** / depth | Frontend cannot label “depth day” without inferring |
| `tasks_per_day` UI vs file mode | File days always use 4 activities (filtered by allowed toggles) — confusing copy |
| Frontend demo maps (`teaching/tasks/feedback` `source.ts`) empty for `"48w"` | Offline/demo paths broken; production WS path OK |
| `course_length` vs `day_id` prefix | Manual `/sessions/start` can mismatch |
| Ops: seed not in deploy docs | Fresh DB → 404 today-plan |
| End-to-end 48w chat | Less tested than 24w W1 |

---

## Architecture reminder (do not re-litigate)

```
Band files (DaySource + depth_day)
    → composer.compose_weeks(24w | 48w)
        → loader.load_weeks → seed_curriculum → PostgreSQL (index + fallback)
        → file_source → SessionService + LearningSessionService (source of truth at runtime)
```

**Rule:** Edit band files only for content. Re-run `uv run python -m scripts.seed_curriculum` after content changes so DB topics/IDs stay aligned.

---

## Phased implementation plan

### Phase 0 — Authoring & compose integrity (prerequisite)

**Owner:** Curriculum / data. **Blocks:** everything else if slots are blank.

**Deliverables**

- All band local weeks 1–8: 7 days × 4 activities, no blank `DaySource`.
- Every parent in 48w bands has `depth_day` (see `depth_topic_table.md`).
- `source_24w.py` / `source_48w.py` remain shims only.

**Verification**

```bash
cd backend
uv run pytest tests/test_composer.py tests/test_file_source.py tests/test_curriculum_v2_data.py -q
uv run pytest tests/test_cycle1_day_integrity.py tests/test_cycle2_day_integrity.py -q  # adjust if named per cycle
```

Optional band depth check — see [`SOURCE_FILE.md`](SOURCE_FILE.md) § Verification.

**Exit criteria:** `file_source.get_day_by_id("day_24_01_01")` and `day_48_01_02` succeed; 336 unique `day_48_*` topics where tests assert.

---

### Phase 1 — Backend: single display truth for dashboard APIs

**Goal:** `today-plan` and `start-today` expose the same **topic / CEFR / pass** the chat will use.

**Tasks**

1. Add helper (e.g. `_resolve_file_day_metadata(day_id)`) in `sessions/routes.py` or `file_source.py`:
   - `topic`, `explanation_brief`, `cefr_level`, `theme_type`
   - `is_file_authored: bool`
   - `pass_index: 0 | 1` (48w only; 0 for 24w)
   - `is_depth_day: bool` (`pass_index == 1` and 48w)
2. Extend `DashboardTodayPlanResponse` (+ `DashboardStartResponse`) in `schemas.py`:
   - `topic` → prefer file when authored (fallback `day.topic`)
   - Optional: `explanation_brief`, `cefr_level`, `course_length`, `is_depth_day`
3. Use file topic in `_serialize_dashboard_plan` call sites (today-plan, start-today).
4. Update `frontend/src/lib/sessions-api.ts` types and `DailyTaskPanel` to show `cefr_level` / depth badge when present.
5. Fix docstrings that still say “source_24w.py only” (`SessionStartRequest`, `SessionService.start_session`).

**Tests**

- `test_today_plan_uses_file_source_archetypes_when_day_is_authored` → assert `topic` matches file, not stale DB string.
- New: 48w `day_48_01_02` today-plan → depth topic + `is_depth_day=true`.

**Exit criteria:** Dashboard title matches chat `session.topic` for W1D1 24w and W1D2 48w without re-seed (activities already did).

---

### Phase 2 — Database & operations

**Goal:** Blank / new environments always have both calendars; deploys stay in sync.

**Tasks**

1. Document in README or `docs/SOURCE_FILE.md` deploy step:
   ```bash
   cd backend && uv run python -m scripts.seed_curriculum
   ```
2. Add CI job or pre-deploy check: `load_weeks(24w)` + `load_weeks(48w)` import cleanly (already in `test_curriculum_v2_data`).
3. Optional script: `scripts/verify_curriculum_seed_parity.py` — compare DB `topic` for sample days to `file_source` (fail if drift > 0 on W1–W4 sample).
4. Subscription → `preference.course_length` (`48w`) documented in onboarding checklist.

**Exit criteria:** Fresh docker Postgres + seed + new user → `GET /api/sessions/today-plan` 200 for `24w` and for user switched to `48w`.

---

### Phase 3 — Learning session / WebSocket parity (24w + 48w)

**Goal:** Chat path indistinguishable from old W1–4 for any authored `day_id`.

**Tasks**

1. Audit `LearningSessionService.create_session` / `_resolve_daily_session`:
   - Always call `_maybe_refresh_file_persona` when `day_id` is file-shaped.
   - Task queue built from `DailySession` attempts that were file-materialised (already expected).
2. Add tests mirroring W1D1 for **48w**:
   - `_persona_from_file("day_48_01_02")` → depth title, A2 `sub_level`, scripted plan from depth teacher steps.
   - Blueprint event test with `day_48_01_02` activity contracts.
3. Confirm `submit_activity` / task regen uses `file_get_day_by_id` on session’s `day_id` (grep `file_source` in `sessions/service.py` — extend tests if gaps).
4. Ensure `advance-day` increments `current_day_in_week` / `current_week` so 48w users hit `day_48_01_02` on day 2.

**Exit criteria:** `uv run pytest tests/test_learning_session_file_mode.py -q` includes 48w depth cases; manual WS smoke: teach → readiness → activity 1 on `day_48_01_01` and `day_48_01_02`.

---

### Phase 4 — Frontend product surfaces

**Goal:** UI reflects two tracks and file-backed plans; no reliance on empty demo stubs in production routes.

**Tasks**

1. **Dashboard** (`DailyTaskPanel`, `dashboard/page.tsx`):
   - Use API `topic`, `is_depth_day`, `cefr_level`.
   - Week progress: `totalWeeks` 24 vs 48 (already partial).
   - Copy: file mode = “4 activities today” (not `tasks_per_day` only).
2. **Session shell** (`sessions/[sessionId]`, chat chrome):
   - Show `course_length` from preference or API, not only `day_id` prefix inference.
3. **Settings / pricing:** 48w plan sets preference via existing subscription route.
4. **Demo / dev-only** (`ChatUI` + `teaching/source.ts` etc.):
   - Either generate demo entries from API for both tracks, or mark demo mode deprecated for curriculum QA.
   - Do **not** block production WS chat on filling `"48w": {}` stubs unless a route still reads them.
5. **Manual start** (`sessions/start/page.tsx`): validate `day_id` prefix matches selected `course_length`; show warning on mismatch.

**Exit criteria:** 48w user completes dashboard → chat → one full activity on week 1 day 1 and day 2 without local `source.ts` data.

---

### Phase 5 — End-to-end QA matrix

Run after Phases 1–4.

| # | Persona | Steps | Expected |
|---|---------|-------|----------|
| 1 | New user, 24w default | seed → diagnosis → today-plan → start chat | W1D1 topic + 4 archetypes match `file_source` |
| 2 | 48w preference | seed → set 48w → W1D1 chat | Base A1 simple present |
| 3 | 48w | W1D2 chat | Depth topic ≠ D1; A2 CEFR |
| 4 | 24w | Edit band title → **no** re-seed | Phase 1: dashboard shows new title from file |
| 5 | 24w | Edit band title → re-seed | DB + file aligned |
| 6 | Either | Disable `speak` in preferences | Plan omits speak archetype; no 422 |
| 7 | Either | Start session, kill before task 1, change file archetype, today-plan again | Stale session abandoned; new preview IDs |
| 8 | 24w | Week 5 day 1 (mirror week) | File archetypes mirror W1D1 structure, new topic |
| 9 | 48w | Calendar week 17 day 1 | B1B2 band base day resolves |
| 10 | Either | Complete day → advance | Pointer increments; next `day_id` correct prefix |

**Automated gate**

```bash
cd backend && uv run pytest tests/test_session_lifecycle.py tests/test_session_dashboard_routes.py tests/test_learning_session_file_mode.py tests/test_file_source.py tests/test_curriculum_v2_data.py -q
cd frontend && npm run lint && npm run build
```

---

### Phase 6 — Hardening & cleanup (optional)

- CI: `seed_curriculum` dry-run on PRs that touch `backend/app/modules/curriculum/data/*.py`.
- Remove or update obsolete comments referencing monolithic `source_24w` as SoT.
- Admin tool: “curriculum drift report” (DB topic vs file topic).
- Deprecate DB `suggested_archetypes` for days that are always file-authored (planner dead code path) — **only** if product agrees never to fall back.

---

## Implementation order (summary)

```
Phase 0 (authoring) → Phase 2 (seed/ops) can parallelize with Phase 1
Phase 1 (API topic/metadata) → Phase 4 (frontend displays)
Phase 3 (chat tests + 48w) → Phase 5 (QA)
Phase 6 (optional)
```

Minimum path to **“works like old W1–4”** for both tracks: **0 + 2 + 3 + 5** with **1** strongly recommended so dashboard and chat titles match.

---

## Agent brief templates

### Brief A — Phase 1 backend

```markdown
Implement file-first metadata for dashboard session APIs.

Read: docs/master_prompt.md Phase 1, app/modules/sessions/routes.py, schemas.py, file_source.py.

Add fields to DashboardTodayPlanResponse; prefer file topic/CEFR when file_get_day_by_id succeeds.
Extend tests in test_session_dashboard_routes.py for 24w stale DB topic and 48w depth day.
Update frontend sessions-api.ts + DailyTaskPanel for new fields.
Do not change scoring or archetype registry.
```

### Brief B — Phase 3 chat / 48w tests

```markdown
Extend learning-session file-mode tests to 48w depth days.

Read: docs/master_prompt.md Phase 3, test_learning_session_file_mode.py, learning_session/service.py.

Add tests for day_48_01_02 persona and session_blueprint parity with day_48_01_01.
Fix any bug found where chat persona does not refresh from file on resume.
```

### Brief C — Phase 4 frontend

```markdown
Align dashboard and session UI with 24w/48w file-backed today-plan.

Read: docs/master_prompt.md Phase 4, DailyTaskPanel, useSessionsFlow, preferences-api.

Consume is_depth_day / cefr_level from API; fix course_length vs day_id mismatch on manual start page.
Do not populate teaching/source.ts unless explicitly for offline demo mode.
```

---

## Key files index

| Area | Path |
|------|------|
| Band content | `backend/app/modules/curriculum/data/source_L_*.py` |
| Compose | `backend/app/modules/curriculum/data/composer.py` |
| Runtime bridge | `backend/app/modules/curriculum/file_source.py`, `blueprint_adapter.py` |
| DB seed | `backend/app/modules/curriculum/data/loader.py`, `scripts/seed_curriculum.py` |
| Session REST | `backend/app/modules/sessions/routes.py`, `service.py`, `schemas.py` |
| Chat WS | `backend/app/modules/learning_session/service.py`, `orchestrator.py` |
| Preferences | `backend/app/modules/preferences/models.py`, `subscriptions/routes.py` |
| Frontend | `frontend/src/components/dashboard/DailyTaskPanel.tsx`, `hooks/useSessionsFlow.ts`, `lib/sessions-api.ts` |
| Tests (reference) | `backend/tests/test_learning_session_file_mode.py`, `test_file_source.py`, `test_session_dashboard_routes.py` |

---

## Out of scope for this master prompt

- New activity **kinds** (archetype + contract registry changes).
- Rewriting scoring engine constants.
- LLM prompt redesign beyond wiring existing file specs.
- Authoring content inside `composer.py` / `loader.py` unless fixing a proven bug.
- Filling all weeks in frontend `teaching/source.ts` (demo-only unless product requests).

---

## Definition of done (program level)

- [ ] Phase 0 tests green on all three bands.
- [ ] `seed_curriculum` documented and run on staging/prod after data deploys.
- [ ] Phase 1: dashboard topic = file topic for authored days (24w + 48w depth).
- [ ] Phase 3: automated chat/file tests cover `day_48_01_01` and `day_48_01_02`.
- [ ] Phase 5 QA matrix rows 1–3 and 7 pass on staging.
- [ ] No regression: `test_authored_w1d1_uses_source_file_content_in_db_mode` still passes.

When all boxes are checked, **24w and 48w courses behave in chat like the legacy authored `source_24w.py` weeks 1–4**, extended across the full composed curriculum.
