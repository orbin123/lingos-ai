"""Task payload schemas for LingosAI.

The active sessions flow validates concrete widget payloads here. The older
large template registry is intentionally not imported because those modules are
not present in this repo snapshot.
"""

from app.tasks.schemas.base import (
    Activity,
    DifficultyTier,
    GeneratedTaskBase,
    ScoringMethod,
    SubSkill,
    TaskTemplate,
    difficulty_tier_for_sublevel,
)
from app.tasks.schemas.task_schemas import BlankItem, FillInBlanksTask

ALL_TEMPLATES: list[TaskTemplate] = []
ALL_OUTPUT_MODELS: dict[str, type[GeneratedTaskBase]] = {
    "FillInBlanksTask": FillInBlanksTask,
}


def get_templates_for(
    sub_skill: SubSkill,
    activity: Activity | None = None,
) -> list[TaskTemplate]:
    return [
        template
        for template in ALL_TEMPLATES
        if template.sub_skill == sub_skill
        and (activity is None or template.activity == activity)
    ]


def get_template_by_id(template_id: str) -> TaskTemplate | None:
    return next(
        (template for template in ALL_TEMPLATES if template.template_id == template_id),
        None,
    )


def get_output_model(model_name: str) -> type[GeneratedTaskBase] | None:
    return ALL_OUTPUT_MODELS.get(model_name)


__all__ = [
    "Activity",
    "DifficultyTier",
    "GeneratedTaskBase",
    "ScoringMethod",
    "SubSkill",
    "TaskTemplate",
    "difficulty_tier_for_sublevel",
    "BlankItem",
    "FillInBlanksTask",
    "ALL_TEMPLATES",
    "ALL_OUTPUT_MODELS",
    "get_templates_for",
    "get_template_by_id",
    "get_output_model",
]
