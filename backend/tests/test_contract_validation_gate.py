"""Contract-unified validation gate across all 34 archetypes."""

from __future__ import annotations

import pytest

from app.modules.sessions.contracts import ARCHETYPE_CONTRACTS
from app.modules.sessions.contracts.validation import (
    normalize_task_content,
    validate_and_project_task_content,
)
from tests.test_task_content_validation import _valid_content_for

THE_34 = frozenset(ARCHETYPE_CONTRACTS)


@pytest.mark.parametrize("archetype_id", sorted(THE_34))
def test_valid_fixture_normalizes_and_projects(archetype_id: str) -> None:
    content = _valid_content_for(archetype_id)
    projected = validate_and_project_task_content(archetype_id, content)
    assert projected["archetype_id"] == archetype_id
    assert projected["task_widget"]


@pytest.mark.parametrize("archetype_id", sorted(THE_34))
def test_normalize_dispatcher_handles_archetype(archetype_id: str) -> None:
    content = _valid_content_for(archetype_id)
    normalized = normalize_task_content(archetype_id, content)
    assert normalized.get("archetype_id") == archetype_id
