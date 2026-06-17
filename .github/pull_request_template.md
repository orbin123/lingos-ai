## What & why

<!-- One or two sentences: what does this PR change and why. -->

## Checklist

- [ ] Tests added/updated for the change (or N/A with a reason).
- [ ] **DB migration**: this PR adds/changes an ORM model → an Alembic migration
      is included **and** the model is registered in `app/models.py`. (or N/A)
- [ ] **New env var**: added to `.env.example`, `.env.production.example`, and the
      Environment Variable Matrix in `docs/complete_production_plan.md`. (or N/A)
- [ ] **OpenAPI**: routes changed → snapshot regenerated
      (`uv run python scripts/export_openapi.py`) and committed. (or N/A)
- [ ] **Security note**: any auth/secrets/PII/CORS/cookie impact considered and
      described below. (or "none")

## Security note

<!-- e.g. "none", or describe the auth/secrets/PII/CORS surface this touches. -->

## How verified

<!-- Commands run / manual QA. CI runs lint · types · unit · integration ·
     coverage · contract · frontend · docker-build automatically. -->
