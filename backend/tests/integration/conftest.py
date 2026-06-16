"""Auto-marks every test collected under tests/integration/ as
@pytest.mark.integration.

Integration tests use a real (in-memory SQLite) DB session and/or a FastAPI
TestClient, wiring multiple modules together with LLM/external collaborators
swapped for Fake*/Stub*. See docs/testing-strategy.md (Phase 2).
"""

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.integration)
