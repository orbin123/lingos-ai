# AGENT_PROGRESS

Execution log for closing `docs/POLISHED_PRODUCTION_PLAN.md`, one gap per session.
Most-recent session first.

---

## Session 2 — Gap G2: Branch protection on `main`

**Status:** code (path-filter fix) implemented; PR open, **not merged**. Branch protection
**enablement is deferred to post-merge** (must run *after* the PR merges, or open PRs wedge).
**Branch:** `feat/g2-branch-protection`
**Date:** 2026-06-18

### Why this gap, why now
G1 merged (`43ee238`), so `push: main` now auto-deploys the backend **with no gate**. Until G2
lands, every merge to `main` is an unattended prod deploy with no required-check guard rail. G2 is
the guard rail. Verified pre-state: `gh api .../branches/main/protection` → **404 "Branch not
protected."**

### The Appendix B path-filter gotcha (handled first, as the plan requires)
Every CI workflow's `pull_request` trigger was `paths:`-filtered. If those jobs are marked
**required** under `strict: true`, a PR that doesn't touch the filtered path never triggers the job,
so the required context never reports and the PR can **never merge**. Fix: drop the `paths:` filter
from the `pull_request` trigger in the four workflows whose jobs become required contexts, so every
PR runs every required gate.

### Completed work (code)
- Removed the `paths:` block from the **`pull_request`** trigger of `backend.yml`, `frontend.yml`,
  `contract.yml`, `docker.yml` (added an explanatory comment in each). Every PR now runs:
  `lint`, `types`, `unit`, `integration`, `migrations`, `coverage` (backend), `ci` (frontend),
  `openapi-drift` (contract), `docker-build` (docker).
- **Left `push:` paths filters intact** — post-merge `push: main` runs don't gate PRs, so there's no
  reason to burn CI minutes there.
- **Left `backend-curriculum.yml` untouched** — `curriculum-seed-smoke` stays optional per the plan
  (Appendix B lists it "optional to require"), so its path filter can stay.

### Branch-protection enablement (deferred to post-merge — founder-gated decisions captured)
Decisions captured this session: `required_approving_review_count: 0` (solo-founder self-merge),
`strict: true`, `enforce_admins: true`, 9 required contexts (curriculum-seed-smoke NOT required).
The agent will run this **after** the PR merges:
```bash
gh api -X PUT repos/orbin123/lingos-ai/branches/main/protection \
  -F 'required_status_checks.strict=true' \
  -F 'required_status_checks.contexts[]=lint' \
  -F 'required_status_checks.contexts[]=types' \
  -F 'required_status_checks.contexts[]=unit' \
  -F 'required_status_checks.contexts[]=integration' \
  -F 'required_status_checks.contexts[]=migrations' \
  -F 'required_status_checks.contexts[]=coverage' \
  -F 'required_status_checks.contexts[]=ci' \
  -F 'required_status_checks.contexts[]=openapi-drift' \
  -F 'required_status_checks.contexts[]=docker-build' \
  -F 'required_pull_request_reviews.required_approving_review_count=0' \
  -F 'enforce_admins=true' -F 'restrictions='
```
(Includes `migrations`, which `DEPLOY.md` §5 omits.)

### Files changed
- `.github/workflows/backend.yml` — drop PR-trigger `paths:`.
- `.github/workflows/frontend.yml` — drop PR-trigger `paths:`.
- `.github/workflows/contract.yml` — drop PR-trigger `paths:`.
- `.github/workflows/docker.yml` — drop PR-trigger `paths:`.
- `docs/AGENT_PROGRESS.md` — this log.

### Verification performed
- **YAML valid:** `ruby -ryaml -e "YAML.load_file(...)"` on all four → OK.
- **Trigger structure confirmed:** parsed each `on:` — `pull_request.paths` is now **(none)** on all
  four; `push.branches=[main]` and `push.paths` still present (intentional).
- **Context names verified against job names** in the workflow files: backend jobs `lint/types/unit/
  integration/migrations/coverage`, frontend `ci`, contract `openapi-drift`, docker `docker-build` —
  all 9 match the plan's required list exactly.
- **This PR self-proves the gates:** it edits all four `.github/workflows/*.yml` files, which match
  each workflow's own `.github/workflows/*.yml` path filter, so every required check runs on this PR.
- **Live branch-protection proof is intentionally NOT done here** — enablement is post-merge.

### Decisions
- Drop `paths:` only on the **PR** trigger (Appendix B "Recommended" option), not the push trigger.
- Keep `curriculum-seed-smoke` optional → its workflow is untouched.
- Self-merge (`review_count: 0`) + `enforce_admins: true` (founder decisions, captured above).

### Risks
- ⚠️ **Ordering is load-bearing:** branch protection must be enabled **only after** this PR merges.
  Enabling it while this PR is open would immediately require the (now-unfiltered) contexts on it —
  which is fine for *this* PR (it triggers them all) but would wedge any *other* open PR that hasn't
  re-run since the filter change. Enable post-merge.
- After enablement with `enforce_admins: true`, the founder can no longer push directly to `main` —
  all changes go through PRs. This is intended.
- More CI minutes: every PR (incl. dependabot, docs-only) now runs the full backend+frontend+docker+
  contract suite. Acceptable at this repo size (the plan's stated trade-off).

### Founder actions required
1. **Review + merge** PR `feat/g2-branch-protection`.
2. After merge, **tell the agent** so it runs the `gh api` enablement command and verifies the rule.
3. (Optional) Confirm the guard rail by opening a throwaway PR with a deliberately failing check and
   verifying it cannot be merged.

### Next recommended gap
**G3 — post-deploy live smoke** (extend the `deploy.yml` `/health/ready` smoke to also assert
`https://www.lingosai.com` 200 + one cheap authenticated GET) and **delete the stray empty
`frontend/e2e/` directory** + any remaining phantom-E2E references. Small, no live-prod risk, and it
completes the Phase A "CI/CD lockstep" trio (G1+G2+G3).

---

## Session 1 — Gap G1: CI/CD lockstep (auto-deploy + auto-rollback)

**Status:** implemented; PR open, **not merged** (merge = first live auto-deploy — founder-gated).
**Branch:** `feat/g1-cicd-lockstep`
**Date:** 2026-06-18

### Completed work
- **G1.1** — `deploy.yml` now triggers on `push: branches: [main]` (alongside `workflow_dispatch`).
- **G1.2** — Fixed the env/concurrency binding: both `environment:` and `concurrency.group` now
  resolve `${{ github.event.inputs.environment || 'production' }}` (was bare `inputs.environment`,
  which is **null on a push** → would fail to target the `production` GitHub Environment / OIDC role).
- **G1.3** — Added a "Capture current task-def (rollback target)" step before the rolling update;
  rewrote the smoke step to, on failure, re-point the service at that task-def, wait for stable, and
  fail the job (was a manual "roll back yourself" message).
- **G1.4** — Removed the dead `DATE_TAG` from the "Compute image tags" step (immutable ECR repo only
  ever pushes `git-<sha>`).
- **G1.5** — Doc-only: documented in `DEPLOY.md` §4 that a `main` merge fires Vercel (FE) + `deploy.yml`
  (BE) on the same commit. No code; live confirmation is a founder observation.
- Reconciled `DEPLOY.md` §2/§4/§6 with the implemented workflow (single immutable tag; auto-rollback;
  forward-only migration caveat; automatic push trigger).

### Files changed
- `.github/workflows/deploy.yml` — trigger, env binding, rollback, date_tag removal.
- `docs/DEPLOY.md` — §2 tag scheme, §4 lockstep note, §6 implemented-behavior rewrite.
- `docs/AGENT_PROGRESS.md` — this log.

### Commits
- `1a49bef ci(deploy): auto-deploy on push to main, fix env binding, add auto-rollback`
- `1646ad9 docs(deploy): reconcile DEPLOY.md with the implemented deploy.yml`
- (this doc commit)

### Verification performed
- **YAML valid:** `ruby -ryaml -e "YAML.load_file('.github/workflows/deploy.yml')"` → OK
  (also via backend venv `python -c "import yaml; yaml.safe_load(...)"` → OK).
- **Env binding target exists:** `gh api repos/orbin123/lingos-ai/environments` lists `production`;
  `.../environments/production/variables` carries all 10 vars the workflow reads
  (AWS_DEPLOY_ROLE_ARN, AWS_REGION, ECR_REPOSITORY, ECS_CLUSTER, ECS_MIGRATE_FAMILY,
  ECS_SECURITY_GROUP, ECS_SERVICE, ECS_SUBNETS, ECS_TASK_FAMILY, HEALTHCHECK_URL). So on a push the
  job binds to `production` and the OIDC role + vars resolve.
- **Diff review:** `date_tag` fully removed; both env references use `|| 'production'`; rollback step
  references `$PREV_TD` captured before the rolling update.
- **Live deploy/rollback proof is intentionally NOT done here** — it deploys to real prod and is a
  founder action (see below).

### Findings
- The phantom-E2E references the plan's G3 mentions live **only** in the historical docs
  (`PRODUCTION_COMPLETION_PLAN.md`, `complete_production_plan.md`), which POLISHED explicitly keeps as
  build logs. The active workflows had **no** e2e references. Only stray active artifact is the empty
  `frontend/e2e/` directory (left for G3).
- There is **no lowercase `staging` GitHub Environment** (only `production`). The `workflow_dispatch`
  default is `staging`, so a manual staging dispatch would fail to bind an environment. Pre-existing,
  out of G1 scope — noted for whoever wires staging.

### Decisions
- Kept the smoke gate on `/health/ready` only (did **not** extend to `www` / a public GET) — that is
  G3's scope, deliberately deferred to keep this one gap.
- Auto-rollback is **service-only** (re-point task-def). Migrations are forward-only and are **not**
  reverted — documented in both the workflow and `DEPLOY.md`.

### Risks
- ⚠️ **No branch protection yet (G2).** With `push: main` live, *every* merge to `main` triggers an
  immediate **production** deploy with **no required-status-check gate**. Until G2 lands, merge to
  `main` deliberately. **This makes G2 the necessary next gap.**
- First merge after this PR = the first unattended prod deploy. Recommend the founder run the manual
  `workflow_dispatch → production` check first (below) to prove the binding before relying on push.

### Founder actions required (live proof — cannot be done by the agent)
1. **Review + merge** PR `feat/g1-cicd-lockstep`. Merging is the first live auto-deploy — be ready.
2. **(Recommended first) Manual binding check:** Actions → `deploy` → "Run workflow" →
   `environment: production`. Confirm it assumes the OIDC role, builds/pushes `git-<sha>`, migration
   exits 0, ECS rollout `COMPLETED`, smoke 200. This proves G1.2 without depending on a merge.
3. **Auto-deploy proof:** after merge, watch Actions auto-run `deploy` on the merge commit → new ECR
   `git-<sha>` → migrate exit 0 → rollout COMPLETED → smoke 200; confirm Vercel deployed the same
   commit (G1.5).
4. **(Optional) Rollback proof:** in a dispatch run, point `HEALTHCHECK_URL` at a failing URL (or
   otherwise force smoke red) and confirm the service is re-pointed at the prior task-def and the job
   fails.

### Next recommended gap
**G2 — branch protection on `main`** (Appendix B): first resolve the path-filter gotcha (drop
`paths:` filters or add always-pass dummy jobs), then enable required contexts incl. `migrations`.
It is the guard rail this gap's auto-deploy requires.
