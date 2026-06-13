"""Blog module — the marketing-site CMS.

A `BlogPost` is authored in Markdown by an admin and read publicly. The
module follows the standard layered pattern:

    routes.py       → public (`/blog`) + admin (`/admin/blog`) HTTP endpoints
    service.py      → business logic, owns transaction commits
    repository.py   → all DB queries (the only layer touching the ORM session)
    models.py       → the `BlogPost` ORM model
    schemas.py      → Pydantic request/response shapes
    exceptions.py   → domain exceptions (routes translate these to HTTP)

Public reads expose only `published` posts; drafts are admin-only. Admin
mutations are audit-logged via `app.modules.admin.audit_service`.
"""
