# `backend/app/models.py`

Central ORM model registry. It imports models from every feature so relationship strings resolve and Alembic sees every table through `Base.metadata`.
