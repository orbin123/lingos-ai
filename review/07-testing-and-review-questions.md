# 7. Testing and review questions

## Test layers

- Backend unit tests isolate services, planners, agents, scoring, and contracts with stubs.
- Backend integration tests exercise real database/test-client boundaries.
- Migration checks replay Alembic against PostgreSQL.
- Frontend Vitest tests components, hooks, stores, and API interactions with browser-like mocks.
- Type/lint/build checks catch contract and bundling errors.

## Questions to answer in a review

1. Where is the transaction boundary for submitting an activity? `SessionService.submit_activity`.
2. Which code decides activity order? Curriculum blueprint plus V2 session/planner, not the chat UI.
3. Where is score math? `app/scoring/`, pure functions, no LLM/DB/I/O.
4. What connects a backend activity to a frontend widget? Archetype contract, widget mapping, task schemas, adapter, and renderer.
5. Why use embeddings? To retrieve semantically relevant learner feedback memory for later prompts.
6. Why LangGraph? To make multi-step AI state transitions explicit and testable.
7. What happens if an LLM returns malformed output? Structured output/Pydantic validation and domain error handling prevent it from becoming unchecked product state.
8. Why import all models in `app/models.py`? To populate SQLAlchemy's registry for relationships and Alembic discovery.
9. How is a repeated submission prevented from awarding points twice? Replay guards/unique constraints and score-writing rules.
10. How does a 401 affect the browser? The shared Axios client clears auth and redirects for non-auth endpoints.
