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
