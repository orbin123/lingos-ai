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

The chat layer never writes scoring tables directly except in the legacy
full-restart wipe (see follow-up #1); all evaluation/feedback/scorecard writes
are owned by `SessionService`.

## Coverage table

| Table / store | Create | Read | Update | Delete |
|---|---|---|---|---|
| **LearningSession** | `create_session` → `session_repo.create` | `get_by_session_id`, `get_by_daily_session_id`; REST `GET …/state`, `GET …/by-daily-session/{id}` | submit handlers (`messages`, `phase`, `evaluation`, `feedback`, `task_queue`, `current_task_index`); `restart_session`, `reset_activity`; `_maybe_refresh_file_persona` (topic/skill/level/instructions) | **None** — never deleted; restart resets in place (follow-up #2) |
| **DailySession** | `SessionService.start_session` | `get_by_session_id`, `get_in_progress`, `get_latest_for_day`, `get_with_attempts` | `status`/`completed_at` on submit/complete; **reopen** (→ `IN_PROGRESS`, `completed_at=None`) on `reset_activity` (if completed) and `restart_session`; stale-file session → `ABANDONED` | **None** — terminal states are `COMPLETED`/`ABANDONED`, rows are kept |
| **ActivityAttempt** | `_materialise_attempt` (during `start_session`) | `list_for_session`, `get`, `first_pending` | submit (`user_response`, `submitted_at`, `status`); `reset_to_pending` (clears response, → `PENDING`); `restart_session` bulk reset to `PENDING` | **None** — reset to `PENDING`, never deleted |
| **ActivityEvaluation** | `submit_activity` | `attempt.evaluation` relationship; aggregated in `complete_session` | **None** — replaced via delete+recreate on re-submit | `reset_activity` → `delete_for_attempt`; `restart_session` → bulk delete by attempt id |
| **ActivityFeedback** | `submit_activity` | `attempt.feedback` relationship; mentor-note aggregation | **None** — replaced via delete+recreate on re-submit | `reset_activity` → `delete_for_attempt`; `restart_session` → bulk delete by attempt id |
| **SessionScorecard** | `complete_session` | `get_scorecard`; chat `GET …/scorecard` (now 404s unless day is `COMPLETED`) | rebuilt (delete + recreate) when stored scores are stale or the day was reopened; `points_applied` / `mentor_note` set at build | `reset_activity` (when day was completed), `restart_session`, and `complete_session`'s rebuild path |
| **SkillPoints / SkillPointsLog** | `apply_session_scorecard` (first completion only) | `SkillPointsRepository.get_*`, `SkillPointsLogRepository.list_for_user` / `has_for_session` | `upsert_points` (cumulative) | **None** — `SkillPointsLog` is append-only; survives scorecard deletion and is the guard against double-award (see below) |
| **streak DailyActivity** | `StreakService.record_in_same_tx` (first evaluated submit per local calendar day) | `get_streak_data`, dashboard reads | streak counters updated in the same TX as the first daily submit | **None** — restart/retry do **not** touch streaks (decision below) |
| **RAG feedback-memory** (Pinecone vectors) | `_store_activity_memory_safe` (on submit), `_store_session_memory_safe` (on complete) — fire-and-forget | `retrieve_context_for_feedback` (mentor-note generation) | **None** | **None** from the session lifecycle (decision below) |

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
- **Full restart** (`restart_session`) wipes the chat envelope, resets every
  attempt to `PENDING`, deletes all evaluations/feedback, deletes the
  scorecard, and reopens the day.
- **Points are awarded at most once per `DailySession`.** `apply_session_scorecard`
  only writes on a first attempt with an un-applied scorecard, but the scorecard
  row is deleted on reopen, so that flag alone is not enough. `complete_session`
  now also consults `SkillPointsLog.has_for_session(session.id)` — the
  append-only log survives scorecard deletion — and treats prior application as
  `old_points_applied`. Re-completing after a retry rebuilds the scorecard with
  the **new** scores while skipping the points write. Covered by
  `tests/test_session_lifecycle.py::TestRestartRescoring`.

## Documented decisions

1. **RAG feedback-memory is NOT deleted on restart/retry.** Restart and
   per-activity reset leave historical feedback-memory vectors in place. This is
   intentional: the memory's purpose is to remember a learner's *recurring*
   weaknesses across attempts, so wiping it on every redo would defeat the
   feature. The trade-off is that a single day re-done several times can
   accumulate near-duplicate activity-feedback entries.
   *Possible follow-up:* dedupe by `(attempt_id, day_id)` or TTL-expire activity
   entries so a heavily-retried day doesn't skew retrieval.

2. **Streaks are NOT reverted on restart/retry.** A streak credit is earned for
   *showing up and completing an activity* on a calendar day; redoing work the
   same day neither re-awards (one `DailyActivity` per day) nor removes it.

## Follow-ups (not done here)

1. **Chat layer issues raw `delete(...)` against V2 tables in
   `restart_session`.** This breaks the "chat layer never writes scoring tables
   directly" rule. Consider extracting
   `SessionService.reset_session(session_id, user_id, *, scope="full")` and
   calling it from the chat layer, mirroring `reset_activity`. Deferred because
   the existing mock-based restart tests are tightly coupled to the inline
   implementation and `_make_v2_session_service` eagerly builds LLM agents
   (awkward in a pure-DB unit test); doing it cleanly means reworking those
   tests. Behaviour is correct today.
2. **`LearningSession` rows are never deleted.** Restart resets in place; there
   is no hard-delete/GC path for abandoned chat envelopes. Acceptable for now.
