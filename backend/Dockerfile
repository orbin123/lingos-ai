# syntax=docker/dockerfile:1
#
# LingosAI backend — multi-stage, uv-based, non-root, slim runtime.
#
# Stage 1 (builder) resolves the locked dependency set into a self-contained
# virtualenv; stage 2 (runtime) ships only that venv + the app code, with no
# build toolchain and a non-root user. Base images are pinned by index digest
# so the build is reproducible across architectures (CI amd64 / local arm64).
#
# Migrations are NOT run here — they run as a separate one-off task so N tasks
# don't race `alembic upgrade head` (Phase 1.13 policy; see docs/RUNBOOK.md).

# ---------------------------------------------------------------------------
# Stage 1 — builder
# ---------------------------------------------------------------------------
# ghcr.io/astral-sh/uv:python3.11-bookworm-slim
FROM ghcr.io/astral-sh/uv@sha256:4f5d923c9dcea037f57bda425dd209f3ec643da2f0b74227f68d09dab0b3bb36 AS builder

# Compile to .pyc at install time (faster cold start); copy rather than hardlink
# (the venv is copied across a stage boundary, so links would dangle).
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Dependency layer first: only pyproject + lockfile, so editing app code does
# not bust the (slow) dependency install cache. --no-install-project installs
# only third-party deps; --no-dev excludes the test/lint toolchain.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Now the application code. uv.lock is the source of truth; --frozen fails if it
# is stale relative to pyproject.toml.
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY scripts ./scripts
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ---------------------------------------------------------------------------
# Stage 2 — runtime
# ---------------------------------------------------------------------------
# python:3.11-slim-bookworm
FROM python@sha256:e2d3af735aff6eeee600b1933bedd99da6645fedf572cc12ef4cc1331f2ceebe AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Non-root runtime user (no shell, no home). Owns /app so the app can write its
# media _cache dirs under app/ai/** when running locally without S3 (Phase 3
# replaces local disk with S3BlobStorage).
RUN groupadd --system --gid 10001 appgroup \
    && useradd --system --uid 10001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Bring over the resolved venv and the app code from the builder.
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app/app /app/app
COPY --from=builder --chown=appuser:appgroup /app/alembic /app/alembic
COPY --from=builder --chown=appuser:appgroup /app/alembic.ini /app/alembic.ini
COPY --from=builder --chown=appuser:appgroup /app/scripts /app/scripts

USER appuser

EXPOSE 8000

# Production process model: gunicorn supervising Uvicorn workers (graceful
# restarts, worker supervision, request timeouts). Mirrors
# backend/scripts/start-prod.sh.
#
# WEB_CONCURRENCY defaults to 1. Multi-worker is correctness-safe (the B4
# double-scoring race is guarded by the session_scorecards unique constraint,
# not an in-memory set) — but scale by TASK COUNT on Fargate first (smaller
# tasks, granular ALB health checks); raise workers per task only when one
# worker per task is the bottleneck.
CMD ["sh", "-c", "exec gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers ${WEB_CONCURRENCY:-1} \
  --bind 0.0.0.0:${PORT:-8000} \
  --timeout 120 \
  --graceful-timeout 30 \
  --access-logfile - \
  --error-logfile -"]
