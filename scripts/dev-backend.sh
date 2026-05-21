#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../backend"
exec uv run uvicorn app.main:app --reload "$@"
