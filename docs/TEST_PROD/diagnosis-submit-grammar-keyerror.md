# `KeyError: 'grammar'` on `POST /diagnosis/submit`

**Date:** 2026-06-19 · **Severity:** High (diagnosis flow fully broken in prod) · **Status:** Fixed, merged, deployed to production

## Problem

A learner submitting the diagnosis multi-form saw a "network error". Sentry
captured `KeyError: 'grammar'` on `/diagnosis/submit` (Jun 19, 9:24:20 PM IST).
The endpoint returned a 500, which the frontend surfaces as a network error.

## Root cause

The `skills` master table was **empty in production** — the 7 canonical
sub-skill rows were never seeded.

`POST /diagnosis/submit` → `DiagnosisService.run_diagnosis` computes the 7 skill
scores and writes them to `SkillPoints`, mapping skill name → id via
`SkillRepository.name_to_id_map()`:

```python
# backend/app/modules/diagnosis/service.py:136-142
name_to_id = self.skills.name_to_id_map()      # {} when skills table is empty
for skill_name, score in skill_scores.items(): # grammar is the first key
    self.points.upsert_points(..., skill_id=name_to_id[skill_name], ...)  # KeyError: 'grammar'
```

`compute_skill_scores` always returns the 7 canonical keys (`app.scoring.SUB_SKILLS`).
With no rows in `skills`, `name_to_id_map()` returns `{}`, so `name_to_id['grammar']`
(the first key iterated) raises `KeyError: 'grammar'`.

**Why the table was empty:**
- The squashed initial migration *creates* `skills` but inserts no rows.
- `f1a2b3c4d567_skill_display_labels` only runs `UPDATE ... WHERE name = :name` — a no-op on an empty table.
- `scripts/seed_curriculum.py` seeded **archetypes + curriculum only**, not skills.
- No code inserted `Skill` rows outside tests.

**Why CI never caught it:** the test DB is built with `Base.metadata.create_all()`
on in-memory SQLite (`tests/fixtures/db.py`) and does **not** run migrations.
Every test that needs skills seeds them itself (factory `tests/factories/progress.py`,
inline `Skill(...)` in `test_diagnosis_seeds_points_only.py:86`), so the missing
production seed was invisible.

This was systemic, not diagnosis-specific: any first writer to `SkillPoints`
(e.g. `sessions/scoring_writer.py`) would have failed the same way. Diagnosis was
just the first place a real prod learner hit it.

## Investigation process

1. Located the crash site from the Sentry stack: `diagnosis/service.py:138`,
   `name_to_id[skill_name]`.
2. Traced `name_to_id_map()` → `SkillRepository.get_all()` → `skills` table. The
   `KeyError` proves `grammar` was absent from the table.
3. `grep -rn "Skill(name" app scripts` → no production inserts; only tests seed skills.
4. Reviewed all migrations referencing `skills`: table created but never seeded;
   `display_label` migration only UPDATEs.
5. Confirmed `seed_curriculum.py` seeds archetypes/curriculum, not skills.
6. Confirmed the test harness uses `metadata.create_all()` (no migrations), so the
   gap can't be caught by the existing suite.
7. Confirmed CD runs `alembic upgrade head` as a one-off ECS task before the
   service update (`.github/workflows/deploy.yml`), so a data migration reaches prod.

## Changes made

1. **Single source of truth** — `backend/app/modules/skills/seed_data.py`:
   `SKILL_SEED` = `(name, description, display_label)` for the 7 sub-skills, built
   from `app.scoring.SUB_SKILLS` + the labels from `f1a2b3c4d567`.
2. **Authoritative fix (migration)** —
   `backend/alembic/versions/r8s9t0u1v234_seed_skill_master_rows.py`
   (down_revision `q7r8s9t0u123`): inserts the 7 rows with
   `INSERT ... ON CONFLICT (name) DO NOTHING` (idempotent; `name` has a unique index).
   Runs automatically in CD's pre-deploy migration step.
3. **Defense-in-depth** — added `seed_skills()` to `seed_all()` in
   `backend/scripts/seed_curriculum.py` so freshly seeded envs get skills even
   without migrations.
4. **Regression guard** — `backend/tests/unit/skills/test_skill_seed_data.py`
   asserts `SKILL_SEED` names == `SUB_SKILLS` and every row has a display_label,
   so a future sub-skill can't be added without a seed row.

## Files modified

- `backend/app/modules/skills/seed_data.py` (new)
- `backend/alembic/versions/r8s9t0u1v234_seed_skill_master_rows.py` (new)
- `backend/scripts/seed_curriculum.py` (+`seed_skills`, wired into `seed_all`)
- `backend/tests/unit/skills/test_skill_seed_data.py` (new)

## Infrastructure changes

None. The fix rides the existing CD migration step (one-off ECS Fargate task
running `alembic upgrade head` before the rolling service update).

## PR(s) created

- https://github.com/orbin123/lingos-ai/pull/118 — squash-merged to `main`.
  (Follow-up commit in the same PR fixed `test_curriculum_v2_db.py::TestSeedAll`,
  which now had to account for `seed_all` also seeding skills.)

## Deployment status

- **Deployed to production.** Deploy run
  [27836977155](https://github.com/orbin123/lingos-ai/actions/runs/27836977155)
  succeeded (5m15s): build → migrate → rolling update → `/health/ready` smoke, all green.
- CloudWatch confirms the migration ran on the live RDS (migrate task log):
  `Running upgrade q7r8s9t0u123 -> r8s9t0u1v234, seed skills: insert the 7 canonical sub-skill master rows`.

## Validation evidence

**Local (throwaway Postgres 16, full migration chain):**
- `alembic upgrade head` applied cleanly; `SELECT * FROM skills` → all 7 rows with
  correct display labels (Grammar, Vocabulary, Pronunciation, Fluency, Thought
  Organization, Listening, Tone & Social).
- Idempotent: re-running the ON CONFLICT insert is a no-op (count stays 7).
- `downgrade -1` removes the 7 rows; `upgrade head` restores them.
- `seed_curriculum.seed_skills` verified idempotent (first run inserts 7, second
  updates 7).
- `pytest tests/unit/skills tests/integration/progress tests/unit/scoring` → 93 passed.

**Production (post-deploy, 2026-06-19):**
- CD migration task exited 0; migrate task CloudWatch log shows the seed migration
  running on the live DB (see Deployment status).
- `GET https://api.lingosai.com/health/ready` → `200`.
- `POST https://api.lingosai.com/diagnosis/submit` (unauth probe) → `401`
  (route reachable, **not** a 500/crash) — logged with `status: 401`, no traceback.
- CloudWatch `filter-log-events` on `/ecs/lingosai-production-backend` for `KeyError`
  over the 30 min post-deploy window → **no events**.

Not done (blocked by policy, not required): a direct prod row-count check via ECS
Exec (`SELECT name FROM skills`) was denied by the Claude Code prod-exec guard.
The migration's effect is deterministic and was verified on a full Postgres chain
locally, and the prod migrate log confirms it ran — so the 7 rows are present. If a
belt-and-suspenders DB confirmation is wanted, run (with authorization):
`aws ecs execute-command … --command "python -c \"from app.core.database import SessionLocal; from app.modules.skills.models import Skill; print(SessionLocal().query(Skill).count())\""`.

## Remaining follow-ups

- Consider a CI job running `alembic upgrade head` against a throwaway Postgres so
  migration-seeded data is exercised — the SQLite `create_all()` harness cannot
  catch this class of bug.
- Optional: an authenticated end-to-end diagnosis submit against prod to observe a
  live `201` (not done here to avoid mutating a real learner's diagnosis state).
