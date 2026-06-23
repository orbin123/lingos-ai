# LingosAI — Final Fixes Plan (post GPT‑5 migration)

> **How to use this document.** This is the master plan for restoring the LingosAI core learner flow after the GPT‑5 migration. Each numbered phase is a self‑contained unit of work for one cloud session. Read the **Context** and **Chosen strategy** sections, then jump to your assigned phase. Sessions record progress in `AGENT_WALKTHROUGH.md` (sibling file). The four bug screenshots referenced below live in this same `docs/Final_fixes/` folder.

---

## Context — why this plan exists

On 2026‑06‑22 the backend migrated **every** LLM agent from GPT‑4o/4.1 to **GPT‑5** in one shot (commit `58f55a3`, PR #133). It was a config‑only model swap — no prompt, route, or DB change. GPT‑5 is a *reasoning* model and behaves differently enough that the **core learner flow** (teach → task → evaluate → feedback) regressed. Four bugs are now visible (screenshots in `docs/Final_fixes/`). A fifth issue — the WebSocket dropping in production — is unrelated to GPT‑5 and is a production‑resilience gap.

The interview demo depends on this exact happy path working end‑to‑end, so the goal is to **restore the known‑good behavior** with the new models, methodically, one fix per phase, each shipped through the normal branch → PR → green CI → squash‑merge → auto‑deploy pipeline.

### The single most important fact (it changes the whole approach)
**GPT‑5 silently ignores `temperature`.** It is a reasoning model; the OpenAI API 400s on a custom temperature, so `OpenAILLMClient` detects reasoning models and *drops* temperature, passing `reasoning_effort` instead (`backend/app/ai/llm/openai_client.py:65` `_is_reasoning_model`, and `:285` `_maybe_rebind_temperature` is a deliberate no‑op for them). That means the carefully‑tuned evaluator `0.2` / feedback `0.4` / task‑gen `0.7` temperatures are **already dead** on GPT‑5. *Lowering temperature cannot fix the eval/feedback accuracy* — the real lever is **which model each agent uses** (and `reasoning_effort`).

### Chosen strategy — hybrid per‑agent model routing (decided)
Instead of one model for every agent, route each agent to the model that fits its job. This restores the low‑temperature determinism we want for grading (temperature *works* on non‑reasoning models) and keeps GPT‑5 where reasoning genuinely helps:

| Agent | Model | Why | Knobs |
| --- | --- | --- | --- |
| **Teacher** (`app/ai/agents/teacher.py`) | `gpt-4.1-mini` (non‑reasoning) | Latency‑critical streaming chat; reasoning latency breaks the stream timeout | `temperature=0.4` (tone) |
| **Evaluator** (`app/ai/sessions/llm_evaluator.py`) | `gpt-4.1-mini` (non‑reasoning) | Determinism matters; mostly deterministic already | `temperature=0.2` (now effective) |
| **Feedback** (`app/ai/sessions/llm_feedback.py`) | `gpt-4.1-mini` (non‑reasoning) | Phrases a known result; wants low variance | `temperature=0.4` (now effective) |
| **Task generator** (`app/ai/sessions/llm_task_generator.py`) | `gpt-5` (reasoning) | Generation quality benefits from reasoning | `reasoning_effort=high` (up from medium) |
| **Quality judge** (`factory._shared_judge_client`) | `gpt-5` (reasoning) | Offline quality gate | `reasoning_effort=high` (unchanged) |

Model ids stay **env‑driven** (the migration's good idea): add `OPENAI_TASKGEN_MODEL` / `OPENAI_TASKGEN_REASONING_EFFORT`, and repoint `OPENAI_CHAT_MODEL` (the teacher/evaluator/feedback default) to `gpt-4.1-mini`. Everything is tunable from `.env` without code edits. `gpt-4.1-mini` is the recommended interactive model (fast, cheap, honors temperature, stronger than the pre‑migration `gpt-4o-mini`); bump evaluator/feedback to full `gpt-4.1` later if you want more accuracy.

> This routing is the **foundation Phases 1 and 2 build on.** Phase 1 wires the teacher's model; Phase 2 wires evaluator/feedback/task‑gen. They touch the same two files (`config.py`, `factory.py`) so run them **in order** (Phase 1 then Phase 2) to avoid merge churn.

---

## How this plan works

- **One fix = one phase.** Each phase is self‑contained: problem → root cause → fix → tests → verification → ship. A fresh cloud session can execute any single phase from this document alone.
- **Each phase ships independently:** branch off `main` → implement → run checks locally → PR → all required checks green → squash‑merge (which auto‑deploys). Branch names are given per phase.
- **Order matters only where noted.** Recommended order by demo impact: **Phase 0 → 1 → 4 → 2 → 3** (teaching and the WebSocket are the most visible failures; the empty‑rule box is cosmetic and quickest).
- **Two categories of fix:**
  - **OBVIOUS** (Phases 1–4) — the user reported these; they are confirmed and must be fixed.
  - **SUGGESTED** (S1–S5) — found while tracing the flow; pick what you want. None are required for the demo, but S3 (observability) and S5 (happy‑path smoke test) materially de‑risk it.
- **After each phase, the cloud session updates `docs/Final_fixes/AGENT_WALKTHROUGH.md`** with: what it changed (files + PR link), how it verified, what the next phase should know, and any follow‑ups. The next session reads the walkthrough first.

### Shipping checklist (applies to every phase — from `CLAUDE.md` + known CI gotchas)
- Branch off `main`; **never push to `main`** (merging auto‑deploys to prod).
- Backend: `uv run ruff format app tests` + `uv run ruff check app tests` + `uv run mypy app` + `uv run python -m pytest …` **before pushing** (use `python -m pytest`, not bare `uv run pytest` — a broken global pytest shadows it).
- If you change backend **routes**: regenerate the contract — `uv run python scripts/export_openapi.py` and commit `backend/openapi.json` (the `openapi-drift` check is blocking).
- Frontend: `npm run lint` + `npx tsc --noEmit` + `npm test` + `npm run build`.
- Coverage gate is `--cov-fail-under=73` and ratchets up — add tests for new code.
- **Sign off every commit** (`git commit -s`) with both trailers (the `DCO` check is blocking):
  ```
  Signed-off-by: Orbin Sunny <91816511+orbin123@users.noreply.github.com>
  Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
  ```
- Required checks include `docker-build` (Trivy CVE scan) and the GitHub‑App checks `DCO` + `Vercel`. A *conflicting* PR skips all Actions and wedges the merge — keep branches rebased on `main`.
- Migrations are **forward‑only** (a smoke‑failure rollback re‑points the service but does **not** revert migrations). None of these phases need a migration.

---

## Phase 0 — Make this plan visible to the cloud sessions (prerequisite, ~10 min)

**Problem.** `/docs` is git‑ignored (`.gitignore:17`). `docs/Final_fixes/` (this plan, the walkthrough, the four PNGs) lives only in the local working tree. Cloud sessions clone the **remote**, so they will **not** see any of it — the multi‑session workflow silently breaks before it starts.

**Fix (pick one):**
- **A — Track just this folder (recommended).** Add a negation to `.gitignore` so the Final_fixes folder is versioned while the rest of `/docs` stays ignored:
  ```gitignore
  /docs
  !/docs/Final_fixes/
  !/docs/Final_fixes/**
  ```
  Then commit the plan + walkthrough + the 4 images. Because **docs‑only PRs to `main` are blocked** (path‑filtered required checks never report → wedged merge), commit these files **bundled into Phase 1's PR** (Phase 1 changes code anyway), or push them on a shared base branch (below).
- **B — Shared base branch.** Create `final-fixes` off `main`, commit the docs there, and branch every phase off `final-fixes` (PR each phase back to `main`). The docs travel to every cloud session via the base branch without ever needing to merge to `main`.
- **C — No repo changes.** Keep the docs local and, in each cloud session, paste the phase text and attach the relevant screenshot manually. Simplest, but you re‑paste every time.

**Recommendation:** **A**, bundled into Phase 1's PR. Verify with `git check-ignore -v docs/Final_fixes/FINAL_FIXES_PLAN.md` returning nothing after the change.

---

# OBVIOUS FIXES

## Phase 1 — Teaching agent: restore real, step‑by‑step teaching

**Screenshot:** `teaching_agent_no_teaching.png` — the tutor says *"…I will guide you through a quick concept check, then we will do a short practice. Say 'ready' when you want to begin."*, the learner types **ready**, and it jumps straight to *"Great! Here is activity 1 of 4."* — **zero teaching.**

**What's actually happening (root cause — confirmed).** The step‑by‑step teaching engine *already exists and is intact*: scripted multi‑step plans, per‑turn step cursor, acknowledge‑then‑probe, off‑topic/non‑English redirection, and readiness detection are all in the teacher prompt and service (`teacher.py:165` the system prompt; `:387` `_current_step_index`; `service.py:2936` turn‑cursor logic; readiness patterns in `service.py`). **The learner never reaches it** because turn 1 hits a fallback:

1. `teacher.py:stream_teaching_turn` does **not** stream incrementally — it **buffers the entire LLM response** (`buffered += chunk`, `:980`) and yields the finished message as a *single* chunk at the very end (after an optional **second** retry LLM call, `:997`).
2. `service.py:_stream_teaching_turn` wraps that generator in `_timed_chunks` with **`_TEACHING_STREAM_FIRST_CHUNK_TIMEOUT_S = 8.0`** (`service.py:334`, used at `:2978`). So the service waits **8 seconds for the first chunk** — but the first chunk can't arrive until GPT‑5 has finished *thinking + generating (+ retrying)*.
3. GPT‑5 at `reasoning_effort=medium` routinely needs **well over 8 s** before any text exists. `_timed_chunks` times out, `break`s with an empty buffer (`service.py:2871`), and the service emits its **hardcoded outer fallback** — the exact "Say 'ready' when you want to begin" string (`service.py:2994‑3008`). GPT‑4o‑mini streamed first tokens in ~1–2 s, so the 8 s budget used to be fine.

**The fix (two required + one safety):**
1. **Route the teacher to a fast non‑reasoning model** (foundational decision). Repoint `OPENAI_CHAT_MODEL` → `gpt-4.1-mini` in `app/core/config.py` and `.env.example` (teacher reads the shared singleton `get_default_llm_client()`, which uses `OPENAI_CHAT_MODEL`). First tokens return in ~1 s; temperature `0.4` (`teacher.py:30`) now actually applies. *(Evaluator/feedback ride the same default — that's intended and handled in Phase 2.)*
2. **Raise the teaching first‑chunk timeout** to absorb a full buffered turn + a possible retry on the fast model: `_TEACHING_STREAM_FIRST_CHUNK_TIMEOUT_S = 30.0` (and apply the same to the follow‑up answer constants at `service.py:336‑337`). This is defense‑in‑depth so a momentary slow response degrades gracefully instead of silently falling back.
3. **Surface the silent fallback (safety).** The fallback path logs `teaching_turn_streaming_failed` / `teacher.fallback_used`, but nothing alerts. At minimum, keep these logs; ideally fold into S3.

**Why this restores the *whole* experience.** Once the teacher LLM actually responds on turn 1, the existing multi‑turn machinery takes over: it follows the authored steps one at a time, acknowledges the learner's answer, asks one probing question per turn, redirects off‑topic/non‑English replies (prompt §OFF‑TOPIC), and only offers "Ready to try the practice task?" at the end. No new teaching logic is needed — just stop short‑circuiting turn 1.

**Verify the demo days have teaching content.** Confirm the A1 Day‑2 lesson (and the days you'll demo) carry a real scripted plan with several steps in `backend/app/modules/curriculum/source_L_A1A2.py` (the `__scripted_plan` sentinel). If a day has an empty/1‑step plan, the teacher correctly free‑forms but will feel thin — fix the curriculum content, not the agent.

**Tests.**
- Unit (`backend/tests/unit/...teacher`): existing teacher tests already cover the contract; add one asserting that when the LLM returns a valid turn, the **service** yields it (not the outer fallback) — i.e. guard against the 8 s short‑circuit by injecting a fast fake stream and asserting `content != fallback`.
- Unit: assert `_TEACHING_STREAM_FIRST_CHUNK_TIMEOUT_S >= 30`.
- Integration (`backend/tests/integration/...learning_session`): start a session with a stubbed teacher that returns a real multi‑step plan; drive `ready`/non‑ready messages; assert the transcript shows ≥2 distinct teaching turns *before* the first activity and that an off‑topic message gets redirected rather than advancing.

**Verify E2E.** `uv run uvicorn app.main:app --reload` + `npm run dev`; open an A1 session; confirm the tutor teaches across multiple turns, redirects an off‑topic reply ("let's talk about football"), and only starts the activity after a genuine readiness exchange.

**Branch & ship.** `fix/teaching-agent-fast-model-and-timeout`. No route/migration change → no OpenAPI/Alembic step. Run ruff+mypy+pytest; PR; green; squash‑merge. *(Bundle the Phase 0 docs here if you chose 0‑A.)*

---

## Phase 2 — Evaluation & feedback accuracy on rule‑based tasks

**Screenshot:** `tasks_eval_feedback_distorted.png` — an **error‑spotting** past‑tense task where the generated sentences contain *off‑topic and/or multiple* mistakes, the evaluation marks some wrong answers right (2nd, 5th), and the feedback lists **3** mistakes when only **2** exist.

**What's actually happening (root cause — confirmed).** Grading here is **deterministic, not LLM‑judged**, and that code is **unchanged** by the migration — so the regression comes from the **only** thing that changed: the model that *generates the task's ground truth*.

- **Error‑spotting (`READ_ERROR_SPOT`) is graded by exact token matching** (`llm_evaluator.py` deterministic set; selected `token_id`s vs the tagged `error.token_id`). The generator enforces **exactly one** tagged error per sentence (`llm_task_generator.py:346` `validate_single_error_token`) — but it only *logs*, never gates, when the **passage quality** is off (`:369` `normalize_quality_targets`). GPT‑5 at medium effort is generating sentences that contain **extra, untagged errors** and **errors unrelated to the lesson's grammar focus**. The deterministic grader faithfully scores against the single tagged token, so to a human it looks like "the 2nd was wrong but marked right" — the *ground truth itself* no longer matches what the learner sees. **This is a generation‑quality problem, not an evaluator bug.**
- **Feedback over‑counts because error_correction has no answer key fed to it.** For `error_spotting` and `fill_in_blanks`, feedback is constrained to **deterministic confirmed mistakes** (`llm_feedback.py:41` `_DETERMINISTIC_WIDGET_KEYS`; `:126‑134`), and the feedback prompt has a hard rule to cite *exactly* those. But **`error_correction` is in `_OPEN_ENDED_WIDGET_KEYS`** (`:57‑64`), so **no** `confirmed_mistakes` are computed — the LLM **re‑derives** mistakes itself and can invent a third one. (Error‑correction grading *is* deterministic via exact‑match `_normalize_sentence` in `app/ai/agents/evaluator.py:893`, so the answer key needed to constrain feedback already exists — it just isn't passed.)

**The fix (model + one targeted code change; deliberately *not* more prompt rules — per the user's guidance).**
1. **Honor the low‑temperature intent by moving grading agents to a temperature‑respecting model.** In `factory.py`, evaluator + feedback already share `_shared_default_client()` → now `gpt-4.1-mini` (from Phase 1's `OPENAI_CHAT_MODEL`). Their `temperature=0.2` / `0.4` (`llm_evaluator.py` / `llm_feedback.py:98`) **finally take effect**, giving the near‑deterministic behavior we want.
2. **Keep task generation on GPT‑5 but raise effort to `high`.** Add `OPENAI_TASKGEN_MODEL=gpt-5` + `OPENAI_TASKGEN_REASONING_EFFORT=high` to `config.py`/`.env.example`; in `factory.build_default_agents`, build a dedicated task‑gen client (`OpenAILLMClient(model=…TASKGEN_MODEL, reasoning_effort=…TASKGEN_REASONING_EFFORT, usage_sink=record_usage)`) and wrap **only** the task generator with it (`factory.py:97`), leaving evaluator/feedback on the fast default. Higher effort produces cleaner, single‑error, on‑topic sentences — the *temperature‑equivalent* lever for a reasoning model.
3. **Make error_correction feedback deterministic.** Move `error_correction` out of the open‑ended path: compute `confirmed_mistakes` from the task's `sample_answer` per item (mirror `compute_wrong_items` used for fill‑in‑blanks) and pass them through, so feedback cites **exactly** the real mistakes — no invented third item. This is the one code change that directly kills the "3 vs 2" bug; reuse the existing `compute_wrong_items` / normalization helpers in `app/ai/sessions/prompts.py` rather than writing new logic.

> Explicitly **not** doing: piling more constraints into the generation prompt (the user flagged this would make it "loose"). The levers here are model/effort + feeding the existing answer key to feedback. If generation quality still misses after `high` effort, S2 (a pre‑delivery judge gate) is the belt‑and‑suspenders option.

**Tests.**
- Unit (`llm_feedback`): error_correction with a known wrong item asserts feedback returns **exactly** the confirmed mistakes (no extras); add a regression for the "3 vs 2" shape.
- Unit (`factory`): assert the task‑generator client uses `OPENAI_TASKGEN_MODEL` + effort `high`, while evaluator/feedback use the default model.
- Unit (`openai_client`): keep/extend the existing reasoning‑model test proving temperature is honored on `gpt-4.1*` and dropped on `gpt-5*`.

**Verify E2E.** Run an error‑spotting and an error‑correction activity; confirm the generated sentences carry exactly one on‑topic error each, the score matches a hand‑grade, and feedback lists only the real mistakes.

**Branch & ship.** `fix/eval-feedback-model-routing-and-determinism`. Touches `config.py`, `factory.py`, `llm_feedback.py`, `.env.example` — **no routes/migration**. Note the **new env vars** in the PR template's new‑env‑var checklist (and set them in the `production` GitHub Environment, or rely on the baked defaults).

---

## Phase 3 — Empty "Correction rule" box

**Screenshot:** `correction_rule_empty.png` — the error‑correction task renders an orange **CORRECTION RULE** card with **no text** inside.

**What's actually happening (root cause — confirmed).** The card binds to `task.grammarRule`, which is empty. Two reasons: (a) the error‑correction **LLM output schema has no rule field** — `ErrorCorrectionTask` (`llm_task_generator.py:272`) lacks the `grammar_rule_to_practice` field that other archetypes have (`:258`), so the projection's fallbacks (`projection.py:163‑165`) find nothing and default to `""` (`contracts/base.py:54` `grammar_rule=""`); (b) the widgets render `RuleCallout` **unconditionally** (`ErrorCorrectionTaskWidget.tsx:47,70`, plus SentenceTransform/SpeakRoleplay/ReadContextMcq/WriteParagraph/… all do `<RuleCallout label=…>{task.grammarRule}</RuleCallout>`), so an empty value still draws the box. The generic path already guards correctly (`runtimeMapping.tsx:144` does `grammarRule && <RuleCallout/>`) — the per‑widget callers don't.

**The fix (one‑line, fixes every widget; this is the "just remove it" the user asked for, done safely).**
1. **Hide the card whenever it's empty** by guarding inside `RuleCallout` itself (in `TaskWidgetFrame.tsx`): return `null` when its children/content are empty or whitespace. This removes the empty box **everywhere at once** without deleting the feature for tasks that *do* carry a rule — no need to edit each widget.
2. **(Optional, richer) Populate it.** Add `grammar_rule_to_practice: str | None = None` to `ErrorCorrectionTask` (`llm_task_generator.py:272`) so GPT‑5 fills a one‑line rule; the projection already maps it (`projection.py:163‑165`). Do this only if you want the rule shown; otherwise step 1 alone satisfies the bug.

**Tests.**
- Frontend (Vitest): `RuleCallout` renders `null` for `""`/whitespace and renders normally for real content; an `ErrorCorrectionTaskWidget` with empty `grammarRule` shows no rule card.
- Backend (only if doing the optional step): a generation test asserting the new field round‑trips into the payload.

**Verify E2E.** Open an error‑correction task: no empty orange card. If you did the optional step, confirm a real one‑line rule appears.

**Branch & ship.** `fix/empty-correction-rule-card`. Frontend‑only if you skip the optional backend bit (then no OpenAPI step). Smallest, lowest‑risk phase — good quick win.

---

## Phase 4 — WebSocket resilience: kill "Connection closed" for good

**Screenshot:** `connection_closed.png` — mid‑session the chat shows *"Connection closed. Reconnecting…"* and the learner is **stuck** (can't submit, nothing recovers). Not a GPT‑5 issue — a production‑resilience gap that surfaces in long/live sessions.

**What's actually happening (root cause — confirmed, three compounding causes).**
1. **The ALB kills idle sockets after 120 s.** `infra/terraform/modules/alb/main.tf` sets `idle_timeout = 120`. There is **no app‑level heartbeat** on either side, so any 2‑minute lull (e.g. the learner reading, or a long LLM turn) drops the socket.
2. **The frontend only auto‑reconnects during feedback.** The reconnect effect (`frontend/src/app/task/chat/[sessionId]/page.tsx:1523‑1540`) bails unless `phase === "submitted"` or `loadingType === "feedback_loading"`. During **teaching** or **practice**, the socket drops, the UI prints "Connection closed. Reconnecting…" (`:2532`) — **but no reconnect ever fires.** The message is a lie; the user is stranded.
3. **The access token the socket carries expires in 20 minutes.** Login mints tokens with `ACCESS_TOKEN_TTL_MINUTES = 20` (`config.py:99`; `auth/routes.py:164/407`). The JWT is passed as a `?token=` query param and validated **once** at the handshake (`router.py:415`); it's never refreshed. The HTTP axios refresh interceptor (`lib/api.ts`) does **not** apply to WebSockets. So a session >20 min that tries to reconnect presents a **stale token** → server closes `4401` → permanently stuck.

**Good news — recovery is already mostly built.** The backend **persists everything** to Postgres (`learning_session/models.py:20‑68`: `messages`, `phase`, `task_queue`, `understanding_confirmed`, `evaluation`, `feedback`) and already **replays** it: `resume_messages_stream` (`service.py:1272‑1361`) rehydrates the transcript + current activity on reconnect, and `GET /learning/sessions/{id}/state` (`router.py:145‑174`) returns a full snapshot for a cold load. **So the instinct (persist + resume) is correct, and the DB — not a cookie — is already the source of truth.** We don't need cookies; we need to keep the socket alive, always reconnect, and present a fresh token. This is the better architecture (server‑authoritative, survives browser/device changes).

**The fix (layered; frontend stays seamless, work is in the connection layer):**
1. **App‑level heartbeat (prevents most drops).** Client sends a `ping` every ~25 s (under the 120 s ALB idle); server replies `pong` (and/or sends periodic keepalive frames during long teacher turns). Backend: handle a `ping` message type in the receive loop (`router.py:445‑482`) without disturbing session logic. Frontend: a `setInterval` tied to the socket lifecycle. This alone stops the idle‑timeout drops.
2. **Universal auto‑reconnect with backoff (recovers any drop).** Remove the phase gate at `page.tsx:1529` so reconnection runs in **every** phase (teaching, practice, submitted) with exponential backoff + a cap. On reconnect the backend's `resume_messages_stream` already rehydrates state — the learner continues where they were.
3. **Refresh the token before reconnecting (fixes the 20‑min death).** Before opening the new socket, call the existing `refreshAccessToken()` (`lib/api.ts`) and build the WS URL with the fresh JWT. A reconnect after token expiry now self‑heals instead of `4401`‑closing.
4. **Honest fallback UX (the "ask to reload" requirement).** After N failed reconnects (e.g. 5), stop pretending — replace "Reconnecting…" with a clear **"Reload session"** action that re‑hydrates via `GET …/state` and reopens the socket. The learner never sees an infinite dead "Reconnecting…".
5. **Defense‑in‑depth (infra).** Optionally raise the ALB `idle_timeout` (e.g. 120 → 300 s) in `alb/main.tf`. Secondary to the heartbeat (which is portable and the real fix); a Terraform change deploys via the infra path, not this app PR.

> **Token lifetime note:** the 20‑min TTL is aggressive for a tutoring session. Fix #3 makes reconnects survive it, but consider S4 (a longer‑lived or sliding session token) so mid‑session expiry stops being a factor at all.

**Tests.**
- Backend unit (`learning_session/router` or service): a `ping` message yields a `pong`/keepalive and does not mutate session state; `resume_messages_stream` after a simulated drop replays the in‑progress activity (not just the intro).
- Frontend (Vitest): reconnect logic fires in `teaching`/`practice` phases (not only feedback); after N failures the "Reload session" CTA renders; the reconnect URL carries a refreshed token.

**Verify E2E.** Start a session; **idle 2.5 min** → confirm the heartbeat keeps it open (no "Connection closed"). Then force‑drop the socket (kill the backend briefly, or close it via devtools) mid‑teaching → confirm it auto‑reconnects and the transcript/activity restore. Let a token expire (or shorten TTL locally) → confirm reconnect refreshes it. Block reconnection entirely → confirm the "Reload session" CTA appears and recovers.

**Branch & ship.** `fix/websocket-resilience-heartbeat-reconnect`. Frontend + a small backend handler (ping/pong). If you add the ping message to the WS contract, check whether `openapi.json` is affected (WS frames usually aren't in the REST schema — only regenerate if a REST route changed). The ALB change, if you do it, is a **separate** infra PR.

---

# SUGGESTED FIXES (additions — pick what you want)

> None are required for the demo. **S3 and S5 are the highest‑value de‑riskers** — they make silent regressions loud and lock in the happy path so this class of bug can't recur unnoticed.

### S1 — Make the teacher truly stream (perceived latency)
Today `stream_teaching_turn` buffers the whole turn then yields once (`teacher.py:980`), so even on the fast model the learner stares at nothing until the full turn is ready. Refactor to **stream tokens through** while still validating/repairing at sentence boundaries (or stream first, validate the completed buffer, and only correct on violation). Makes the chat feel alive and renders the first‑chunk timeout irrelevant. *Branch:* `feat/teacher-true-streaming`.

### S2 — Pre‑delivery quality gate for error tasks (belt‑and‑suspenders for grading)
If raising task‑gen effort to `high` still lets through multi‑error/off‑topic sentences, add a **validation pass** using the existing judge infra (`factory._shared_judge_client`, gpt‑5 high): before delivering an error‑spotting/error‑correction task, ask the judge "exactly one error per sentence, tagged correctly, on‑topic for {focus}? else regenerate." This is a **structural gate**, not extra generation‑prompt rules (which the user vetoed) — it can't make generation looser, only reject bad tasks. Costs one extra call + latency, so gate it behind a flag. *Branch:* `feat/error-task-quality-gate`.

### S3 — Surface silent LLM fallbacks (observability) — **recommended**
The teacher fallback, stream timeouts, and structured‑validation failures all log quietly today (`teacher.fallback_used`, `teaching_turn_streaming_failed`, `llm_structured_validation_failed`). Add a metric/Sentry breadcrumb (Sentry is already wired) on each, so a regression is **visible** before a learner (or interviewer) hits it. Cheap, high value the night before a demo. *Branch:* `feat/llm-fallback-observability`.

### S4 — Longer / sliding session token
Raise the learner session token TTL or add a **sliding refresh** so a 30–60 min session never carries an expired token. Complements Phase 4 #3 (which heals on reconnect) by removing the cause. Touches `config.py:99` + the auth refresh path; mind the security trade‑off of longer‑lived tokens. *Branch:* `feat/session-token-lifetime`.

### S5 — One end‑to‑end happy‑path smoke test — **recommended**
There is no single test that drives **teach → task → evaluate → feedback → scorecard** with stubbed LLMs. Add one integration test (backend) and/or a Playwright/Vitest flow (frontend) asserting: multi‑turn teaching occurs, an activity is graded correctly against a known key, and feedback cites only real mistakes. This test would have caught **all four** obvious bugs. Raises coverage toward the ratchet too. *Branch:* `test/core-flow-happy-path-smoke`.

---

## Verification summary (the demo acceptance test)

After Phases 1–4, walk the A1 demo session once and confirm:
1. The tutor **teaches across multiple turns**, probes with one question per turn, and **redirects** an off‑topic reply — before any activity.
2. An **error‑spotting** task has exactly one on‑topic error per sentence; the score matches a hand‑grade.
3. An **error‑correction** task shows **no empty rule card**, and its feedback lists **only** the real mistakes.
4. The session **survives a 2.5‑min idle and a forced socket drop** mid‑teaching, auto‑reconnecting and restoring state; a blocked reconnect shows a working **"Reload session"** CTA.

---

## Common cloud‑session kickoff prompt (paste per session; set PHASE)

> Replace `<N>` with the phase number (or `S<k>` for a suggested fix). Attach the matching screenshot from `docs/Final_fixes/` if your cloud session can't read the repo's images.

```
You are working on the LingosAI repo. We migrated all LLM agents from GPT‑4o/4.1 to
GPT‑5 (PR #133) and it regressed the core learner flow (teach → task → evaluate →
feedback) plus exposed a production WebSocket drop. We are fixing these methodically,
one phase per session.

READ FIRST, in order:
1. docs/Final_fixes/FINAL_FIXES_PLAN.md — the full plan. Read the "Context",
   "Chosen strategy (hybrid per‑agent model routing)", and "How this plan works"
   sections, then the phase you're assigned.
2. docs/Final_fixes/AGENT_WALKTHROUGH.md — what previous sessions already did and
   any notes for you. (If it's empty, you're early in the sequence.)
3. The screenshot(s) referenced by your phase in docs/Final_fixes/ — they show the
   exact bug.

KEY FACT you must not forget: GPT‑5 ignores `temperature` (it's a reasoning model;
the client drops temperature and uses reasoning_effort). The fix strategy is per‑agent
MODEL ROUTING, not temperature changes. See the plan's "Chosen strategy" table.

YOUR TASK THIS SESSION: execute **Phase <N>** from FINAL_FIXES_PLAN.md, end to end:
- Implement exactly that phase's fix (don't drift into other phases).
- Add/adjust the tests the phase lists.
- Run the local gates before pushing: backend `uv run ruff format app tests`,
  `uv run ruff check app tests`, `uv run mypy app`, `uv run python -m pytest …`
  (use `python -m pytest`, not bare `uv run pytest`); frontend `npm run lint`,
  `npx tsc --noEmit`, `npm test`, `npm run build`. If you changed backend routes,
  run `uv run python scripts/export_openapi.py` and commit backend/openapi.json.
- Branch off main with the phase's branch name. NEVER push to main (merge auto‑deploys
  to prod). Open a PR, fill the PR template, get all required checks green.
- Sign off every commit (`git commit -s`) with BOTH trailers:
    Signed-off-by: Orbin Sunny <91816511+orbin123@users.noreply.github.com>
    Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
- Verify the fix end‑to‑end exactly as the phase's "Verify E2E" section describes,
  and include the evidence in your final message.

WHEN DONE: append a section to docs/Final_fixes/AGENT_WALKTHROUGH.md with: phase number
+ title, files changed, the PR link, how you verified (with proof), anything the next
session must know, and any follow‑ups you deferred. Then stop — do not start the next
phase.
```

---

## Files this plan touches (quick map)

- **Models/strategy:** `backend/app/core/config.py`, `backend/.env.example`, `backend/app/ai/sessions/factory.py`, `backend/app/ai/llm/openai_client.py`
- **Phase 1 (teaching):** `backend/app/modules/learning_session/service.py` (timeouts `:334‑337`, `_stream_teaching_turn` `:2881‑3024`), `backend/app/ai/agents/teacher.py`, curriculum `source_L_A1A2.py`
- **Phase 2 (eval/feedback):** `backend/app/ai/sessions/llm_feedback.py` (`:41‑64`, `:124‑148`), `backend/app/ai/sessions/llm_task_generator.py` (`:272`, `:346`, `:369`), `backend/app/ai/sessions/prompts.py` (reuse `compute_wrong_items`), `factory.py`, `config.py`
- **Phase 3 (rule card):** `frontend/src/components/chat/tasks/task_widgets/TaskWidgetFrame.tsx` (`RuleCallout`), optionally `llm_task_generator.py:272`
- **Phase 4 (websocket):** `frontend/src/app/task/chat/[sessionId]/page.tsx` (`:1523‑1540`, `:1927‑1992`, `:2532`), `backend/app/modules/learning_session/router.py` (`:408‑486`), `frontend/src/lib/api.ts` (token refresh), optionally `infra/terraform/modules/alb/main.tf`
