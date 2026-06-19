# G8 — Rollback drill + DR runbook

> **Gap G8** of [`POLISHED_PRODUCTION_PLAN.md`](./POLISHED_PRODUCTION_PLAN.md) (Phase C).
> Closes the launch items: *run the documented rollback once and record the time (<5 min),
> and row-verify an RDS snapshot restore — without ever putting the prod password in an env
> override.*
>
> ⚠️ `docs/` is git-ignored — force-add: `git add -f docs/G8_ROLLBACK_DR_RUNBOOK.md`.

All commands assume `--region us-east-1`, account `924903313980`, and the `lingos-ai-cli`
credentials. The helper scripts pin `--region` for you (the CLI user defaults to `ap-south-1`).

---

## What the code/IaC PR already did (`feat/g8-rollback-dr`)

| Change | File | Effect |
|---|---|---|
| Enable **ECS Exec** on the backend service + grant the task role SSM messaging perms | `infra/terraform/modules/compute/main.tf` | Lets an IAM-gated operator open a shell in a running task → the **password-safe** way to row-verify the restore (reuse the in-container `DATABASE_URL`, never an env override). It's the prerequisite RUNBOOK §3 assumed but that wasn't actually enabled. |
| Read-only **DR-readiness verifier** | `scripts/verify-dr-readiness.sh` | Proves the drill preconditions live: service healthy, a previous task-def revision exists, ECS Exec on, RDS Multi-AZ/PITR/deletion-protect/private, recent snapshot. **No mutations.** |
| **Timed rollback drill** | `scripts/rollback-drill.sh` | Re-points the service at the previous revision, times it vs. the <5 min target, then rolls forward to the original. `--dry-run` + typed confirmation. |
| **RDS restore drill** | `scripts/rds-restore-drill.sh` | Restores the latest automated snapshot to a throwaway private instance (prod subnet group + SG discovered live), times the spin-up, and prints the exact ECS Exec row-verify steps. `--teardown` deletes it. |

**Already in place before this PR (verified, no change needed):** deploy.yml auto-rollback on
smoke failure (G1); the manual rollback procedure (RUNBOOK §8); RDS daily snapshots + 7-day PITR +
deletion protection + Multi-AZ (the restore source); the `/health/ready` smoke target.

### ⚠️ ECS Exec needs an apply **and** a fresh deployment — in that order

`terraform apply` sets `enable_execute_command = true` on the service, but **ECS Exec only works
for tasks launched *after* the change**. So you must `--force-new-deployment` once before the
row-verify drill, or `execute-command` will error with a "container runtime" / "not connected"
message on the old task. The readiness verifier's "ecs exec enabled" check stays **FAIL** until
both steps are done — that's the intended "not done yet" signal (it reads the service flag; the
runtime check is `execute-command` itself in step 4).

---

## Founder steps (in order)

### 0. [AUTO] Check readiness first
```bash
./scripts/verify-dr-readiness.sh | tee /tmp/dr-readiness.log
```
Pre-apply this exits **1** with exactly one FAIL — `ecs exec enabled` — and everything else PASS
(this is the agent-captured baseline: `PASS=10 FAIL=1` on 2026-06-19). After step 1 it should exit
**0**.

### 1. [FOUNDER] Apply ECS Exec + force a fresh deployment
```bash
cd infra/terraform/envs/production
terraform apply        # adds enable_execute_command + SSM perms (review the plan: 1 service + 1 IAM policy change)

# New tasks must launch to carry the exec agent:
aws ecs update-service --cluster lingosai-production \
  --service lingosai-production-backend --force-new-deployment --region us-east-1
aws ecs wait services-stable --cluster lingosai-production \
  --services lingosai-production-backend --region us-east-1
```
Re-run `./scripts/verify-dr-readiness.sh` → expect **exit 0** (`ecs exec enabled` now PASS).

> If you need the SSM Session Manager plugin locally for `execute-command`, install it once:
> AWS docs → "Install the Session Manager plugin". `execute-command` will tell you if it's missing.

### 2. [FOUNDER] Timed backend rollback drill (the <5 min metric)
Run in a quiet window (a single task means each phase is a brief rolling replace). Preview first:
```bash
./scripts/rollback-drill.sh --dry-run        # shows current→previous revision + the commands
./scripts/rollback-drill.sh                  # real drill (type 'rollback' to confirm)
```
It rolls the service back to the previous revision, waits stable, smokes `/health/ready`, prints
**`ROLLBACK COMPLETE in <N>s`**, then rolls forward to the original revision so prod is unchanged
at the end. **Record the `<N>s`** — that is the G8 rollback time (<300s target).

**Frontend rollback (one click, no script):** Vercel → *Deployments → previous → Promote to
Production*. Note the time for completeness.

### 3. [FOUNDER] RDS restore drill
```bash
./scripts/rds-restore-drill.sh --dry-run     # shows snapshot, subnet group, SG it will use
./scripts/rds-restore-drill.sh               # restore latest snapshot → lingosai-restore-drill
```
It times the spin-up (last manual drill: 7m 28s on 2026-06-18; RTO target <1h) and prints the
restored **endpoint** + the row-verify steps for the next step. The drill instance is **private,
single-AZ, throwaway** and does **not** touch prod.

### 4. [FOUNDER] Row-verify the restore via ECS Exec (password-safe)
Follow the steps the restore drill printed (also summarized here). The key property: the prod
password is read from the **already-injected** `$DATABASE_URL` inside a running task — never typed,
never written to a file, never an env override.
```bash
TASK=$(aws ecs list-tasks --region us-east-1 --cluster lingosai-production \
  --service-name lingosai-production-backend --query 'taskArns[0]' --output text)
aws ecs execute-command --region us-east-1 --cluster lingosai-production \
  --task "$TASK" --container backend --interactive --command "/bin/sh"
# Inside the shell, paste the python snippet from the restore-drill output:
#   it swaps the host in $DATABASE_URL for the drill endpoint, connects, and prints
#   alembic_version + the top tables by row count. Compare against prod.
```
Expected rows present + matching `alembic_version` == **restore verified**.

### 5. [FOUNDER] Tear down + re-check
```bash
./scripts/rds-restore-drill.sh --teardown    # delete-db-instance --skip-final-snapshot
./scripts/verify-dr-readiness.sh             # exit 0; confirms prod still healthy + exec on
```

---

## Definition of done for G8
- [ ] ECS Exec applied + fresh deployment; `verify-dr-readiness.sh` exits **0**.
- [ ] Backend rollback drill run once; **rollback time recorded** and <5 min (paste the `<N>s` here: ____).
- [ ] Frontend rollback path confirmed (Vercel promote) — optional time noted.
- [ ] RDS snapshot restored to `lingosai-restore-drill`; **spin-up time recorded** (____), <1h RTO.
- [ ] Restore **row-verified** via ECS Exec: `alembic_version` + key table row counts captured and
      match prod (evidence pasted).
- [ ] Drill instance torn down (`--teardown`); no stray RDS cost.

## Notes / safety
- **The drills mutate prod / cost money.** `rollback-drill.sh` ends prod on its original revision;
  `rds-restore-drill.sh` creates a real (small) instance until `--teardown`. Both have `--dry-run`.
- **Nothing here changes the prod DB.** The restore is to a *separate* throwaway instance; ECS Exec
  reads but does not write.
- The rollback drill's forward step re-points to the *exact* task-def ARN that was live at start, so
  even if a deploy lands mid-drill the script restores the revision it captured (run it when no
  deploy is in flight to avoid confusion).
- ECS Exec is IAM-gated (the deploy/admin principal), not exposed to the app or learners; it grants
  an interactive shell, so treat the privilege like any prod-access grant.
