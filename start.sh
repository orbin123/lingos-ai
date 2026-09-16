#!/usr/bin/env bash

# Start LingosAI's Azure production backend for a bounded window. The default
# is six hours. A local timer requests shutdown at the exact deadline; the
# five-minute GitHub watchdog remains the durable backstop if this computer is
# asleep or offline.

set -Eeuo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT
readonly HOURS="${1:-6}"
readonly EXPECTED_CNAME="lingosai-prod.centralindia.cloudapp.azure.com."
readonly PID_FILE="${TMPDIR:-/tmp}/lingosai-azure-auto-down-${UID}.pid"
readonly LOG_FILE="${TMPDIR:-/tmp}/lingosai-azure-auto-down-${UID}.log"

command -v dig >/dev/null 2>&1 || {
  printf 'ERROR: dig is required to verify the safe DNS cutover.\n' >&2
  exit 1
}

actual_cname="$(dig +short CNAME api.lingosai.com | tr '[:upper:]' '[:lower:]')"
if [[ "$actual_cname" != "$EXPECTED_CNAME" ]]; then
  cat >&2 <<EOF
ERROR: api.lingosai.com must be a CNAME to $EXPECTED_CNAME
before ephemeral billing can be enabled. It currently resolves as:
  ${actual_cname:-no CNAME record}

This guard prevents shutdown from deleting the current static IP while DNS
still points directly at that address.
EOF
  exit 1
fi

export AZURE_EPHEMERAL_BILLING_ENABLED=true
set +e
"$REPO_ROOT/scripts/azure-up.sh" "$HOURS"
up_status=$?
set -e

deadline="$(
  az group show \
    --name rg-lingosai-prod \
    --query 'tags."lingosai-active-until"' \
    --output tsv \
    --only-show-errors
)"
[[ "$deadline" =~ ^20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]] || {
  printf 'ERROR: Azure returned an invalid active-window deadline: %s\n' "$deadline" >&2
  exit 1
}

if [[ -f "$PID_FILE" ]]; then
  old_pid="$(tr -cd '0-9' <"$PID_FILE")"
  if [[ -n "$old_pid" ]] \
    && ps -p "$old_pid" -o command= 2>/dev/null | grep -Fq 'azure-auto-down.sh'; then
    kill "$old_pid" 2>/dev/null || true
  fi
fi

nohup "$REPO_ROOT/scripts/azure-auto-down.sh" "$deadline" \
  >"$LOG_FILE" 2>&1 </dev/null &
timer_pid=$!
printf '%s\n' "$timer_pid" >"$PID_FILE"

printf '\nAutomatic shutdown scheduled for %s.\n' "$deadline"
printf 'Local fallback log: %s\n' "$LOG_FILE"
printf 'The GitHub watchdog also enforces the deadline within five minutes.\n'

exit "$up_status"
