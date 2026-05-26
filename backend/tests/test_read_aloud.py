from __future__ import annotations

import pytest
from app.modules.sessions.task_generator import build_past_read_aloud_content
from app.modules.curriculum import file_source


def test_fallback_read_aloud_content():
    """Verify that build_past_read_aloud_content generates a 50-60 word simple past narrative passage."""
    payload = build_past_read_aloud_content("Simple Past Tense")
    assert payload["task_intro"] == "Read the passage above out loud."
    assert "Liam" in payload["text_to_read_aloud"]
    
    word_count = len(payload["text_to_read_aloud"].split())
    assert 50 <= word_count <= 60, f"Expected word count between 50 and 60, got {word_count}"
    assert payload["speaking_duration_seconds"] == 45
    assert "Pronounce regular past" in payload["grammar_rule_to_practice"]
    assert "walked" in payload["grammar_rule_to_practice"]
    assert "played" in payload["grammar_rule_to_practice"]


def test_curriculum_read_aloud_spec():
    """Verify that the curriculum source spec for Week 1 Day 2 contains the SPEAK_READ_ALOUD spec."""
    day = file_source.get_day_by_id("day_24_01_02")
    
    assert day.day_id == "day_24_01_02"
    assert "SPEAK_READ_ALOUD" in day.task_archetypes_used
    
    # SPEAK_READ_ALOUD is the 4th activity (index 3)
    speak_spec = file_source.task_spec_for(day, 3)
    assert speak_spec["topic_override"] == "Read past simple passage aloud"
    assert "connected simple past narrative passage" in speak_spec["instructions_override"]
    assert "50-60 words" in speak_spec["instructions_override"]
    assert "text_to_read_aloud" in speak_spec["widget_requirements"]
