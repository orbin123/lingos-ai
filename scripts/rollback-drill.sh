#!/usr/bin/env bash
#
# rollback-drill.sh — timed backend rollback drill (G8).
#
# Proves the documented rollback (RUNBOOK §8 / deploy.yml) works and TIMES it
# against the plan's <5 min target. It performs a REAL rollback: re-points the
# ECS service at the previous ACTIVE task-def revision, waits for stable, smokes
# /health/ready, prints the elapsed rollback time, then rolls FORWARD to the
# original revision so prod ends exactly where it started.
#
# ⚠️ THIS MUTATES PRODUCTION. With a single task each step is a brief rolling
# replace. Run in a quiet window. Use --dry-run first to preview the exact
# commands without touching anything.
#
# Usage:
#   ./scripts/rollback-drill.sh --dry-run     # preview, no changes
#   ./scripts/rollback-drill.sh               # run the real timed drill (prompts)
#   ./scripts/rollback-drill.sh --yes         # skip the confirmation prompt
#
# Overridable via env (defaults target production):
#   AWS_REGION, ECS_CLUSTER, ECS_SERVICE, ECS_TASK_FAMILY, HEALTHCHECK_URL
#
# Requirements: bash, curl, jq, AWS CLI with ecs:UpdateService on the prod
# service (the read-only verifier is enough to *check* readiness; this drill
# needs write access).
#
# NOTE: the CLI user defaults to ap-south-1 — every aws call here passes
# --region explicitly (RUNBOOK §8 gotcha).

set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
ECS_CLUSTER="${ECS_CLUSTER:-lingosai-production}"
ECS_SERVICE="${ECS_SERVICE:-lingosai-production-backend}"
ECS_TASK_FAMILY="${ECS_TASK_FAMILY:-lingosai-production-backend}"
HEALTHCHECK_URL="${HEALTHCHECK_URL:-https://api.lingosai.com/health/ready}"

DRY_RUN=0
ASSUME_YES=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --yes|-y)  ASSUME_YES=1 ;;
    -h|--help) sed -n '2,30p' "$0"; exit 0 ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

for bin in aws jq curl; do
  command -v "$bin" >/dev/null 2>&1 || { echo "ERROR: '$bin' not on PATH." >&2; exit 2; }
done

aws() { command aws --region "$AWS_REGION" "$@"; }   # always pin the region

smoke() {
  # Retry /health/ready up to 10×/6s (mirrors deploy.yml's smoke gate).
  local i code
  for i in $(seq 1 10); do
    code=$(curl -sSL -o /dev/null -w '%{http_code}' "$HEALTHCHECK_URL" 2>/dev/null || echo 000)
    [ "$code" = "200" ] && { echo "  smoke: 200"; return 0; }
    echo "  smoke: got $code (attempt $i/10), retrying in 6s…"
    sleep 6
  done
  return 1
}

echo "LingosAI — backend rollback drill ($([ "$DRY_RUN" = 1 ] && echo DRY-RUN || echo LIVE))"
echo "  region=$AWS_REGION  cluster=$ECS_CLUSTER  service=$ECS_SERVICE"
echo "  smoke=$HEALTHCHECK_URL"
echo

# --- Resolve current + previous revisions -----------------------------------
CURRENT_TD=$(aws ecs describe-services --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE" \
  --query 'services[0].taskDefinition' --output text)
[ -n "$CURRENT_TD" ] && [ "$CURRENT_TD" != "None" ] || { echo "ERROR: could not read current task-def." >&2; exit 1; }

# Newest-first list of ACTIVE revisions; [0] is current, [1] is the rollback target.
PREV_TD=$(aws ecs list-task-definitions --family-prefix "$ECS_TASK_FAMILY" --status ACTIVE \
  --sort DESC --query 'taskDefinitionArns[1]' --output text)
if [ -z "$PREV_TD" ] || [ "$PREV_TD" = "None" ]; then
  echo "ERROR: no previous ACTIVE revision to roll back to (need >=2)." >&2
  exit 1
fi

echo "  current revision : ${CURRENT_TD##*/}"
echo "  rollback target  : ${PREV_TD##*/}"
echo

if [ "$DRY_RUN" = 1 ]; then
  cat <<EOF
DRY-RUN — would run, timing the rollback phase:
  # roll BACK
  aws ecs update-service --region $AWS_REGION --cluster $ECS_CLUSTER --service $ECS_SERVICE \\
    --task-definition $PREV_TD
  aws ecs wait services-stable --region $AWS_REGION --cluster $ECS_CLUSTER --services $ECS_SERVICE
  curl -fsS $HEALTHCHECK_URL   # smoke (10×/6s)
  # then roll FORWARD to restore the original revision
  aws ecs update-service --region $AWS_REGION --cluster $ECS_CLUSTER --service $ECS_SERVICE \\
    --task-definition $CURRENT_TD
  aws ecs wait services-stable --region $AWS_REGION --cluster $ECS_CLUSTER --services $ECS_SERVICE
EOF
  exit 0
fi

if [ "$ASSUME_YES" != 1 ]; then
  echo "⚠️  This will roll PRODUCTION back to ${PREV_TD##*/}, then forward again."
  printf "    Type 'rollback' to proceed: "
  read -r reply
  [ "$reply" = "rollback" ] || { echo "aborted."; exit 1; }
fi

# --- Phase 1: roll BACK (timed — this is the <5 min metric) ------------------
echo
echo ">> Rolling back to ${PREV_TD##*/} …"
T0=$(date +%s)
aws ecs update-service --cluster "$ECS_CLUSTER" --service "$ECS_SERVICE" \
  --task-definition "$PREV_TD" >/dev/null
aws ecs wait services-stable --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE"
if ! smoke; then
  echo "ERROR: smoke failed after rollback — investigate before proceeding." >&2
  exit 1
fi
T1=$(date +%s)
ROLLBACK_SECS=$(( T1 - T0 ))
echo ">> ROLLBACK COMPLETE in ${ROLLBACK_SECS}s ($(( ROLLBACK_SECS / 60 ))m $(( ROLLBACK_SECS % 60 ))s)."
if [ "$ROLLBACK_SECS" -le 300 ]; then
  echo "   ✅ within the <5 min (300s) target."
else
  echo "   ⚠️  exceeded the 5 min target — record + investigate."
fi

# --- Phase 2: roll FORWARD to restore the original revision ------------------
echo
echo ">> Restoring original revision ${CURRENT_TD##*/} …"
aws ecs update-service --cluster "$ECS_CLUSTER" --service "$ECS_SERVICE" \
  --task-definition "$CURRENT_TD" >/dev/null
aws ecs wait services-stable --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE"
if ! smoke; then
  echo "ERROR: smoke failed after restoring the original revision — service may need attention." >&2
  exit 1
fi
echo ">> Restored. Prod is back on ${CURRENT_TD##*/}."
echo
echo "============================================================"
echo "Rollback drill result:  ${ROLLBACK_SECS}s  (target <300s)"
echo "Record this number in docs/G8_ROLLBACK_DR_RUNBOOK.md (definition of done)."
echo "============================================================"
