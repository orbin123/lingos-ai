# Session CRUD audit

Coverage of Create / Read / Update / Delete across every table (and the RAG
vector store) touched by the chat-session lifecycle — start, teaching, task
submit, evaluation/feedback, day completion, **and** the new resume / restart /
per-activity retry flows on `feat/chat-session-crud-logic`.

Two session concepts (see `CLAUDE.md`):

- **`LearningSession`** — the chat/conversation envelope (Postgres JSONB:
  `messages`, `task_queue`, `evaluation`, `feedback`, `pre_generated_tasks`).
- **`DailySession`** + children (`ActivityAttempt`, `ActivityEvaluation`,
  `ActivityFeedback`, `SessionScorecard`) — the V2 engine that owns task
  content, scoring and the points write-back.

The chat layer never writes scoring tables directly; all
evaluation/feedback/scorecard writes — including full restart — are owned by
`SessionService` (`reset_activity`, `reset_session_full`).

## Coverage table

| Table / store | Create | Read | Update | Delete |
|---|---|---|---|---|
| **LearningSession** | `create_session` → `session_repo.create` | `get_by_session_id`, `get_by_daily_session_id`; REST `GET …/state`, `GET …/by-daily-session/{id}` | submit handlers (`messages`, `phase`, `evaluation`, `feedback`, `task_queue`, `current_task_index`); `restart_session`, `reset_activity`; `_maybe_refresh_file_persona` (topic/skill/level/instructions) | **None** — never deleted; restart resets in place (follow-up #2) |
| **DailySession** | `SessionService.start_session` | `get_by_session_id`, `get_in_progress`, `get_latest_for_day`, `get_with_attempts` | `status`/`completed_at` on submit/complete; **reopen** (→ `IN_PROGRESS`, `completed_at=None`) on `reset_activity` (if completed) and `restart_session`; stale-file session → `ABANDONED` | **None** — terminal states are `COMPLETED`/`ABANDONED`, rows are kept |
| **ActivityAttempt** | `_materialise_attempt` (during `start_session`) | `list_for_session`, `get`, `first_pending` | submit (`user_response`, `submitted_at`, `status`); `reset_to_pending` (clears response, → `PENDING`) via both `reset_activity` and `reset_session_full` | **None** — reset to `PENDING`, never deleted |
| **ActivityEvaluation** | `submit_activity` | `attempt.evaluation` relationship; aggregated in `complete_session` | **None** — replaced via delete+recreate on re-submit | `reset_activity` / `reset_session_full` → `delete_for_attempt` |
| **ActivityFeedback** | `submit_activity` | `attempt.feedback` relationship; mentor-note aggregation | **None** — replaced via delete+recreate on re-submit | `reset_activity` / `reset_session_full` → `delete_for_attempt` |
| **SessionScorecard** | `complete_session` | `get_scorecard`; chat `GET …/scorecard` (now 404s unless day is `COMPLETED`) | rebuilt (delete + recreate) when stored scores are stale or the day was reopened; `points_applied` / `mentor_note` set at build | `reset_activity` (when day was completed), `reset_session_full`, and `complete_session`'s rebuild path |
| **SkillPoints / SkillPointsLog** | `apply_session_scorecard` (first completion only) | `SkillPointsRepository.get_*`, `SkillPointsLogRepository.list_for_user` / `has_for_session` | `upsert_points` (cumulative) | **None** — `SkillPointsLog` is append-only; survives scorecard deletion and is the guard against double-award (see below) |
| **streak DailyActivity** | `StreakService.record_in_same_tx` (first evaluated submit per local calendar day) | `get_streak_data`, dashboard reads | streak counters updated in the same TX as the first daily submit | **None** — restart/retry do **not** touch streaks (decision below) |
| **RAG feedback-memory** (Pinecone vectors + Postgres mirror) | `_store_activity_memory_safe`, `_store_session_memory_safe` (post-completion worker) — fire-and-forget | `retrieve_context_for_feedback` (mentor-note generation) | **None** | `reset_activity` / `reset_session_full` purge the reset attempt vector(s) + session-summary vector via a **background** worker (own DB session) — best-effort, non-blocking (decision below) |

## Behavioural guarantees after this change

- **Resume** (`resume_messages_stream`) lands on the first pending V2 attempt and
  never re-emits completed activities' evaluation/feedback widgets. The
  `GET …/state` snapshot now also returns `completed_activities` (sequence,
  label, widget, `raw_score`) so the UI renders compact read-only rows with a
  per-activity Retry button instead of replaying the full widgets.
- **Per-activity retry** (`reset_activity`) clears that attempt's
  evaluation/feedback, flips it to `PENDING`, and — if the day was
  `COMPLETED` — reopens the day and drops the now-stale scorecard. Other
  activities are untouched.
- **Full restart** (`restart_session`) wipes the chat envelope, then delegates
  the V2 reset to `SessionService.reset_session_full`: every attempt → `PENDING`,
  all evaluations/feedback deleted, scorecard dropped, day reopened. The V2 reset
  commits immediately; stale RAG vectors are purged in the background.
- **Points are awarded at most once per `DailySession`.** `apply_session_scorecard`
  only writes on a first attempt with an un-applied scorecard, but the scorecard
  row is deleted on reopen, so that flag alone is not enough. `complete_session`
  now also consults `SkillPointsLog.has_for_session(session.id)` — the
  append-only log survives scorecard deletion — and treats prior application as
  `old_points_applied`. Re-completing after a retry rebuilds the scorecard with
  the **new** scores while skipping the points write. Covered by
  `tests/test_session_lifecycle.py::TestRestartRescoring`.

## Documented decisions

1. **RAG vectors for the reset attempt(s) are purged in the background.**
   Per-activity reset and full restart drop the now-stale activity-feedback
   vector(s) for the reset attempts (and the session-summary vector when the day
   is reopened) so Pinecone and its Postgres mirror stay in sync with the V2
   reset. This runs **fire-and-forget on its own DB session**
   (`_run_rag_delete_worker`) so it never blocks the reset/restart commit, and is
   best-effort (failures logged under `rag.delete.*`, never raised). Historical
   vectors from *other* days/sessions are untouched, so the memory still surfaces
   a learner's *recurring* weaknesses across days. The previous policy left the
   stale vector in place; deleting it before re-completion re-indexes avoids
   accumulating near-duplicate entries for a heavily-retried day.

2. **Streaks are NOT reverted on restart/retry.** A streak credit is earned for
   *showing up and completing an activity* on a calendar day; redoing work the
   same day neither re-awards (one `DailyActivity` per day) nor removes it.

## Follow-ups

1. **DONE — Chat layer no longer issues raw `delete(...)` against V2 tables.**
   `restart_session` now delegates to `SessionService.reset_session_full`,
   mirroring `reset_activity`, so all scoring-table writes are owned by
   `SessionService`. The V2 reset commits immediately and schedules background
   RAG cleanup.
2. **`LearningSession` rows are never deleted.** Restart resets in place; there
   is no hard-delete/GC path for abandoned chat envelopes. Acceptable for now.
