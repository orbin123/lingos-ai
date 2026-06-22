"""Pydantic models bound to OpenAI structured output (``additionalProperties: false``).

Post-LLM validation uses the permissive widget models in ``task_schemas`` (``extra="allow"``).
These schemas are only passed to ``ILLMClient.generate_structured``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.tasks.schemas.task_schemas import BlankItem, FillInBlanksTask


class BlankItemLLM(BlankItem):
    """OpenAI-compatible cloze item; rejects unknown keys."""

    model_config = ConfigDict(extra="forbid")


class FillInBlanksTaskLLM(FillInBlanksTask):
    """OpenAI-compatible fill-in-blanks payload sent as ``response_format``."""

    model_config = ConfigDict(extra="forbid")

    # Narrows the base `list[BlankItem]` to the extra="forbid" item model; lists
    # are invariant so mypy flags the override even though it's intentional.
    # Floor relaxed to 1: the prompt targets 4-5 blanks, but accepting fewer
    # renders fine and avoids a hard failure when the LLM under-produces.
    items: list[BlankItemLLM] = Field(  # type: ignore[assignment]
        default_factory=list, min_length=1, max_length=5
    )


def assert_openai_structured_schema(model: type[BaseModel]) -> None:
    """Every object in the JSON schema must declare ``additionalProperties: false``."""
    schema = model.model_json_schema()
    defs = schema.get("$defs", {})

    def resolve(ref: str) -> dict:
        name = ref.rsplit("/", 1)[-1]
        return defs[name]

    def check_object(obj: dict, path: str) -> None:
        if obj.get("type") != "object":
            return
        assert obj.get("additionalProperties") is False, (
            f"{path}: additionalProperties must be false for OpenAI structured output"
        )
        for prop_name, prop_schema in obj.get("properties", {}).items():
            walk(prop_schema, f"{path}.{prop_name}")

    def walk(node: dict, path: str) -> None:
        if not isinstance(node, dict):
            return
        if "$ref" in node:
            check_object(resolve(node["$ref"]), path)
            return
        if "anyOf" in node:
            for i, branch in enumerate(node["anyOf"]):
                walk(branch, f"{path}[anyOf:{i}]")
            return
        if node.get("type") == "object":
            check_object(node, path)
            return
        if node.get("type") == "array":
            walk(node.get("items", {}), f"{path}[]")

    check_object(schema, model.__name__)
    for def_name, def_schema in defs.items():
        if def_schema.get("type") == "object":
            check_object(def_schema, f"{model.__name__}.$defs.{def_name}")
