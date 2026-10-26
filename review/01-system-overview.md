# 1. System overview

LingosAI is an AI English-tutoring platform. A learner follows a 24-week or 48-week curriculum. A daily lesson is made of teaching, a task, evaluation, feedback, and progress updates. The browser is a Next.js application; the API is a FastAPI application; PostgreSQL stores durable state and Redis supports short-lived coordination/rate limiting.

## The main request path

```text
Browser page
  -> frontend/lib/*-api.ts or WebSocket client
  -> FastAPI route
  -> service (business rules and transaction boundary)
  -> repository (database queries)
  -> PostgreSQL
  -> typed response/event
  -> React widget and Zustand/TanStack Query state
```

For AI-backed work, the service injects an agent/collaborator. The collaborator uses a prompt plus an LLM, optionally retrieves learner memory from Pinecone, and returns validated structured data. The database write still belongs to the domain service. This separation prevents an LLM graph from silently owning product state.

## Three kinds of truth

- Curriculum truth: authored source data and/or seeded database rows decide which activities exist and their order.
- Contract truth: the session archetype registry connects an activity kind to its task payload, agents, evaluation, feedback, projection, and frontend widget.
- Score truth: `backend/app/scoring/` is deterministic math. It does not call an LLM or the database.

## A useful mental model

The frontend is the presentation and interaction layer. The API is the application boundary. Feature modules own business rules. Repositories own ORM queries. The AI layer supplies probabilistic content and judgments behind interfaces. Scoring and contracts turn that probabilistic output into controlled product behavior.
