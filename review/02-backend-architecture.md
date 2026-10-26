# 2. Backend architecture

The backend is Python 3.11+, FastAPI, SQLAlchemy 2, PostgreSQL, Alembic, Pydantic, and `uv`. `backend/app/main.py` creates the application, middleware, static mounts, exception handling, health routes, and router registration.

## Layering rule

Most modules follow:

```text
routes.py -> schemas.py -> service.py -> repository.py -> models.py
```

Routes are thin HTTP adapters. Schemas validate input/output. Services contain business decisions and commit at logical boundaries. Repositories are the only feature layer that directly queries SQLAlchemy. Models describe tables and relationships. Domain exceptions are translated to HTTP errors at the route boundary.

## Cross-cutting areas

- `app/core/`: settings, database engine/session, security, logging, rate limits, headers, upload limits, and shared ORM mixins.
- `app/models.py`: imports every ORM model so SQLAlchemy relationships and Alembic see the full registry.
- `app/modules/`: product features such as auth, curriculum, sessions, progress, challenges, feedback memory, subscriptions, and admin.
- `app/ai/`: provider interfaces and AI orchestration.
- `app/scoring/`: pure deterministic scoring.
- `app/tasks/schemas/`: typed payload contracts for activity widgets and structured LLM output.
- `app/payments/` and `app/email/`: provider boundaries with replaceable clients.

## Session distinction

`modules/sessions` is the authoritative daily-session engine: start, next activity, submit, complete, scorecard, evaluation, feedback, and points. `modules/learning_session` is the chat/WebSocket presentation stream. The chat orchestrator turns existing deterministic session data into events; it does not invent lesson order or own evaluation writes.
