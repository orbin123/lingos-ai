# LingosAI - AI English Tutor

An AI-powered English learning platform that analyzes a user's 
weaknesses and gives personalized daily tasks with precise feedback.

## Tech Stack
- Backend: FastAPI + PostgreSQL + SQLAlchemy
- AI: LangChain + LLM
- Frontend: Next.js + Tailwind
- Infra: Docker, Redis, Celery

## Status
🚧 In active development. MVP in progress.

## Admin System
Phase 3 adds production admin billing and access-control surfaces:

- Role-backed permissions for `learner`, `admin`, and `super_admin`
- Super-admin APIs for role assignment and role permission grants
- Billing admin tables for subscriptions and payments; only provider IDs are stored
- Admin payment, subscription, and per-user billing views with masked provider IDs
- Audit logs for role, payment, subscription, task-template, user-status, and feedback-review changes
- Admin/login rate limiting with clear `401`, `403`, and `404` responses

Normal admins can read limited billing information when granted `payments.read`.
Only super admins can manage roles or subscription status.

## Setup
Backend:

```bash
cd backend
uv run alembic upgrade head
uv run pytest tests/test_admin_api.py
```

Frontend:

```bash
cd frontend
npm run test:admin
npm run build
```
