# Agent Walkthrough — Final Fixes (post GPT‑5 migration)

> One section per completed phase. The next session reads this first. Newest at the bottom.

---

## Phase 0 + Phase 1 — Teaching agent: restore real, step‑by‑step teaching

**Session date:** 2026‑06‑23
**Branch:** `fix/teaching-agent-fast-model-and-timeout`
**PR:** https://github.com/orbin123/lingos-ai/pull/135 (Phase 0 docs bundled in, per the plan's recommendation A)

### What changed & why
Turn 1 of every lesson was a canned "Say 'ready' when you want to begin." with zero teaching (screenshot: `teaching_agent_no_teaching.png`). Two compounding causes:
1. The teacher **buffers its whole LLM turn** then yields one chunk, but the service waited only **8 s** for that first chunk. GPT‑5 (`reasoning_effort=medium`) routinely needs **>8 s** to think+generate, so `_timed_chunks` timed out, broke with an empty buffer, and emitted the hardcoded outer fallback.
2. GPT‑5 is a reasoning model → **ignores `temperature`**, so the teacher's tuned `0.4` was already dead.

The fix is the **hybrid per‑agent model routing** the whole plan rests on, applied to the teacher:
- Repointed `OPENAI_CHAT_MODEL` `gpt-5` → **`gpt-4.1-mini`** (non‑reasoning): ~1 s first token + `temperature=0.4` honored.
- Raised the teaching **and** follow‑up first‑chunk timeouts **8 s → 30 s** (defense‑in‑depth). Existing fallback logs kept.

### Files changed
- `backend/app/core/config.py` — `OPENAI_CHAT_MODEL` default `gpt-5` → `gpt-4.1-mini` (+ rewritten comment; `OPENAI_REASONING_EFFORT` clarified as reasoning‑model‑only).
- `.env.example` (repo root) — same default + comment. (`.env.production.example` doesn't pin the model — uses the config default — so untouched.)
- `backend/app/modules/learning_session/service.py` — `_TEACHING_STREAM_FIRST_CHUNK_TIMEOUT_S` and `_FOLLOWUP_STREAM_FIRST_CHUNK_TIMEOUT_S` `8.0` → `30.0` (+ explanatory comment). Chunk (inter‑token) timeouts left at 20 s — the teacher yields one buffered chunk, so only the first‑chunk budget matters.
- `backend/tests/unit/ai/test_openai_client_models.py` — pin `gpt-4.1-mini` as non‑reasoning + a test that its `temperature=0.4` is honored.
- `backend/tests/unit/learning_session/test_teaching_stream.py` *(new)* — real `_stream_teaching_turn` yields a fast teacher turn (not the canned fallback); first‑chunk budget ≥ 30 s.
- `backend/tests/integration/learning_session/test_learning_session_file_mode.py` — new test driving `process_message_stream` across two relevant answers (two distinct teaching turns, no activity) then an off‑topic reply (redirected, not advanced).
- `.gitignore` — `/docs` → `/docs/*` + `!/docs/Final_fixes/` (Phase 0; git can't re‑include under a fully‑excluded parent, hence `/docs/*`).
- `docs/Final_fixes/**` — plan + this walkthrough + 4 screenshots now tracked.

### How verified (proof)
- Backend gates: `ruff format` (clean), `ruff check` (**All checks passed**), `mypy app` (**no issues, 270 files**).
- `uv run python -m pytest tests/unit` and `tests/integration` — both exit 0, no failures. The 4 new/extended tests pass.
- **Offline runtime smoke** (no network — client construction is local): `settings.OPENAI_CHAT_MODEL = gpt-4.1-mini`, default client `is_reasoning=False`, `reasoning_effort=None`, and `_maybe_rebind_temperature(0.4).temperature == 0.4` on a fresh instance → the teacher's 0.4 now reaches the API (it was a dropped no‑op on gpt‑5).
- **Not run:** a full live browser E2E (uvicorn + `npm run dev` + a seeded A1 session driving real GPT‑4.1‑mini WebSocket turns). It needs a seeded curriculum DB + a live key + real LLM spend, which this environment isn't set up for. The integration test exercises the exact regressed paths (`_stream_teaching_turn`, `process_message_stream`) with only the LLM boundary stubbed, which is the deterministic equivalent. Worth a manual demo‑day walkthrough before the interview.

### What the next session must know
- **Phases 1 & 2 share `config.py` (and Phase 2 also `factory.py`).** This PR already set `OPENAI_CHAT_MODEL=gpt-4.1-mini`, so evaluator + feedback **already ride that fast non‑reasoning default** (their `temperature` 0.2/0.4 are now live). **Phase 2's remaining work** is: add `OPENAI_TASKGEN_MODEL=gpt-5` + `OPENAI_TASKGEN_REASONING_EFFORT=high`, build a dedicated task‑gen client in `factory.build_default_agents`, and make `error_correction` feedback deterministic. Do **not** re‑touch `OPENAI_CHAT_MODEL`. Rebase Phase 2 on `main` after this merges to avoid churn.
- Heads‑up for Phase 2: `tests/integration/admin/test_ai_request_logging.py::test_build_default_agents_shares_one_inner_client` currently asserts the **task generator shares the same inner client** as eval/feedback (`gen_a.llm._inner is inner_a`). When Phase 2 gives task‑gen its own gpt‑5 client, **that assertion must be updated** (gen should no longer share the inner client).
- Phase 0 is done: `docs/Final_fixes/` is tracked. Future phases can edit this walkthrough as a normal tracked file. Because docs‑only PRs to `main` are blocked, keep bundling any docs edits into a code PR (every phase changes code anyway).
- `docs/` (the rest) is still gitignored — only `docs/Final_fixes/` is whitelisted.

### Deferred follow‑ups
- **S1 (true streaming):** the teacher still buffers the whole turn then yields once, so even on the fast model the learner waits for the full turn. Real token streaming would make chat feel alive and render the first‑chunk timeout moot. Not required for the demo.
- **S3 (observability):** the fallback paths still only log (`teacher.fallback_used`, `teaching_turn_streaming_failed`). A Sentry breadcrumb/metric would make a future regression loud. Recommended before the demo.
- Curriculum content: confirm the A1 days you'll demo carry a multi‑step `__scripted_plan` (thin/1‑step plans make the teacher free‑form and feel sparse — that's a content issue, not the agent).

---

## Phase 2 — Evaluation & feedback accuracy on rule‑based tasks

**Session date:** 2026‑06‑23
**Branch:** `fix/eval-feedback-model-routing-and-determinism` (stacked **on the Phase 1 branch**, not `main`)
**PR:** https://github.com/orbin123/lingos-ai/pull/136 — **base = `fix/teaching-agent-fast-model-and-timeout` (#135)**, because the `OPENAI_CHAT_MODEL=gpt-4.1-mini` foundation *and* the `docs/Final_fixes/` setup live only on the Phase 1 branch, not yet on `main`. Merge **after #135**; GitHub auto‑retargets this PR to `main` when #135 merges (rebase if the squash conflicts on `config.py`/`factory.py`).

### What changed & why
Screenshot `tasks_eval_feedback_distorted.png`: an error task where grading marks wrong answers right and feedback lists **3** mistakes when only **2** exist. Two compounding causes, fixed with the plan's two levers (GPT‑5 ignores `temperature` → the lever is **model routing + `reasoning_effort`**):

1. **Task‑generation quality.** Gave the task generator its **own** reasoning‑model client — `gpt-5` at **HIGH** effort — via new env‑driven settings, wired in `factory.build_default_agents`. Evaluator + feedback stay on the fast non‑reasoning interactive default (`gpt-4.1-mini` from Phase 1), where their `temperature` 0.2/0.4 now actually applies. Higher effort → cleaner, single‑error, on‑topic generated sentences (the temperature‑equivalent lever for a reasoning model).
2. **Feedback over‑counting ("3 vs 2").** `error_correction` carries a per‑item answer key (`sample_answer`) but was in the open‑ended set, so the LLM re‑derived (and invented) mistakes. Moved it to the **deterministic** path: compute confirmed wrong items by exact sentence‑match against `sample_answer` (case/trailing‑punctuation insensitive) and render **exactly** those — the LLM can no longer add a phantom third item; all‑correct → zero mistakes.

### Files changed
- `backend/app/core/config.py` — new `OPENAI_TASKGEN_MODEL` (`gpt-5`) + `OPENAI_TASKGEN_REASONING_EFFORT` (`high`) settings.
- `.env.example` — same two vars + comment. (`.env.production.example` only lists `OPENAI_API_KEY` and relies on config defaults — left untouched, matching Phase 1.)
- `backend/app/ai/sessions/factory.py` — new `_shared_taskgen_client()` (cached gpt‑5/high client); `build_default_agents` wraps **only** the task generator with it; eval/feedback keep the shared default.
- `backend/app/ai/sessions/prompts.py` — new `compute_error_correction_wrong_items()` + two helpers (`_normalize_correction_sentence`, `_error_correction_rule_hint`).
- `backend/app/ai/sessions/llm_feedback.py` — removed `error_correction` from `_OPEN_ENDED_WIDGET_KEYS`; new dispatch + post‑process branches; new `_normalize_error_correction_mistakes()`.
- `backend/tests/unit/ai/test_llm_feedback.py` — "3 vs 2" regression + all‑correct‑shows‑none.
- `backend/tests/unit/ai/test_llm_feedback_helpers.py` — `compute_error_correction_wrong_items` unit coverage + prompt‑injection (no longer open‑ended).
- `backend/tests/unit/ai/test_factory_model_routing.py` *(new)* — task‑gen on `OPENAI_TASKGEN_MODEL`+high while eval/feedback share the default; defaults pinned to gpt‑5/high.
- `backend/tests/integration/admin/test_ai_request_logging.py` — updated the inner‑client‑sharing assertion (task‑gen now has its **own** client; the Phase‑1 heads‑up).

### How verified (proof)
- Backend gates: `ruff format` (2 files reformatted, then clean), `ruff check app tests` → **All checks passed**, `mypy app` → **Success: no issues in 270 files**.
- `python -m pytest tests/unit tests/integration` → **exit 0** (all pass). Targeted Phase‑2 set = **43 passed** (`test_llm_feedback`, `test_llm_feedback_helpers`, `test_factory_model_routing`, `test_openai_client_models`, `test_ai_request_logging`).
- `export_openapi.py` → **no drift** (no routes changed).
- **Determinism proof** (the "3 vs 2" fix): with the fake LLM hallucinating 3 mistakes on a 3‑item task where only 2 items were left unfixed, feedback renders **exactly** the 2 real misses; all‑correct renders **none**.
- **Not run:** live browser E2E (needs seeded curriculum DB + live key + real gpt‑5 spend). The unit/integration tests stub only the LLM boundary and exercise the exact regressed paths.

### What the next session must know
- **Plan correction — read this.** The plan claims error‑correction grading is *deterministic* via `agents/evaluator.py:893`. In the **V2 sessions flow that's false**: `LLMEvaluator.evaluate` (`app/ai/sessions/llm_evaluator.py`) has **no** error‑correction branch, so the **score** comes from the **generic LLM eval path**. `agents/evaluator.py` is the older LangGraph evaluator, not used by `SessionService`. Phase 2 therefore made only the **feedback mistakes list** deterministic (computed from `sample_answer`); the **score stays LLM‑driven** (`WRITE_ERROR_CORR` is *not* in `_DETERMINISTIC_SCORE_ARCHETYPES`). If you later want score+mistakes fully consistent, making the error‑correction **score** deterministic too is a clean follow‑up (out of Phase 2 scope).
- error_correction `user_response` is a **flat `{item_id: text}` map** (confirmed in `TaskWidgetFrame.tsx`), and the projected `task_content` has `items[].incorrect_sentence` + `items[].sample_answer` (`contracts/base.py:ErrorCorrectionItem`).
- **Remaining phases: 3 and 4.** Plan's recommended order was 0→1→4→2→3; the user ran 2 before 4, so 3 (empty rule card, frontend‑only, smallest) and 4 (WebSocket resilience) are left. Both are **independent of `config.py`/`factory.py`** and can branch off `main` once #135 + #136 land — no more stacking needed. **Phase 3 note:** the plan's optional step adds `grammar_rule_to_practice` to `ErrorCorrectionTask` (`llm_task_generator.py:272`); Phase 2 did **not** touch that schema.
- Merge order: **#135 → #136**. If #136 still shows Phase 1's diff after #135 merges, rebase `fix/eval-feedback-model-routing-and-determinism` onto `main`.

### Deferred follow‑ups
- **S2 (pre‑delivery quality gate):** if gpt‑5/high still lets multi‑error/off‑topic sentences through, add a judge‑backed structural gate (`factory._shared_judge_client`) that rejects+regenerates bad error tasks. Belt‑and‑suspenders; not required for the demo.
- **Dead debug cruft:** `llm_task_generator.py` has `_agent_debug_log()` (a Cursor `# region agent log` block) that writes to `.cursor/debug-dfa507.log` on every listening‑task generation, swallowing all exceptions. It's leftover agent‑debugging instrumentation and should be removed (flagged as a separate task).
- **error‑correction score determinism** (see "next session must know") — optional consistency improvement.

---

## Phase 3 — Empty "Correction rule" box

**Session date:** 2026‑06‑24
**Branch:** `fix/empty-correction-rule-card` (off `main` — #135 + #136 already merged, so no stacking needed)
**PR:** https://github.com/orbin123/lingos-ai/pull/137

### What changed & why
Screenshot `correction_rule_empty.png`: error‑correction tasks rendered a blank orange **CORRECTION RULE** card with no text. Root cause confirmed: ~30 task widgets render `<RuleCallout label=…>{task.grammarRule}</RuleCallout>` **unconditionally**, and the error‑correction LLM output schema carries **no rule field**, so `task.grammarRule` arrives as `""` and the component still drew an empty labelled box. (The generic `runtimeMapping.tsx:144` path already guarded with `grammarRule && …`; the per‑widget callers didn't.)

Fix = the plan's recommended **step 1, frontend‑only**: guard inside `RuleCallout` itself (in `TaskWidgetFrame.tsx`) — return `null` when its children are empty/whitespace via a small `hasRuleContent(node)` helper (handles `""`, whitespace, `null`/`undefined`/boolean, and recurses arrays; real strings / numbers / elements render). One change fixes **every** widget at once without deleting the rule for tasks that *do* carry one. Did **not** do the optional backend step (adding `grammar_rule_to_practice` to `ErrorCorrectionTask`) — deferred below.

### Files changed
- `frontend/src/components/chat/tasks/task_widgets/TaskWidgetFrame.tsx` — new private `hasRuleContent()` helper + an early `return null` guard in `RuleCallout`.
- `frontend/tests/unit/components/RuleCallout.test.tsx` *(new)* — `RuleCallout` renders null for `""`/whitespace/nullish, renders for real content; `ErrorCorrectionTaskWidget` with empty `grammarRule` shows no card, with a real rule shows it. (Tests live under `frontend/tests/**`, not colocated — see `vitest.config.ts` `include`.)
- `docs/Final_fixes/AGENT_WALKTHROUGH.md` — this entry (bundled into the code PR; docs‑only PRs to `main` are blocked).

### How verified (proof)
- Frontend gates all green: `npm run lint` → **0 errors** (89 pre‑existing warnings, none in the changed files); `npx tsc --noEmit` → **exit 0**; `npm test` → **23 files / 114 tests pass** (incl. the 6 new); `npm run build` → **Compiled successfully**, exit 0.
- **Live browser proof** (this is a purely visual frontend fix, so unlike Phases 1–2 it *was* feasible without the backend): rendered the real `ErrorCorrectionTaskWidget` via a throwaway dev page (`npm run dev`), one instance with empty `grammarRule` and one with a real rule. Accessibility snapshot + screenshot confirm the empty case jumps straight from the task pills to the question — **no orange card** — while the real‑rule control still shows `CORRECTION RULE` + its text. No console errors. The throwaway page was deleted before committing (`git status` clean of it; gate runs reflect the committed tree).
- No backend routes changed → **no OpenAPI/Alembic step**.

### What the next session must know
- **Only Phase 4 (WebSocket resilience) remains.** It's `config.py`/`factory.py`‑independent and branches cleanly off `main` once #137 merges. It's frontend‑heavy (`frontend/src/app/task/chat/[sessionId]/page.tsx`) + a small backend ping/pong handler (`learning_session/router.py`); see the plan's Phase 4 for the four layered fixes (heartbeat, universal reconnect, token refresh on reconnect, "Reload session" CTA).
- This PR moved the empty/whitespace guard into `RuleCallout`, so the per‑widget external guards on `ListenCloze`/`ListenDictation` and the generic `runtimeMapping.tsx:144` are now redundant (harmless — they short‑circuit before an already‑safe component). No need to touch them.
- The fix is generic: **any** widget passing an empty `grammarRule` now hides its callout, not just error‑correction.

### Deferred follow‑ups
- **Optional Phase 3 step 2 (populate the rule):** add `grammar_rule_to_practice: str | None = None` to `ErrorCorrectionTask` (`backend/app/ai/sessions/llm_task_generator.py:272`); the projection already maps it (`projection.py:163‑165`). Would show a real one‑line rule instead of hiding the card. Not required for the bug; skipped to keep this the smallest, lowest‑risk PR.
- **Dead debug cruft** (carried over from Phase 2): `llm_task_generator.py` `_agent_debug_log()` writes to `.cursor/debug-dfa507.log` and swallows exceptions — should be removed in a separate cleanup.

---

## Phase 4 — WebSocket resilience: kill "Connection closed" for good

**Session date:** 2026‑06‑24
**Branch:** `fix/websocket-resilience-heartbeat-reconnect` (off `main`)
**PR:** https://github.com/orbin123/lingos-ai/pull/138

### Merge order (resolved)
This branch was cut from `main` while #137 (Phase 3) was still open, so it temporarily re‑included the Phase 3 entry to keep the walkthrough ordered. #137 was merged first; this branch was then rebased onto `main` and the duplicate Phase 3 section dropped (the Phase 3 entry above now comes from #137). The code never overlapped Phase 3 (`TaskWidgetFrame.tsx`) — only this doc did.

### What changed & why
Screenshot `connection_closed.png`: mid‑session the chat shows a permanent "Connection closed. Reconnecting…" and the learner is stranded — can't submit, never recovers. Three compounding causes (all confirmed in code), fixed in four layers:

1. **No heartbeat → ALB 120s idle drop.** The backend receive loop had no keepalive handling, so any 2‑minute lull (reading, or a long buffered LLM turn) dropped the socket. **Fix:** the client pings every 25s; a new `ping` short‑circuit in the WS receive loop (`router.py`) replies `pong` *before* the rate‑limit guard and `process_message_stream`, so it never consumes the message budget or touches session state.
2. **Phase‑gated reconnect + stuck‑on‑failed‑reconnect.** The reconnect effect bailed unless `phase==="submitted"`/`feedback_loading`, and `onclose`/`onerror` returned early during an in‑flight reconnect (`intent !== "none"`), leaving `connectionState` stuck on "connecting" with no retry. **Fix:** universal, phase‑independent auto‑reconnect with capped exponential backoff (600ms→…→10s, 5 attempts); failed reconnects now mark the socket closed so the next attempt fires.
3. **Stale token on reconnect.** The socket carried the localStorage JWT, validated once at the handshake; a session past the 20‑min access‑token TTL reconnected with an expired token → server `4401` → permanently stuck. **Fix:** `refreshAccessToken()` (now exported from `lib/api.ts`) runs before each reconnect; the fresh token is persisted via `authStore.setToken` and used to build the WS URL.
4. **Honest fallback UX.** After the 5‑attempt budget is spent, the dishonest "Reconnecting…" is replaced by a real **"Reload session"** CTA (`ReconnectNotice`) that resets the budget and forces a fresh connect; bumping `reconnectAttempt` also re‑runs the REST `/state` hydrate, so the learner resumes the in‑progress activity.

Recovery was already mostly built server‑side (Postgres‑persisted transcript/phase/queue + `resume_messages_stream` replay), so the work was purely in the connection layer — no new server state. The ALB `idle_timeout` bump (defense‑in‑depth) is intentionally **left to a separate infra PR** per the plan; the heartbeat is the portable real fix.

### Files changed
- `backend/app/modules/learning_session/router.py` — `ping`→`pong` branch in the WS receive loop (before rate‑limit + session pipeline).
- `backend/app/modules/learning_session/schemas.py` — documented `ping`/`pong` in the WS message‑type comments (the `type` field is a free `str`, so no functional schema change → no OpenAPI drift).
- `frontend/src/lib/api.ts` — `export` the existing `refreshAccessToken` (was private).
- `frontend/src/lib/ws-reconnect.ts` *(new)* — pure helpers: `HEARTBEAT_INTERVAL_MS` (25s), `MAX_RECONNECT_ATTEMPTS` (5), `nextReconnectDelayMs` (backoff+cap), `reconnectExhausted`, `shouldScheduleReconnect` (phase‑agnostic by construction), `buildLearningWsUrl`.
- `frontend/src/components/chat/ReconnectNotice.tsx` *(new)* — connection‑status bubble: upgrade prompt (4402) / "Reload session" CTA (exhausted) / calm "Reconnecting…".
- `frontend/src/app/task/chat/[sessionId]/page.tsx` — wired it together: heartbeat interval in the WS effect; async token‑refresh before reconnect; universal backoff reconnect effect (replaces the feedback‑only gate); `onclose`/`onerror` recover instead of returning early; `reloadSession`; ignore `pong` in `handleIncoming`; render `ReconnectNotice`. (Large diff is mostly re‑indentation from wrapping the connect logic in an `async` IIFE to `await` the refresh.)
- `backend/tests/integration/learning_session/test_ws_heartbeat.py` *(new)* — ping→pong via a real `TestClient` WS handshake (service stubbed; `LearningSession` JSONB can't compile on SQLite), proving a ping is ponged and never enters the session pipeline (a 2nd ping is a FIFO barrier confirming the real `user_message` was processed).
- `frontend/tests/unit/lib/ws-reconnect.test.ts` *(new)* — backoff sequence + cap, exhaustion threshold (= "after N failures"), phase‑independence of `shouldScheduleReconnect`, and `buildLearningWsUrl` token encoding (= "URL carries refreshed token").
- `frontend/tests/unit/components/ReconnectNotice.test.tsx` *(new)* — Reload CTA renders + fires when exhausted; calm "Reconnecting…" while recovering; upgrade (not reload) on 4402.

### How verified (proof)
- **Backend gates:** `ruff format` (410 files unchanged), `ruff check app tests` → **All checks passed**, `mypy app` → **Success: no issues in 270 files**. `export_openapi.py` → **no drift**.
- **Backend tests:** full `python -m pytest tests/unit tests/integration` → **exit 0**, no failures. WS‑focused subset (learning_session + premium_guard) = **62 passed**, including the new ping→pong test.
- **Frontend gates:** `npm run lint` → **0 errors** (88 pre‑existing warnings, none in changed files); `npx tsc --noEmit` → **exit 0**; `npm test` → **24 files / 122 tests pass** (incl. 10 ws‑reconnect + 4 ReconnectNotice); `npm run build` → **Compiled successfully**.
- **Deterministic proof maps to each Phase‑4 requirement:** ping→pong + no state mutation (backend integration test); backoff/cap/exhaustion + phase‑independent reconnect + refreshed‑token URL (ws‑reconnect unit tests); "Reload session" CTA renders + fires (ReconnectNotice test); resume replays the in‑progress activity (already covered by existing `test_resume_lands_on_pending_activity_without_replaying_feedback` / `test_resume_keeps_next_activity_when_attempt_is_pending`).
- **Not run:** a full live‑browser E2E (idle 2.5 min → heartbeat holds; force‑drop mid‑teaching → auto‑reconnect + state restore; token‑expiry → refresh‑on‑reconnect; blocked reconnect → Reload CTA). Same constraint as Phases 1–2: it needs a running backend + seeded curriculum DB + an authenticated live session + real LLM spend, which this environment isn't set up for. The unit/integration tests exercise every decision path with only the socket/LLM boundary stubbed. **Worth a manual demo‑day walkthrough** following the plan's "Verify E2E" steps.

### What the next session must know
- **All four OBVIOUS phases (1–4) are now implemented.** Remaining work is only the optional SUGGESTED fixes (S1–S5). The plan's "Verification summary" demo acceptance walk is the next sensible step before the interview.
- **The ALB `idle_timeout` 120→300s bump is NOT done** — deliberately deferred to a separate infra/Terraform PR (`infra/terraform/modules/alb/main.tf:29`). The heartbeat makes it non‑critical, but it's cheap defense‑in‑depth.
- Heartbeat cadence / attempt budget live in `frontend/src/lib/ws-reconnect.ts` (25s ping, 5 attempts, 10s max backoff) — tune there, no page edits needed.
- The WS `ping`/`pong` frames are not in `openapi.json` (WS isn't in the REST schema) — no contract step for this change.

### Deferred follow‑ups
- **ALB idle_timeout** (separate infra PR) as above.
- **S4 (longer / sliding session token):** the 20‑min access‑token TTL is aggressive for tutoring; Phase 4 heals on reconnect but a sliding refresh would remove mid‑session expiry as a factor (`config.py:99` + auth refresh path).
- **Long‑turn keepalive:** the heartbeat covers idle drops (the documented #1 cause). A single server turn exceeding 120s with no streamed bytes is still theoretically at risk; interleaving server keepalive frames during long buffered turns (or S1 true‑streaming) would close that gap. Current turns stay under the 90s frontend loading timeout, so low‑risk.
- **Carry‑over cruft (from Phases 2–3):** `llm_task_generator.py` `_agent_debug_log()` writes to `.cursor/debug-dfa507.log` and swallows exceptions — remove in a cleanup PR.
