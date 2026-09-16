#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../../.." && pwd)"
control_plane="$repo_root/.github/scripts/azure-control-plane.sh"
fixture_dir="$(mktemp -d)"
trap 'rm -rf -- "$fixture_dir"' EXIT
log_file="$fixture_dir/az.log"
ip_state="$fixture_dir/public-ip-exists"
firewall_state="$fixture_dir/firewall-exists"

export AZURE_RESOURCE_GROUP=rg-lingosai-prod
export AZURE_VM_NAME=vm-lingosai-prod
export AZURE_POSTGRES_SERVER=lingosai-test-postgres
export AZURE_EPHEMERAL_BILLING_ENABLED=true

# shellcheck source=.github/scripts/azure-control-plane.sh
source "$control_plane"

az() {
  printf '%s\n' "$*" >>"$log_file"

  if [[ "$*" == "group show --name rg-lingosai-prod --query location"* ]]; then
    printf 'centralindia\n'
    return 0
  fi
  if [[ "$*" == "network public-ip create "* ]]; then
    touch "$ip_state"
    return 0
  fi
  if [[ "$*" == "network public-ip delete "* ]]; then
    rm -f -- "$ip_state"
    return 0
  fi
  if [[ "$*" == "network public-ip show "* ]]; then
    [[ -f "$ip_state" ]] || return 3
    if [[ "$*" == *"--query ipAddress"* ]]; then
      printf '203.0.113.25\n'
    elif [[ "$*" == *"--query dnsSettings.fqdn"* ]]; then
      printf 'lingosai-prod.centralindia.cloudapp.azure.com\n'
    fi
    return 0
  fi
  if [[ "$*" == "postgres flexible-server firewall-rule create "* ]]; then
    touch "$firewall_state"
    return 0
  fi
  if [[ "$*" == "postgres flexible-server firewall-rule delete "* ]]; then
    rm -f -- "$firewall_state"
    return 0
  fi
  if [[ "$*" == "postgres flexible-server firewall-rule show "* ]]; then
    [[ -f "$firewall_state" ]] || return 3
    return 0
  fi
  return 0
}

require_config
ensure_active_public_endpoint

grep -Fq 'network public-ip create' "$log_file"
grep -Fq -- '--allocation-method Static' "$log_file"
grep -Fq -- '--dns-name lingosai-prod' "$log_file"
grep -Fq 'network nic ip-config update' "$log_file"
grep -Fq -- '--public-ip-address pip-lingosai-prod' "$log_file"
grep -Fq 'postgres flexible-server firewall-rule create' "$log_file"
grep -Fq -- '--start-ip-address 203.0.113.25 --end-ip-address 203.0.113.25' "$log_file"

remove_active_public_endpoint

[[ ! -e "$ip_state" ]]
[[ ! -e "$firewall_state" ]]
grep -Fq 'postgres flexible-server firewall-rule delete' "$log_file"
grep -Fq -- '--remove publicIpAddress' "$log_file"
grep -Fq 'network public-ip delete' "$log_file"

# A watchdog retry against an already-cold environment must stay successful.
remove_active_public_endpoint

printf 'Azure ephemeral lifecycle guardrails passed.\n'
