"""Tests for the objective-driven curriculum loader.

After the refactor, every topic JSON entry must carry communication_goal
and language_focus. The legacy `topic_name` field is gone. The loader
should raise a KeyError at startup if it encounters a legacy entry.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.modules.curriculum.topics import (
    CourseTopic,
    _load_topics,
    get_course_topic,
)


@pytest.mark.parametrize(
    "duration_weeks,expected_count",
    [(24, 168), (48, 336)],
)
def test_curriculum_files_have_new_schema(
    duration_weeks: int, expected_count: int
) -> None:
    """Every entry in both course files uses the new objective-driven shape."""
    _load_topics.cache_clear()
    topics = _load_topics(duration_weeks)
    assert len(topics) == expected_count

    for entry in topics.values():
        assert isinstance(entry, CourseTopic)
        assert entry.communication_goal, entry
        assert entry.language_focus, entry
        # Legacy field must be gone.
        assert not hasattr(entry, "topic_name")


def test_course_topic_display_label_concatenates_goal_and_focus() -> None:
    topic = CourseTopic(
        week=1, day=1, topic_id="1:1",
        sub_skill="grammar", sub_level=1,
        communication_goal="introduce yourself in everyday situations",
        language_focus="present simple — affirmative",
    )
    label = topic.display_label
    assert "introduce yourself" in label
    assert "present simple" in label
    assert " — " in label


def test_loader_rejects_legacy_topic_name_schema(tmp_path: Path, monkeypatch) -> None:
    """A JSON file that still uses topic_name must surface a clear KeyError.

    This guards against deploying a stale topics_*w.json file alongside
    the new loader.
    """
    legacy_payload = {
        "plan": "legacy-test",
        "duration_weeks": 99,
        "total_topics": 1,
        "topics": [
            {
                "week": 1,
                "day": 1,
                "topic_id": "1:1",
                "sub_skill": "grammar",
                "sub_level": 1,
                "topic_name": "Old Family & Home",
            }
        ],
    }
    legacy_file = tmp_path / "topics_99w.json"
    legacy_file.write_text(json.dumps(legacy_payload), encoding="utf-8")

    monkeypatch.setattr(
        "app.modules.curriculum.topics._COURSE_DATA_DIR", tmp_path
    )
    _load_topics.cache_clear()
    with pytest.raises(KeyError):
        _load_topics(99)


def test_get_course_topic_returns_none_for_missing_day() -> None:
    assert get_course_topic(duration_weeks=24, week=9999, day=1) is None


def test_get_course_topic_returns_populated_entry_for_known_day() -> None:
    topic = get_course_topic(duration_weeks=24, week=1, day=1)
    assert topic is not None
    assert topic.sub_skill == "grammar"
    assert topic.communication_goal
    assert topic.language_focus
