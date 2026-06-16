"""Every archetype: eval-prompt assembly + generator output → contract projection.

Split out of the former monolithic test_llm_session_agents.py.
"""

from __future__ import annotations


import pytest

from app.ai.sessions.llm_task_generator import (
    LLMTaskGenerator,
)
from app.modules.sessions.contracts.registry import get_contract
from app.scoring import ARCHETYPE_REGISTRY, get_archetype
from tests.fixtures.task_content import THE_34

# Canonical fakes (Phase 3 — moved out of this file into tests/mocks/).
from tests.mocks.llm import FakeLLMClient
from tests.mocks.tts import FakeTTSService
from tests.unit.ai._llm_agent_support import _canned_llm_output_for


class TestEveryArchetypeRoundTrips:
    """Every archetype in the registry must produce a valid eval prompt
    without raising. Catches bad rubric or weight_map data."""

    @pytest.mark.parametrize(
        "spec",
        list(ARCHETYPE_REGISTRY.values()),
        ids=lambda s: s.archetype_id,
    )
    def test_eval_prompt_assembles(self, spec):
        from app.ai.sessions.prompts import build_eval_user_prompt

        prompt = build_eval_user_prompt(
            archetype=spec,
            task_content={"topic": "x"},
            user_response={"answer": "y"},
        )
        assert spec.archetype_id in prompt
        assert "rubric criteria" in prompt.lower()


_LISTENING_ARCHETYPES = frozenset(
    aid for aid in THE_34 if get_archetype(aid).core_activity == "listen"
)


class TestGeneratorOutputProjectsThroughContract:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("archetype_id", sorted(THE_34))
    async def test_generated_content_projects_onto_contract(
        self, archetype_id: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from app.modules.sessions.contracts import project_task_payload

        if archetype_id in _LISTENING_ARCHETYPES:
            from app.ai import tts as tts_module

            monkeypatch.setattr(
                tts_module, "get_default_tts_service", lambda: FakeTTSService()
            )

        spec = get_archetype(archetype_id)
        agent = LLMTaskGenerator(FakeLLMClient([_canned_llm_output_for(archetype_id)]))

        generated = await agent.generate(
            archetype=spec,
            day_topic=spec.name,
            explanation_brief="Cycle-1 practice task.",
            cefr_level="A1",
            sub_level=1,
        )

        assert generated.content["phase"] == "live"

        payload = project_task_payload(
            archetype_id,
            dict(generated.content),
            activity_id="attempt-1",
            sequence=1,
        )
        model = get_contract(archetype_id).task_payload.model_validate(payload)
        assert model.archetype_id == archetype_id
        assert model.task_widget == get_contract(archetype_id).task_widget
