#!/usr/bin/env bash
#
# rds-restore-drill.sh — RDS restore drill + password-safe row-verify (G8).
#
# Codifies RUNBOOK §3 so the disaster-recovery drill is repeatable: find the
# latest automated snapshot, restore it to a throwaway private instance
# (lingosai-restore-drill) reusing the prod subnet group + RDS SG, time the
# spin-up, then print the EXACT ECS Exec row-verify command. Optionally tear the
# instance down.
#
# Row-verify is intentionally NOT automated by this script: it happens hands-on
# via `aws ecs execute-command` into a running task, reusing the password
# already injected as DATABASE_URL inside the container — the prod password is
# NEVER written to a file or an env override (plan §G8 / RUNBOOK §3).
#
# ⚠️ THIS CREATES A REAL RDS INSTANCE (cost until torn down). It does NOT touch
# the live prod database. Always --teardown when done.
#
# Usage:
#   ./scripts/rds-restore-drill.sh --dry-run    # preview the commands
#   ./scripts/rds-restore-drill.sh              # restore + print verify steps
#   ./scripts/rds-restore-drill.sh --teardown   # delete the drill instance
#
# Overridable via env (defaults target production):
#   AWS_REGION, RDS_INSTANCE_ID, DRILL_ID, DRILL_CLASS,
#   ECS_CLUSTER, ECS_SERVICE, ECS_CONTAINER
#
# Requirements: bash, jq, AWS CLI with rds:RestoreDBInstanceFromDBSnapshot etc.
# NOTE: the CLI user defaults to ap-south-1 — every aws call passes --region.

set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
RDS_INSTANCE_ID="${RDS_INSTANCE_ID:-lingosai-production-postgres}"
DRILL_ID="${DRILL_ID:-lingosai-restore-drill}"
DRILL_CLASS="${DRILL_CLASS:-db.t4g.small}"
ECS_CLUSTER="${ECS_CLUSTER:-lingosai-production}"
ECS_SERVICE="${ECS_SERVICE:-lingosai-production-backend}"
ECS_CONTAINER="${ECS_CONTAINER:-backend}"

DRY_RUN=0
TEARDOWN=0
for arg in "$@"; do
  case "$arg" in
    --dry-run)  DRY_RUN=1 ;;
    --teardown) TEARDOWN=1 ;;
    -h|--help)  sed -n '2,33p' "$0"; exit 0 ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

for bin in aws jq; do
  command -v "$bin" >/dev/null 2>&1 || { echo "ERROR: '$bin' not on PATH." >&2; exit 2; }
done
aws() { command aws --region "$AWS_REGION" "$@"; }

# --- Teardown path ----------------------------------------------------------
if [ "$TEARDOWN" = 1 ]; then
  echo ">> Tearing down drill instance $DRILL_ID …"
  if [ "$DRY_RUN" = 1 ]; then
    echo "DRY-RUN: aws rds delete-db-instance --region $AWS_REGION --db-instance-identifier $DRILL_ID --skip-final-snapshot --delete-automated-backups"
    exit 0
  fi
  aws rds delete-db-instance --db-instance-identifier "$DRILL_ID" \
    --skip-final-snapshot --delete-automated-backups >/dev/null
  echo ">> Deletion initiated (no final snapshot)."
  exit 0
fi

echo "LingosAI — RDS restore drill ($([ "$DRY_RUN" = 1 ] && echo DRY-RUN || echo LIVE))"
echo "  region=$AWS_REGION  source=$RDS_INSTANCE_ID  drill=$DRILL_ID ($DRILL_CLASS)"
echo

# --- Discover prod networking (don't hardcode) ------------------------------
prod=$(aws rds describe-db-instances --db-instance-identifier "$RDS_INSTANCE_ID" \
  --query 'DBInstances[0].{sg:VpcSecurityGroups[0].VpcSecurityGroupId,sub:DBSubnetGroup.DBSubnetGroupName,eng:EngineVersion}' \
  --output json)
SG=$(echo "$prod"     | jq -r '.sg')
SUBNETS=$(echo "$prod" | jq -r '.sub')
ENGINE=$(echo "$prod" | jq -r '.eng')

# --- Latest automated snapshot (the restore source) -------------------------
SNAP=$(aws rds describe-db-snapshots --snapshot-type automated \
  --query "reverse(sort_by(DBSnapshots[?DBInstanceIdentifier=='$RDS_INSTANCE_ID'],&SnapshotCreateTime))[0].DBSnapshotIdentifier" \
  --output text)
[ -n "$SNAP" ] && [ "$SNAP" != "None" ] || { echo "ERROR: no automated snapshot found." >&2; exit 1; }

echo "  snapshot   : $SNAP"
echo "  subnet grp : $SUBNETS"
echo "  rds sg     : $SG"
echo "  engine     : $ENGINE"
echo

if [ "$DRY_RUN" = 1 ]; then
  cat <<EOF
DRY-RUN — would run:
  aws rds restore-db-instance-from-db-snapshot --region $AWS_REGION \\
    --db-instance-identifier $DRILL_ID --db-snapshot-identifier $SNAP \\
    --db-instance-class $DRILL_CLASS --no-multi-az --no-publicly-accessible \\
    --db-subnet-group-name $SUBNETS --vpc-security-group-ids $SG
  aws rds wait db-instance-available --region $AWS_REGION --db-instance-identifier $DRILL_ID
  # then row-verify via ECS Exec (printed below), then:
  ./scripts/rds-restore-drill.sh --teardown
EOF
  exit 0
fi

# --- Restore + time the spin-up ---------------------------------------------
echo ">> Restoring $SNAP → $DRILL_ID (private, single-AZ) …"
T0=$(date +%s)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier "$DRILL_ID" --db-snapshot-identifier "$SNAP" \
  --db-instance-class "$DRILL_CLASS" --no-multi-az --no-publicly-accessible \
  --db-subnet-group-name "$SUBNETS" --vpc-security-group-ids "$SG" >/dev/null
echo "   waiting for available (RTO target <1h) …"
aws rds wait db-instance-available --db-instance-identifier "$DRILL_ID"
T1=$(date +%s)
SECS=$(( T1 - T0 ))
ENDPOINT=$(aws rds describe-db-instances --db-instance-identifier "$DRILL_ID" \
  --query 'DBInstances[0].Endpoint.Address' --output text)
echo ">> Available in ${SECS}s ($(( SECS / 60 ))m $(( SECS % 60 ))s).  endpoint=$ENDPOINT"
echo

# --- Print the password-safe ECS Exec row-verify steps ----------------------
cat <<EOF
============================================================
ROW-VERIFY (hands-on, password-safe — run these yourself):

1) Find a running backend task:
   TASK=\$(aws ecs list-tasks --region $AWS_REGION --cluster $ECS_CLUSTER \\
     --service-name $ECS_SERVICE --query 'taskArns[0]' --output text)

2) Open a shell in the task (requires ECS Exec — enabled in this PR; if it
   errors, the task predates the change → 'aws ecs update-service
   --force-new-deployment' first):
   aws ecs execute-command --region $AWS_REGION --cluster $ECS_CLUSTER \\
     --task "\$TASK" --container $ECS_CONTAINER --interactive --command "/bin/sh"

3) Inside the shell, point a connection at the DRILL endpoint reusing the
   password already in \$DATABASE_URL (never written to a file/override):
   python3 - <<'PY'
   import os
   from urllib.parse import urlsplit, urlunsplit
   import psycopg
   u = urlsplit(os.environ["DATABASE_URL"].replace("postgresql+psycopg", "postgresql"))
   creds = u.netloc.rsplit("@", 1)[0]                      # user:pass
   drill = urlunsplit((u.scheme, f"{creds}@$ENDPOINT:5432", u.path, "", ""))
   with psycopg.connect(drill) as c:
       v = c.execute("select version_num from alembic_version").fetchone()
       print("alembic_version:", v[0] if v else "none")
       rows = c.execute(
           "select relname, n_live_tup from pg_stat_user_tables "
           "order by n_live_tup desc limit 8").fetchall()
       for name, n in rows:
           print(f"  {name:30s} {n}")
   PY
   # Compare these counts/schema head against prod — they should match the
   # snapshot's point in time. Expected rows present == restore verified.

4) When done, tear the drill instance down:
   ./scripts/rds-restore-drill.sh --teardown

Record the spin-up time (${SECS}s) and the verified row counts in
docs/G8_ROLLBACK_DR_RUNBOOK.md (definition of done).
============================================================
EOF
