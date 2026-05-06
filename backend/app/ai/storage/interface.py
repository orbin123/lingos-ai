"""Blob storage contract — STUB.

Implementation comes later — TTS, STT, and image-gen all need somewhere
to put their output bytes. This abstraction lets them stay agnostic of
the actual backend (local disk in dev, S3 / Cloudflare R2 in prod).

Why an interface here at all? Because storage is the *one* dependency
that every multimedia AI module will share — and the cheapest place to
make a wrong decision. Locking the contract early means TTS / STT /
ImageGen don't have to know whether they're writing to /tmp or to S3.
"""

from __future__ import annotations

from typing import Protocol

from typing_extensions import TypedDict


class StoredBlob(TypedDict):
    """A blob that has been persisted and is now servable."""
    public_url: str        # URL the frontend / browser can hit
    storage_key: str       # provider-side key (S3 path, local path, etc.)
    content_type: str      # e.g. "audio/mpeg", "image/png"
    size_bytes: int


class IBlobStorage(Protocol):
    """Minimal blob-storage contract.

    Implementations decide:
      - where bytes live (local disk, S3, R2, ...)
      - how URLs are signed (public bucket vs presigned URL)
      - retention policy (purge after N days, etc.)

    Callers only know: 'put bytes in, get a URL out.'
    """

    async def put(
        self,
        *,
        key: str,
        data: bytes,
        content_type: str,
    ) -> StoredBlob:
        """Store `data` under `key`. Returns a StoredBlob with public URL.

        Implementations are responsible for idempotency — calling `put`
        twice with the same key + data must be a no-op cost-wise.
        """
        ...

    async def get(self, *, key: str) -> bytes | None:
        """Return the bytes for `key`, or None if not found.

        Used by hash-caches to verify a blob already exists before
        re-synthesising / re-generating.
        """
        ...

    async def exists(self, *, key: str) -> bool:
        """Cheap existence check — does NOT pull bytes.

        Used to avoid an expensive `get` just to check the cache.
        """
        ...
