#!/usr/bin/env bash

# Local exact-deadline fallback launched by start.sh. The scheduled GitHub
# watchdog is authoritative when the operator's computer is unavailable.

set -Eeuo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
readonly REPO_ROOT
readonly DEADLINE="${1:-}"

[[ "$DEADLINE" =~ ^20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]] || {
  printf 'Invalid UTC deadline: %s\n' "$DEADLINE" >&2
  exit 2
}

remaining_seconds="$(python3 - "$DEADLINE" <<'PY'
from datetime import datetime, timezone
import sys

deadline = datetime.strptime(sys.argv[1], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
print(max(0, int((deadline - datetime.now(timezone.utc)).total_seconds())))
PY
)"

sleep "$remaining_seconds"
export AZURE_EPHEMERAL_BILLING_ENABLED=true
exec "$REPO_ROOT/scripts/azure-down.sh"
