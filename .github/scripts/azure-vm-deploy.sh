#!/usr/bin/env bash

# Runs as root through Azure VM Run Command. Production images are built from
# an exact commit in the public LingosAI repository and retained on the VM's
# free-tier OS disk. This avoids a continuously billed container registry while
# preserving commit-pinned deployments and a local rollback image.

set -Eeuo pipefail
umask 077

readonly MODE="${1:-}"
readonly REQUESTED_SHA="${2:-}"
readonly CONTAINER_NAME="lingosai-backend"
readonly REPOSITORY_ARCHIVE="https://github.com/orbin123/lingos-ai/archive"
readonly STATE_DIR="/var/lib/lingosai"
readonly ENV_FILE="/etc/lingosai/backend.env"
readonly DEPLOYED_IMAGE_FILE="$STATE_DIR/deployed-image"
readonly DEPLOYED_SHA_FILE="$STATE_DIR/deployed-sha"
readonly ROLLBACK_IMAGE_FILE="$STATE_DIR/rollback-image"
readonly MAINTENANCE_FILE="$STATE_DIR/maintenance"

previous_image=""
deployment_started=0
build_dir=""
built_image_id=""

log() { printf '%s\n' "$*"; }
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

cleanup() {
  if [[ -n "$build_dir" ]]; then
    rm -rf -- "$build_dir"
  fi
}

is_commit_sha() { [[ "$1" =~ ^[a-f0-9]{40}$ ]]; }
is_image_id() { [[ "$1" =~ ^sha256:[a-f0-9]{64}$ ]]; }

require_host_contract() {
  local tool
  for tool in curl docker tar; do
    command -v "$tool" >/dev/null 2>&1 || fail "$tool is required on the VM"
  done

  install -d -m 0755 "$STATE_DIR"
  [[ -f "$ENV_FILE" ]] || fail "$ENV_FILE is missing"
  [[ "$(stat -c '%U:%G' "$ENV_FILE")" == "root:root" ]] || fail "$ENV_FILE must be owned by root"
  local env_mode
  env_mode="$(stat -c '%a' "$ENV_FILE")"
  if ((8#$env_mode > 8#600)); then
    fail "$ENV_FILE must not be more permissive than mode 0600"
  fi
}

build_commit_image() {
  local commit_sha="$1"
  local archive source_root image_id

  is_commit_sha "$commit_sha" || fail "deployment requires a full lowercase Git commit SHA"
  build_dir="$(mktemp -d)"
  archive="$build_dir/source.tar.gz"

  curl \
    --fail \
    --silent \
    --show-error \
    --location \
    --proto '=https' \
    --tlsv1.2 \
    "$REPOSITORY_ARCHIVE/$commit_sha.tar.gz" \
    --output "$archive"
  tar -xzf "$archive" -C "$build_dir"
  source_root="$build_dir/lingos-ai-$commit_sha"
  [[ -f "$source_root/backend/Dockerfile" ]] || fail "commit archive does not contain backend/Dockerfile"

  DOCKER_BUILDKIT=1 docker build \
    --pull \
    --tag "lingosai-backend:git-$commit_sha" \
    --file "$source_root/backend/Dockerfile" \
    "$source_root/backend"

  image_id="$(docker image inspect --format '{{.Id}}' "lingosai-backend:git-$commit_sha")"
  is_image_id "$image_id" || fail "Docker did not return an immutable image ID"
  built_image_id="$image_id"
}

read_recorded_image() {
  local path="$1"
  local image=""
  if [[ -f "$path" ]]; then
    image="$(tr -d '\r\n' <"$path")"
    if is_image_id "$image" && docker image inspect "$image" >/dev/null 2>&1; then
      printf '%s' "$image"
    fi
  fi
}

current_container_image() {
  local image=""
  if docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    image="$(docker container inspect --format '{{.Image}}' "$CONTAINER_NAME")"
    if is_image_id "$image" && docker image inspect "$image" >/dev/null 2>&1; then
      printf '%s' "$image"
    fi
  fi
}

stop_current_container() {
  if docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
    docker stop --time 45 "$CONTAINER_NAME" >/dev/null
    docker rm "$CONTAINER_NAME" >/dev/null
  fi
}

start_container() {
  local image="$1"
  is_image_id "$image" || fail "refusing a mutable or invalid local image reference"
  docker image inspect "$image" >/dev/null 2>&1 || fail "local image $image is missing"

  docker run --detach \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    --network host \
    --env-file "$ENV_FILE" \
    --env WEB_CONCURRENCY=1 \
    --env PORT=8000 \
    --memory 768m \
    --memory-swap 1024m \
    --log-driver json-file \
    --log-opt max-size=10m \
    --log-opt max-file=3 \
    "$image" >/dev/null
}

wait_for_local_health() {
  local attempt
  for attempt in $(seq 1 30); do
    if curl --fail --silent --show-error --max-time 5 \
      http://127.0.0.1:8000/health/live >/dev/null \
      && curl --fail --silent --show-error --max-time 5 \
        http://127.0.0.1:8000/health/ready >/dev/null; then
      return 0
    fi
    log "Local health attempt $attempt/30 failed"
    sleep 4
  done
  return 1
}

run_one_off() {
  local image="$1"
  shift
  docker run --rm \
    --network host \
    --env-file "$ENV_FILE" \
    --env WEB_CONCURRENCY=1 \
    "$image" "$@"
}

restore_previous_after_failure() {
  local original_status="$?"
  trap - ERR

  if ((deployment_started == 0)); then
    exit "$original_status"
  fi

  log "Deployment failed; attempting local application rollback. Database migrations are not reverted."
  stop_current_container || log "Failed to remove the unhealthy container before rollback"

  if [[ -n "$previous_image" ]] \
    && docker image inspect "$previous_image" >/dev/null 2>&1 \
    && start_container "$previous_image" \
    && wait_for_local_health; then
    printf '%s\n' "$previous_image" >"$DEPLOYED_IMAGE_FILE"
    rm -f "$MAINTENANCE_FILE"
    log "Previous local image restored: $previous_image"
  else
    log "No healthy local rollback image is available; maintenance mode remains active."
  fi

  exit "$original_status"
}

deploy() {
  local requested_image
  build_commit_image "$REQUESTED_SHA"
  requested_image="$built_image_id"

  previous_image="$(current_container_image)"
  if [[ -z "$previous_image" ]]; then
    previous_image="$(read_recorded_image "$DEPLOYED_IMAGE_FILE")"
  fi
  if [[ -n "$previous_image" && "$previous_image" != "$requested_image" ]]; then
    printf '%s\n' "$previous_image" >"$ROLLBACK_IMAGE_FILE"
  fi

  touch "$MAINTENANCE_FILE"
  deployment_started=1
  trap restore_previous_after_failure ERR

  stop_current_container

  # Migrations are forward-only. The old local image is restored on
  # application failure, but schema changes are never reversed automatically.
  run_one_off "$requested_image" alembic upgrade head
  run_one_off "$requested_image" \
    sh -c 'python -m scripts.seed_curriculum && python -m scripts.seed_ielts_challenge && python -m scripts.seed_a2z_challenge'

  start_container "$requested_image"
  wait_for_local_health

  printf '%s\n' "$requested_image" >"$DEPLOYED_IMAGE_FILE"
  printf '%s\n' "$REQUESTED_SHA" >"$DEPLOYED_SHA_FILE"
  rm -f "$MAINTENANCE_FILE"
  trap - ERR
  log "Deployment healthy for commit $REQUESTED_SHA at local image $requested_image"
  printf 'deployed_image=%s\n' "$requested_image"
}

rollback() {
  local rollback_image current_image
  rollback_image="$(read_recorded_image "$ROLLBACK_IMAGE_FILE")"
  [[ -n "$rollback_image" ]] || fail "no local rollback image is recorded"

  current_image="$(current_container_image)"
  if [[ -z "$current_image" ]]; then
    current_image="$(read_recorded_image "$DEPLOYED_IMAGE_FILE")"
  fi

  touch "$MAINTENANCE_FILE"
  stop_current_container
  start_container "$rollback_image"
  if ! wait_for_local_health; then
    fail "rollback image did not become healthy; maintenance mode remains active"
  fi

  printf '%s\n' "$rollback_image" >"$DEPLOYED_IMAGE_FILE"
  if [[ -n "$current_image" && "$current_image" != "$rollback_image" ]]; then
    printf '%s\n' "$current_image" >"$ROLLBACK_IMAGE_FILE"
  fi
  rm -f "$MAINTENANCE_FILE"
  log "Rollback healthy at local image: $rollback_image"
}

main() {
  require_host_contract
  trap cleanup EXIT

  case "$MODE" in
    deploy)
      deploy
      ;;
    rollback)
      rollback
      ;;
    *)
      fail "usage: $0 {deploy <commit-sha>|rollback}"
      ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main
fi
