from __future__ import annotations

from app.modules.curriculum import file_source


def test_curriculum_read_aloud_spec():
    """Verify that the curriculum source spec for Week 1 Day 2 contains the SPEAK_READ_ALOUD spec."""
    day = file_source.get_day_by_id("day_24_01_02")

    assert day.day_id == "day_24_01_02"
    assert "SPEAK_READ_ALOUD" in day.task_archetypes_used

    # SPEAK_READ_ALOUD is the 4th activity (index 3)
    speak_spec = file_source.task_spec_for(day, 3)
    assert speak_spec["topic_override"] == "Read past simple passage aloud"
    assert (
        "connected simple past narrative passage" in speak_spec["instructions_override"]
    )
    assert "50-60 words" in speak_spec["instructions_override"]
    assert "text_to_read_aloud" in speak_spec["widget_requirements"]
