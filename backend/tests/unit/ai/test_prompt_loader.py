"""Unit tests for the agent prompt loader (`app/ai/agents/prompt_loader.py`).

`render_prompt_template` is the rendering primitive every prompt-driven agent
relies on; its key contract — fill ``{{var}}`` placeholders but never touch raw
JSON braces, and fail loudly on a missing variable — had no direct test.
"""

from __future__ import annotations

import json

import pytest

from app.ai.agents.prompt_loader import load_prompt, render_prompt_template


class TestRenderPromptTemplate:
    def test_fills_simple_placeholder(self):
        assert (
            render_prompt_template("Hello {{name}}!", {"name": "Sam"}) == "Hello Sam!"
        )

    def test_tolerates_whitespace_in_placeholder(self):
        assert render_prompt_template("Hi {{ name }}.", {"name": "Sam"}) == "Hi Sam."

    def test_repeated_and_multiple_placeholders(self):
        out = render_prompt_template("{{a}} and {{b}} and {{a}}", {"a": "x", "b": "y"})
        assert out == "x and y and x"

    def test_missing_variable_raises(self):
        with pytest.raises(ValueError, match="Missing prompt variable"):
            render_prompt_template("Hello {{name}}", {})

    def test_json_braces_are_not_interpreted(self):
        # Single braces (a JSON example in the prompt) must survive untouched;
        # only {{double}} placeholders render.
        template = 'Reply as {"score": 5} about {{topic}}.'
        out = render_prompt_template(template, {"topic": "grammar"})
        assert out == 'Reply as {"score": 5} about grammar.'

    def test_non_string_value_is_json_encoded(self):
        out = render_prompt_template("{{data}}", {"data": {"b": 2, "a": 1}})
        # Stringified as sorted-key JSON, so it parses back to the same object.
        assert json.loads(out) == {"a": 1, "b": 2}
        assert out.index('"a"') < out.index('"b"')  # sort_keys=True

    def test_template_without_placeholders_is_unchanged(self):
        assert render_prompt_template("no vars here", {"unused": 1}) == "no vars here"


class TestLoadPrompt:
    def test_invalid_name_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid prompt name"):
            load_prompt("../etc/passwd")

    def test_missing_prompt_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_prompt("definitely/not/a/real/prompt")
