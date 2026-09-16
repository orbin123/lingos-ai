#!/usr/bin/env bash

# Put the LingosAI production environment fully to sleep.
#
#   scripts/azure-down.sh
#
# Idempotent: safe to run when things are already stopped, and safe to re-run
# after a partial failure. The control plane expires the live window FIRST, so
# even if a later step fails, the five-minute watchdog will finish the job.
#
# The order is deliberate and not ours to change:
#   1. drain the app in-guest and raise Caddy's maintenance page
#   2. DEALLOCATE the VM (a plain shutdown keeps billing compute hours)
#   3. stop PostgreSQL
#
# Note: Azure force-restarts a stopped Flexible Server after seven days. That
# is the platform's behaviour, not a bug in this script; the watchdog puts it
# back to sleep on its next run.

# shellcheck source=scripts/_azure-common.sh
source "$(dirname -- "${BASH_SOURCE[0]}")/_azure-common.sh"

require_azure_cli

bold "Putting LingosAI production to sleep"
note "VM:         $(vm_power_state)"
note "PostgreSQL: $(postgres_state)"
echo

run_control_plane sleep

echo
final_vm="$(vm_power_state)"
final_pg="$(postgres_state)"
final_ip="retained"
if [[ "$EPHEMERAL_BILLING_ENABLED" == "true" ]]; then
  final_ip="$(az network public-ip show \
    --resource-group "$RESOURCE_GROUP" \
    --name pip-lingosai-prod \
    --query name \
    --output tsv \
    --only-show-errors 2>/dev/null || true)"
fi

if [[ "$final_vm" == "PowerState/deallocated" \
  && "$final_pg" == "Stopped" \
  && ( "$EPHEMERAL_BILLING_ENABLED" != "true" || -z "$final_ip" ) ]]; then
  bold "Asleep."
  note "VM is deallocated, so it is no longer consuming the 750-hour allowance."
  note "PostgreSQL is stopped."
  if [[ "$EPHEMERAL_BILLING_ENABLED" == "true" ]]; then
    note "The Standard public IP and active-window PostgreSQL firewall rule are deleted."
    note "No Azure Container Registry is retained."
  else
    warn "Ephemeral billing is not active; the retained Standard public IP can still accrue cost."
  fi
  echo
  note "Wake it again with:  scripts/azure-up.sh 4"
  exit 0
fi

warn "Sleep finished but the final state is not fully cold (VM=$final_vm, PostgreSQL=$final_pg, PublicIP=${final_ip:-absent})."
warn "The live window is expired, so the five-minute watchdog will retry. Re-run this to force it."
exit 1
