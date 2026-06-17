"""Blob storage package — local-disk implementation + factory.

Public surface:

    from app.ai.storage import (
        IBlobStorage, StoredBlob, get_default_blob_storage,
        StorageError,
    )
"""

from pathlib import Path

from app.ai.storage.exceptions import (
    StorageError,
    StorageNotFound,
    StorageReadError,
    StorageWriteError,
)
from app.ai.storage.interface import IBlobStorage, StoredBlob
from app.ai.storage.local_client import LocalBlobStorage
from app.ai.storage.s3_client import S3BlobStorage


# ---------------------------------------------------------------------------
# Factory — pick the backend by config.
#
# Every call-site passes the same two args it used to pass to
# `LocalBlobStorage`: a local cache dir (used only by the local backend) and a
# `public_url_prefix`. In S3 mode the prefix becomes the S3 key namespace and,
# for public blobs, the suffix appended to the CloudFront base. Setting
# `private=True` keeps the blob off CloudFront and routes `url_for` back
# through an owner-checked app route (learner audio).
# ---------------------------------------------------------------------------
def build_blob_storage(
    *,
    cache_dir: str | Path,
    public_url_prefix: str,
    private: bool = False,
) -> IBlobStorage:
    """Return a blob-storage client for the configured backend.

    `STORAGE_BACKEND=local` (default) → `LocalBlobStorage`; `=s3` →
    `S3BlobStorage` against `MEDIA_S3_BUCKET` / `MEDIA_CDN_URL`. The S3 object
    key layout mirrors the local shard layout so caches stay consistent.
    """
    from app.core.config import settings

    if settings.STORAGE_BACKEND == "s3":
        key_prefix = public_url_prefix.strip("/")
        if private:
            return S3BlobStorage(
                bucket=settings.MEDIA_S3_BUCKET,
                key_prefix=key_prefix,
                region=settings.MEDIA_S3_REGION,
                internal_url_prefix=public_url_prefix,
            )
        return S3BlobStorage(
            bucket=settings.MEDIA_S3_BUCKET,
            key_prefix=key_prefix,
            region=settings.MEDIA_S3_REGION,
            public_url_base=settings.MEDIA_CDN_URL,
        )

    return LocalBlobStorage(
        root_dir=Path(cache_dir),
        public_url_prefix=public_url_prefix,
    )


# ---------------------------------------------------------------------------
# Process-wide singleton — lazy + cached.
#
# We avoid `lru_cache` here because the storage client takes args derived
# from `settings`, which we want to read once on first use (not at import
# time, which makes testing harder).
# ---------------------------------------------------------------------------
_default_storage: IBlobStorage | None = None


def get_default_blob_storage() -> IBlobStorage:
    """Return the shared default blob-storage client.

    Rooted at the TTS cache dir / `/audio` prefix. The backend (local vs S3)
    is chosen by `STORAGE_BACKEND`; callers don't change.
    """
    global _default_storage
    if _default_storage is None:
        from app.core.config import settings

        _default_storage = build_blob_storage(
            cache_dir=settings.TTS_CACHE_DIR,
            public_url_prefix=settings.TTS_PUBLIC_URL_PREFIX,
        )
    return _default_storage


__all__ = [
    "IBlobStorage",
    "StoredBlob",
    "LocalBlobStorage",
    "S3BlobStorage",
    "build_blob_storage",
    "get_default_blob_storage",
    "StorageError",
    "StorageNotFound",
    "StorageReadError",
    "StorageWriteError",
]
