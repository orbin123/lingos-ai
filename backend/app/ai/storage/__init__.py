"""Blob storage package — local-disk implementation + factory.

Public surface:

    from app.ai.storage import (
        IBlobStorage, StoredBlob, get_default_blob_storage,
        StorageError,
    )
"""

from app.ai.storage.exceptions import (
    StorageError,
    StorageNotFound,
    StorageReadError,
    StorageWriteError,
)
from app.ai.storage.interface import IBlobStorage, StoredBlob
from app.ai.storage.local_client import LocalBlobStorage


# ---------------------------------------------------------------------------
# Process-wide singleton — lazy + cached.
#
# We avoid `lru_cache` here because the storage client takes args derived
# from `settings`, which we want to read once on first use (not at import
# time, which makes testing harder).
# ---------------------------------------------------------------------------
_default_storage: LocalBlobStorage | None = None


def get_default_blob_storage() -> LocalBlobStorage:
    """Return the shared default blob-storage client.

    Today: LocalBlobStorage rooted at `settings.TTS_CACHE_DIR`.
    Tomorrow (production): swap the body for an S3 / R2 client. Callers
    don't change.
    """
    global _default_storage
    if _default_storage is None:
        # Lazy import to avoid pulling settings at module load — keeps
        # `from app.ai.storage import IBlobStorage` cheap for type hints.
        from pathlib import Path

        from app.core.config import settings

        _default_storage = LocalBlobStorage(
            root_dir=Path(settings.TTS_CACHE_DIR),
            public_url_prefix=settings.TTS_PUBLIC_URL_PREFIX,
        )
    return _default_storage


__all__ = [
    "IBlobStorage",
    "StoredBlob",
    "LocalBlobStorage",
    "get_default_blob_storage",
    "StorageError",
    "StorageNotFound",
    "StorageReadError",
    "StorageWriteError",
]
