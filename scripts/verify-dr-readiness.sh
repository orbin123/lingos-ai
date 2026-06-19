#!/usr/bin/env bash
#
# verify-dr-readiness.sh — read-only disaster-recovery readiness verifier (G8).
#
# Proves that the *preconditions* for the rollback + RDS-restore drills
# (POLISHED_PRODUCTION_PLAN §G8) are in place against LIVE prod: ECS Exec is
# enabled (the password-safe path for the row-verify drill), a rollback target
# task-def revision exists, a recent RDS snapshot exists, and the RDS data
# protections (Multi-AZ, PITR retention, deletion protection, private) hold. It
# makes **no mutations** — only `curl` GET and read-only `aws describe/list`.
#
# It does NOT run the drills themselves (they mutate prod / create a real RDS
# instance) — see docs/G8_ROLLBACK_DR_RUNBOOK.md for the founder steps and the
# evidence to capture (rollback timed <5 min; restored DB row-verified).
#
# Usage:
#   ./scripts/verify-dr-readiness.sh                 # verify prod (defaults)
#   ./scripts/verify-dr-readiness.sh | tee dr.log
#
# Overridable via env vars (defaults target production):
#   API_URL, AWS_REGION, ECS_CLUSTER, ECS_SERVICE, ECS_TASK_FAMILY, RDS_INSTANCE_ID
#
# Requirements: bash, curl, jq, and AWS CLI authenticated for the prod account
# (the read-only `lingos-ai-cli` user is sufficient).
#
# Exit code: 0 if every check PASSes; 1 if any FAILs. WARNs (e.g. a snapshot
# older than 24h) do NOT fail the run.
#
# NOTE: the "ECS Exec enabled" check FAILs until the founder runs
# `terraform apply` + `--force-new-deployment` (the IaC change in this PR sets
# the desired state). A FAIL there is the expected pre-apply "not done yet"
# signal; it flips to PASS once the new tasks carry the exec agent.

set -uo pipefail

# ---------------------------------------------------------------------------
# Config (prod defaults; override via env).
# ---------------------------------------------------------------------------
API_URL="${API_URL:-https://api.lingosai.com}"
AWS_REGION="${AWS_REGION:-us-east-1}"
ECS_CLUSTER="${ECS_CLUSTER:-lingosai-production}"
ECS_SERVICE="${ECS_SERVICE:-lingosai-production-backend}"
ECS_TASK_FAMILY="${ECS_TASK_FAMILY:-lingosai-production-backend}"
RDS_INSTANCE_ID="${RDS_INSTANCE_ID:-lingosai-production-postgres}"

# ---------------------------------------------------------------------------
# Tiny check framework (shared style with verify-prod-parity.sh).
# ---------------------------------------------------------------------------
PASS=0
FAIL=0
WARN=0
RESULTS=()

_record() { RESULTS+=("$1|$2|$3"); }  # status|name|detail

pass() { PASS=$((PASS + 1)); _record "PASS" "$1" "$2"; printf '  \033[32mPASS\033[0m  %s — %s\n' "$1" "$2"; }
fail() { FAIL=$((FAIL + 1)); _record "FAIL" "$1" "$2"; printf '  \033[31mFAIL\033[0m  %s — %s\n' "$1" "$2"; }
warn() { WARN=$((WARN + 1)); _record "WARN" "$1" "$2"; printf '  \033[33mWARN\033[0m  %s — %s\n' "$1" "$2"; }

require() {
  for bin in "$@"; do
    if ! command -v "$bin" >/dev/null 2>&1; then
      echo "ERROR: required tool '$bin' not found on PATH." >&2
      exit 2
    fi
  done
}

http_code() { curl -sSL -o /dev/null -w '%{http_code}' "$1" 2>/dev/null || echo "000"; }

# ---------------------------------------------------------------------------
require curl jq aws

echo "LingosAI — DR readiness verifier (read-only)"
echo "  $(date -u '+%Y-%m-%dT%H:%M:%SZ')  region=$AWS_REGION"
echo "  api=$API_URL  service=$ECS_SERVICE  rds=$RDS_INSTANCE_ID"
echo

# Fail fast if AWS creds are missing/expired.
if ! ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null); then
  echo "ERROR: AWS CLI is not authenticated. Run with valid prod credentials." >&2
  exit 2
fi
echo "  aws account=$ACCOUNT"
echo

# ===========================================================================
echo "[1] Backend service health + rollback target"
# ---------------------------------------------------------------------------
svc=$(aws ecs describe-services --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE" \
  --region "$AWS_REGION" \
  --query 'services[0].{r:runningCount,d:desiredCount,s:status,td:taskDefinition,x:enableExecuteCommand}' \
  --output json 2>/dev/null || echo '{}')
running=$(echo "$svc" | jq -r '.r // "?"')
desired=$(echo "$svc" | jq -r '.d // "?"')
status=$(echo "$svc"  | jq -r '.s // "?"')
td=$(echo "$svc"      | jq -r '.td // "?"')
exec_on=$(echo "$svc" | jq -r '.x // false')

if [ "$status" = "ACTIVE" ] && [ "$running" = "$desired" ] && [ "$running" != "0" ] && [ "$running" != "?" ]; then
  pass "ecs service" "ACTIVE, $running/$desired running (${td##*/})"
else
  fail "ecs service" "status=$status running=$running desired=$desired"
fi

# Rollback target: need >=2 ACTIVE revisions so we can re-point to the previous one.
revs=$(aws ecs list-task-definitions --family-prefix "$ECS_TASK_FAMILY" --status ACTIVE \
  --region "$AWS_REGION" --query 'taskDefinitionArns' --output json 2>/dev/null || echo '[]')
rev_count=$(echo "$revs" | jq 'length')
if [ "$rev_count" -ge 2 ] 2>/dev/null; then
  pass "rollback target" "$rev_count ACTIVE task-def revisions (previous revision available)"
else
  warn "rollback target" "only $rev_count ACTIVE revision(s) — no previous revision to roll back to yet"
fi

# ===========================================================================
echo
echo "[2] ECS Exec (password-safe row-verify path)"
# ---------------------------------------------------------------------------
# enableExecuteCommand on the service is necessary; the running tasks must also
# have been launched after it was enabled (founder --force-new-deployment).
if [ "$exec_on" = "true" ]; then
  pass "ecs exec enabled" "enableExecuteCommand=true on $ECS_SERVICE"
else
  fail "ecs exec enabled" "enableExecuteCommand=$exec_on — run terraform apply + --force-new-deployment (G8 runbook)"
fi

# ===========================================================================
echo
echo "[3] RDS data protections + recent snapshot (restore source)"
# ---------------------------------------------------------------------------
db=$(aws rds describe-db-instances --db-instance-identifier "$RDS_INSTANCE_ID" \
  --region "$AWS_REGION" \
  --query 'DBInstances[0].{maz:MultiAZ,br:BackupRetentionPeriod,dp:DeletionProtection,pub:PubliclyAccessible,st:DBInstanceStatus}' \
  --output json 2>/dev/null || echo '{}')
# NOTE: use a null-guard (not `//`) for booleans — jq's `//` treats `false` as
# empty, so `.pub // "?"` would wrongly yield "?" for a (correct) `false`.
_bool() { echo "$1" | jq -r --arg k "$2" '.[$k] | if . == null then "?" else tostring end'; }
maz=$(_bool "$db" maz)
dp=$(_bool "$db" dp)
pub=$(_bool "$db" pub)
br=$(echo "$db"   | jq -r '.br // "?"')
dbst=$(echo "$db" | jq -r '.st // "?"')

[ "$dbst" = "available" ]   && pass "rds available"        "$RDS_INSTANCE_ID is available" || fail "rds available" "status=$dbst"
[ "$maz" = "true" ]         && pass "rds multi-az"         "Multi-AZ enabled"               || fail "rds multi-az" "MultiAZ=$maz"
[ "$dp" = "true" ]          && pass "rds deletion-protect" "deletion protection on"         || fail "rds deletion-protect" "DeletionProtection=$dp"
[ "$pub" = "false" ]        && pass "rds private"          "not publicly accessible"        || fail "rds private" "PubliclyAccessible=$pub"
if [ "$br" != "?" ] && [ "$br" -ge 7 ] 2>/dev/null; then
  pass "rds PITR retention" "$br-day backup retention (>=7)"
else
  fail "rds PITR retention" "BackupRetentionPeriod=$br (expected >=7)"
fi

# Latest automated snapshot — the restore source. Same query the drill uses.
snap_json=$(aws rds describe-db-snapshots --snapshot-type automated --region "$AWS_REGION" \
  --query "reverse(sort_by(DBSnapshots[?DBInstanceIdentifier=='$RDS_INSTANCE_ID'],&SnapshotCreateTime))[0].{id:DBSnapshotIdentifier,t:SnapshotCreateTime}" \
  --output json 2>/dev/null || echo '{}')
snap_id=$(echo "$snap_json" | jq -r '.id // "None"')
snap_t=$(echo "$snap_json"  | jq -r '.t // ""')
if [ "$snap_id" = "None" ] || [ -z "$snap_id" ]; then
  fail "rds snapshot" "no automated snapshot found for $RDS_INSTANCE_ID"
else
  # Age in hours (best-effort; portable across GNU/BSD date).
  age_note=""
  if [ -n "$snap_t" ]; then
    snap_epoch=$(date -u -d "$snap_t" +%s 2>/dev/null || date -u -j -f "%Y-%m-%dT%H:%M:%S" "${snap_t%%.*}" +%s 2>/dev/null || echo "")
    if [ -n "$snap_epoch" ]; then
      age_h=$(( ( $(date -u +%s) - snap_epoch ) / 3600 ))
      age_note=" (${age_h}h old)"
      if [ "$age_h" -gt 24 ]; then
        warn "rds snapshot age" "latest automated snapshot is ${age_h}h old — expected daily (<24h)"
      else
        pass "rds snapshot age" "latest automated snapshot ${age_h}h old"
      fi
    fi
  fi
  pass "rds snapshot" "restore source: ${snap_id}${age_note}"
fi

# ===========================================================================
echo
echo "[4] API liveness (rollback smoke target)"
# ---------------------------------------------------------------------------
code=$(http_code "$API_URL/health/ready")
[ "$code" = "200" ] && pass "api /health/ready" "200 (drill smoke target reachable)" \
  || fail "api /health/ready" "expected 200, got $code"

# ===========================================================================
echo
echo "============================================================"
echo "Summary:  PASS=$PASS  FAIL=$FAIL  WARN=$WARN"
echo "  Readiness only. The drills themselves (timed rollback, RDS"
echo "  restore + row-verify) are founder-run and prod-mutating —"
echo "  see docs/G8_ROLLBACK_DR_RUNBOOK.md."
echo "============================================================"

[ "$FAIL" -eq 0 ]
