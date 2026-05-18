"""Small filesystem prompt loader for agent prompt templates."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


_PROMPT_ROOT = Path(__file__).resolve().parent / "prompts"
_PROMPT_NAME_RE = re.compile(r"^[A-Za-z0-9_/-]+$")
_PLACEHOLDER_RE = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_]*)\s*}}")


def load_prompt(name: str) -> str:
    """Load a prompt by slash-delimited name, for example ``ielts/generator``."""
    if not _PROMPT_NAME_RE.fullmatch(name):
        raise ValueError(f"Invalid prompt name: {name!r}")

    root = _PROMPT_ROOT.resolve()
    path = (root / f"{name}.md").resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Prompt path escapes prompt root: {name!r}")
    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {name!r}")
    return path.read_text(encoding="utf-8")


def render_prompt_template(template: str, variables: dict[str, Any]) -> str:
    """Render ``{{variable}}`` placeholders without interpreting JSON braces."""

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in variables:
            raise ValueError(f"Missing prompt variable: {key!r}")
        return _stringify_prompt_value(variables[key])

    return _PLACEHOLDER_RE.sub(replace, template)


def _stringify_prompt_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True, default=str)
