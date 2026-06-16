"""Regenerate ``backend/openapi.json`` from the live FastAPI app.

The committed ``openapi.json`` is the API contract snapshot. CI (contract.yml)
and ``tests/unit/platform/test_openapi_snapshot.py`` regenerate it and fail on
drift, so a response-model change that isn't reflected in the snapshot breaks
the build with a clear "run scripts/export_openapi.py" hint.

Run from ``backend/``:  ``uv run python scripts/export_openapi.py``

Determinism: ``sort_keys=True`` neutralises pydantic-v2 property-ordering
jitter; FastAPI/pydantic versions are pinned by ``uv.lock`` so dev and CI emit
identical specs.
"""

import json
import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Mirror tests/conftest.py: app.main reads settings at import time, so these
# MUST be set before `from app.main import app`. setdefault keeps any real env
# (local .env) from being clobbered while guaranteeing values exist in CI.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("LANGCHAIN_API_KEY", "test-langchain-key")
os.environ.setdefault("PINECONE_API_KEY", "test-pinecone-key")
os.environ.setdefault("STRICT_CONTRACTS", "true")
os.environ.setdefault("AI_RATE_LIMIT_ENABLED", "false")

OUTPUT = BACKEND_ROOT / "openapi.json"


def build_spec() -> dict:
    """Return the OpenAPI schema for the app (imported after env is set)."""
    from app.main import app

    return app.openapi()


def serialize(spec: dict) -> str:
    """Deterministic JSON: sorted keys, 2-space indent, trailing newline."""
    return json.dumps(spec, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> None:
    OUTPUT.write_text(serialize(build_spec()), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(BACKEND_ROOT)}")


if __name__ == "__main__":
    main()
