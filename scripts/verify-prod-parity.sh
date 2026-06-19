#!/usr/bin/env bash
#
# verify-prod-parity.sh — read-only production feature-parity verifier (G4).
#
# Proves the CLI-checkable rows of the POLISHED_PRODUCTION_PLAN §G4 matrix
# against LIVE prod: API health, frontend, ECS service, media S3 + CloudFront,
# and the env/secret wiring in the running task definition. It makes **no
# mutations** — only `curl` GET/HEAD and read-only `aws describe/list` calls.
#
# The browser- and purchase-driven rows (Google OAuth loop, Razorpay test
# purchase, WebSocket session, pronunciation recording, RAG repeat-weakness)
# CANNOT be proven from a shell — see docs/PROD_PARITY_RUNBOOK.md for the exact
# founder steps and evidence to capture for those.
#
# Usage:
#   ./scripts/verify-prod-parity.sh                 # verify prod (defaults)
#   ./scripts/verify-prod-parity.sh | tee parity.log
#
# Overridable via env vars (defaults target production):
#   API_URL, WWW_URL, AWS_REGION, ECS_CLUSTER, ECS_SERVICE, ECS_TASK_FAMILY
#
# Requirements: bash, curl, jq, and AWS CLI authenticated for the prod account
# (the read-only `lingos-ai-cli` user is sufficient).
#
# Exit code: 0 if every [AUTO] check PASSes; 1 if any FAILs. WARNs (e.g. an
# empty media bucket awaiting app traffic) do NOT fail the run.

set -uo pipefail

# ---------------------------------------------------------------------------
# Config (prod defaults; override via env).
# ---------------------------------------------------------------------------
API_URL="${API_URL:-https://api.lingosai.com}"
WWW_URL="${WWW_URL:-https://www.lingosai.com}"
AWS_REGION="${AWS_REGION:-us-east-1}"
ECS_CLUSTER="${ECS_CLUSTER:-lingosai-production}"
ECS_SERVICE="${ECS_SERVICE:-lingosai-production-backend}"
ECS_TASK_FAMILY="${ECS_TASK_FAMILY:-lingosai-production-backend}"

# ---------------------------------------------------------------------------
# Tiny check framework.
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

# No -f: we WANT the real status code for non-2xx (with -f, curl errors and the
# `|| echo 000` fallback would concatenate, e.g. "403000").
http_code() { curl -sSL -o /dev/null -w '%{http_code}' "$1" 2>/dev/null || echo "000"; }

# ---------------------------------------------------------------------------
require curl jq aws

echo "LingosAI — prod feature-parity verifier (read-only)"
echo "  $(date -u '+%Y-%m-%dT%H:%M:%SZ')  region=$AWS_REGION"
echo "  api=$API_URL  www=$WWW_URL"
echo

# Fail fast if AWS creds are missing/expired.
if ! ACCOUNT=$(aws sts get-caller-identity --query Account --output text 2>/dev/null); then
  echo "ERROR: AWS CLI is not authenticated. Run with valid prod credentials." >&2
  exit 2
fi
echo "  aws account=$ACCOUNT"
echo

# ===========================================================================
echo "[1] API + frontend reachability"
# ---------------------------------------------------------------------------
code=$(http_code "$API_URL/health")
[ "$code" = "200" ] && pass "api /health" "200 (liveness)" || fail "api /health" "expected 200, got $code"

ready_body=$(curl -fsS "$API_URL/health/ready" 2>/dev/null || echo '{}')
db=$(echo "$ready_body"     | jq -r '.checks.database // "?"' 2>/dev/null)
redis=$(echo "$ready_body"  | jq -r '.checks.redis // "?"'    2>/dev/null)
if [ "$db" = "ok" ] && [ "$redis" = "ok" ]; then
  pass "api /health/ready" "200 (database=ok, redis=ok)"
else
  fail "api /health/ready" "database=$db redis=$redis (body: $ready_body)"
fi

code=$(http_code "$WWW_URL")
[ "$code" = "200" ] && pass "frontend www" "200" || fail "frontend www" "expected 200, got $code"

# ===========================================================================
echo
echo "[2] ECS backend service"
# ---------------------------------------------------------------------------
svc=$(aws ecs describe-services --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE" \
  --region "$AWS_REGION" --query 'services[0].{r:runningCount,d:desiredCount,s:status,td:taskDefinition}' \
  --output json 2>/dev/null || echo '{}')
running=$(echo "$svc"  | jq -r '.r // "?"')
desired=$(echo "$svc"  | jq -r '.d // "?"')
status=$(echo "$svc"   | jq -r '.s // "?"')
td=$(echo "$svc"       | jq -r '.td // "?"')
if [ "$status" = "ACTIVE" ] && [ "$running" = "$desired" ] && [ "$running" != "0" ] && [ "$running" != "?" ]; then
  pass "ecs service" "ACTIVE, $running/$desired running (${td##*/})"
else
  fail "ecs service" "status=$status running=$running desired=$desired"
fi

# ===========================================================================
echo
echo "[3] Task-def env + secret wiring (feature parity is env-driven)"
# ---------------------------------------------------------------------------
td_json=$(aws ecs describe-task-definition --task-definition "$ECS_TASK_FAMILY" \
  --region "$AWS_REGION" --query 'taskDefinition.containerDefinitions[0]' \
  --output json 2>/dev/null || echo '{}')

get_env() { echo "$td_json" | jq -r --arg k "$1" '(.environment[]? | select(.name==$k) | .value) // ""'; }

storage=$(get_env STORAGE_BACKEND)
email=$(get_env EMAIL_PROVIDER)
bucket=$(get_env MEDIA_S3_BUCKET)
priv_bucket=$(get_env MEDIA_PRIVATE_S3_BUCKET)
cdn=$(get_env MEDIA_CDN_URL)
debug=$(get_env DEBUG)
otp_bypass=$(get_env DEV_OTP_BYPASS)

[ "$storage" = "s3" ] && pass "STORAGE_BACKEND" "s3" || fail "STORAGE_BACKEND" "expected s3, got '$storage'"
[ -n "$email" ]  && pass "EMAIL_PROVIDER"  "$email"  || fail "EMAIL_PROVIDER"  "unset"
[ -n "$bucket" ] && pass "MEDIA_S3_BUCKET" "$bucket" || fail "MEDIA_S3_BUCKET" "unset"
[ -n "$cdn" ]    && pass "MEDIA_CDN_URL"   "$cdn"    || fail "MEDIA_CDN_URL"   "unset"

# Prod-safety flags must be off (cross-checks G7's prod guard from the outside).
[ "$debug" = "false" ]      && pass "DEBUG"          "false" || fail "DEBUG"          "expected false, got '$debug'"
[ "$otp_bypass" = "false" ] && pass "DEV_OTP_BYPASS" "false" || fail "DEV_OTP_BYPASS" "expected false, got '$otp_bypass'"

# Secret wiring: assert the feature secrets are referenced by the task-def
# (names only — values are never read).
EXPECTED_SECRETS=(DATABASE_URL REDIS_URL JWT_SECRET OPENAI_API_KEY PINECONE_API_KEY \
  AZURE_SPEECH_KEY DEEPGRAM_API_KEY GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET \
  RAZORPAY_KEY_ID RAZORPAY_KEY_SECRET RAZORPAY_WEBHOOK_SECRET SENTRY_DSN)
present_secrets=$(echo "$td_json" | jq -r '[.secrets[]?.name] | join(" ")')
missing=()
for s in "${EXPECTED_SECRETS[@]}"; do
  case " $present_secrets " in *" $s "*) : ;; *) missing+=("$s") ;; esac
done
if [ ${#missing[@]} -eq 0 ]; then
  pass "secret wiring" "all ${#EXPECTED_SECRETS[@]} feature secrets referenced"
else
  fail "secret wiring" "missing: ${missing[*]}"
fi

# ===========================================================================
echo
echo "[4] Media: S3 buckets + CloudFront serve path"
# ---------------------------------------------------------------------------
if aws s3api head-bucket --bucket "$bucket" --region "$AWS_REGION" >/dev/null 2>&1; then
  pass "media bucket" "$bucket exists"
else
  fail "media bucket" "$bucket not reachable"
fi
if [ -n "$priv_bucket" ] && aws s3api head-bucket --bucket "$priv_bucket" --region "$AWS_REGION" >/dev/null 2>&1; then
  pass "private media bucket" "$priv_bucket exists"
else
  warn "private media bucket" "${priv_bucket:-unset} not reachable"
fi

# CloudFront domain must resolve/respond (any HTTP code = reachable; 000 = DNS/conn fail).
if [ -n "$cdn" ]; then
  cdn_code=$(curl -sS -o /dev/null -w '%{http_code}' "$cdn/" 2>/dev/null || echo "000")
  if [ "$cdn_code" = "000" ]; then
    fail "cloudfront reachable" "$cdn did not respond (DNS/conn fail)"
  else
    pass "cloudfront reachable" "$cdn responded ($cdn_code)"
  fi
fi

# Media write→serve proof: only possible once app traffic has generated a TTS/
# image object. If the bucket has objects, HEAD the first via CloudFront.
first_key=$(aws s3api list-objects-v2 --bucket "$bucket" --max-items 1 \
  --region "$AWS_REGION" --query 'Contents[0].Key' --output text 2>/dev/null || echo "None")
if [ "$first_key" = "None" ] || [ -z "$first_key" ]; then
  warn "media write→serve" "bucket empty — trigger a TTS/image in a live session, then re-run (see RUNBOOK row 5)"
elif [ -n "$cdn" ]; then
  obj_code=$(curl -sS -o /dev/null -w '%{http_code}' "$cdn/$first_key" 2>/dev/null || echo "000")
  [ "$obj_code" = "200" ] && pass "media write→serve" "$first_key serves 200 via CDN" \
    || fail "media write→serve" "$first_key returned $obj_code via $cdn"
fi

# ===========================================================================
echo
echo "============================================================"
echo "Summary:  PASS=$PASS  FAIL=$FAIL  WARN=$WARN"
echo "  [AUTO] rows verified above. The browser/purchase rows"
echo "  (OAuth, Razorpay, WebSocket session, pronunciation, RAG)"
echo "  are founder-driven — see docs/PROD_PARITY_RUNBOOK.md."
echo "============================================================"

[ "$FAIL" -eq 0 ]
