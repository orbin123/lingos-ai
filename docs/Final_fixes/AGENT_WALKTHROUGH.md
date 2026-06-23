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
