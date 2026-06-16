"""Auto-marks every test collected under tests/unit/ as @pytest.mark.unit.

Unit tests are fast and isolated: no DB, no HTTP, no network. This lets CI
select by marker (`-m unit`) or by path. See docs/testing-strategy.md (Phase 2).
"""

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.unit)
