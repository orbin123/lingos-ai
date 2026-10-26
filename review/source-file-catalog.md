# Source-file catalog and “what each file means” guide

The real repository has many small files, so this catalog groups the individual files by their responsibility. When studying a source file, first identify its suffix and then use the matching question below. This is more useful than copying code into the review mirror.

## Backend file meanings

| Source pattern | What to explain when reviewing it |
| --- | --- |
| `routes.py` / `router.py` | HTTP/WebSocket path, dependencies, status codes, and exception translation |
| `service.py` | Business rules, collaborator injection, transaction/commit boundary |
| `repository.py` | SQLAlchemy query, filters, ordering, locking, and persistence behavior |
| `models.py` | Table columns, keys, relationships, constraints, and ownership |
| `schemas.py` | API input/output validation and serialization contract |
| `exceptions.py` | Domain failure and where it becomes an HTTP error |
| `interface.py` | Provider-independent capability contract used for dependency inversion |
| `*_client.py` | Vendor SDK call, timeout/error translation, and configuration use |
| `factory.py` | Production implementation assembly and test substitution point |
| `prompts/*.md` | Model role, required context, rubric, output format, and safety instructions |
| `graph/*.py` | Shared state, node responsibility, edge/branch, and persistence boundary |
| `scoring/*.py` | Pure input/output math and locked constants; verify no I/O |
| `contracts/*.py` | Activity archetype contract and typed boundary between agents/API/UI |
| `alembic/versions/*.py` | One forward schema change and its relationship to previous/next revision |
| `tests/unit/*` | Isolated invariant or edge case |
| `tests/integration/*` | Cross-layer behavior and fixture/database boundary |

## Frontend file meanings

| Source pattern | What to explain when reviewing it |
| --- | --- |
| `app/**/page.tsx` | URL, data needed, auth/access behavior, and composed UI |
| `components/**/*.tsx` | Presentation responsibility, props, events, and accessibility |
| `*-api.ts` | Endpoint wrapper, request/response shape, and error behavior |
| `hooks/*.ts` | Reusable workflow, query/mutation lifecycle, and side effects |
| `store/*.ts` | Client state shape, actions, persistence, and reset behavior |
| `providers/*.tsx` | Shared React context and cache configuration |
| `validators/*.ts` | User-input schema and user-facing validation |
| `*.test.*` | Behavior under test and the user-visible regression prevented |

## File-by-file study rule

For every real file, write or say three sentences: “This file owns ___; it collaborates with ___; it must not own ___.” Then trace one caller and one callee. This keeps the review grounded in actual boundaries instead of memorized names.
