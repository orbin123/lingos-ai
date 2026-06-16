"""Guards the committed OpenAPI snapshot against silent drift.

If a route or response model changes without regenerating the snapshot, this
fails with a fix hint. The CI `contract` job does the same check via
`git diff --exit-code openapi.json`; this test gives the same signal locally
inside the unit suite. Env is provided by the root conftest.py (it sets the
dummy vars before app.* is imported).
"""

from pathlib import Path

from scripts.export_openapi import build_spec, serialize

SNAPSHOT = Path(__file__).resolve().parents[3] / "openapi.json"

_REGEN_HINT = "run: uv run python scripts/export_openapi.py (and commit openapi.json)"


def test_openapi_snapshot_is_current():
    assert SNAPSHOT.exists(), f"openapi.json missing — {_REGEN_HINT}"
    current = serialize(build_spec())
    committed = SNAPSHOT.read_text(encoding="utf-8")
    assert current == committed, f"OpenAPI schema drift — {_REGEN_HINT}"
