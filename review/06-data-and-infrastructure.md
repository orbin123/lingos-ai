# 6. Data and infrastructure

## Database

PostgreSQL is the durable store. SQLAlchemy models describe tables, repositories query them, and Alembic migrations evolve the schema forward. The migration graph matters because tests using SQLite `create_all` do not prove that every migration replays correctly.

## Redis

Docker Compose provides Redis for local coordination such as rate limiting or short-lived state. It is not the source of truth for curriculum, sessions, or points.

## Configuration

`app/core/config.py` is the single settings boundary and reads the repository `.env`. Required values fail startup intentionally. The frontend receives its API base URL through `NEXT_PUBLIC_API_URL`. Secrets and provider keys belong in environment/configuration systems, never in review notes.

## Media and deployment

Local media caches live under AI capability directories and are served through FastAPI static mounts. Docker Compose runs Postgres and Redis while the apps run on the host in local development. AWS deployment is frozen recovery history; Azure work is gated and must not be enabled or mutated without explicit approval. Vercel can host the frontend independently.

## Security

JWT bearer auth identifies the current user. Google OAuth is supported. Roles and permissions protect admin functions. Admin mutations create audit records. Payment records retain provider identifiers rather than raw payment data. Rate limiting and security headers are cross-cutting defenses.
