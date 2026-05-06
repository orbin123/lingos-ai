"""TTS cache layer — the public-facing TTS service.

This is the layer agents and routes actually import. It composes:

    OpenAITTSClient  +  IBlobStorage  =  CachedTTSService

The contract:
  - Same (text, voice, speed, instructions, model) -> always same audio
  - First call:  OpenAI -> storage write -> URL  (cache_hit=False)
  - Later calls: storage read              -> URL  (cache_hit=True, $0)

Why a separate layer (not a method on OpenAITTSClient)?
  - Single Responsibility: providers do TTS, storage stores blobs, this
    glues them together. Either side can be swapped without rewriting
    the cache.
  - Testability: feed in a fake provider + fake storage to unit-test
    cache hits / misses without touching the network or disk.
"""

from __future__ import annotations

import hashlib
import logging

from app.ai.storage import IBlobStorage, get_default_blob_storage
from app.ai.tts.exceptions import TTSValidationError
from app.ai.tts.interface import SynthesisResult
from app.ai.tts.openai_client import OpenAITTSClient, get_default_tts_client

logger = logging.getLogger(__name__)


def _compute_cache_key(
    *,
    text: str,
    voice: str,
    speed: float,
    style_instructions: str | None,
    model: str,
    audio_format: str,
) -> str:
    """Build a stable cache key from all inputs that affect the audio.

    SHA-256 is overkill for collision safety here, but it's the
    cheapest way to guarantee no clash for many years of usage.
    Truncated to 16 hex chars (64 bits) — Birthday collisions become
    likely only past ~2^32 entries (4 billion). We won't hit that.

    Format: <16-char-hash>.<extension>
    Example: "a3f9c2e8b1d04f6e.mp3"

    Why include `model` in the hash? gpt-4o-mini-tts and tts-1 produce
    audibly different output. Switching models without busting the
    cache would serve stale audio.

    Why include `style_instructions`? It changes delivery noticeably
    on gpt-4o-mini-tts. None and "" must hash differently from
    "speak slowly" so we normalize None → "".
    """
    parts = "|".join([
        model,
        voice,
        f"{speed:.2f}",
        style_instructions or "",
        text,
    ])
    digest = hashlib.sha256(parts.encode("utf-8")).hexdigest()[:16]
    return f"{digest}.{audio_format}"


class CachedTTSService:
    """High-level TTS façade with on-disk dedup caching.

    Usage:
        service = get_default_tts_service()
        result = await service.synthesize(text="Hello!", voice="alloy")
        audio_url = result["audio_url"]
        was_cached = result["cache_hit"]
    """

    def __init__(
        self,
        *,
        provider: OpenAITTSClient,
        storage: IBlobStorage,
        audio_format: str = "mp3",
    ) -> None:
        self._provider = provider
        self._storage = storage
        self._audio_format = audio_format
        # mp3 is the only content_type we currently produce; if you ever
        # change the format, update the lookup below.
        self._content_type_map: dict[str, str] = {
            "mp3":  "audio/mpeg",
            "opus": "audio/opus",
            "aac":  "audio/aac",
            "flac": "audio/flac",
            "wav":  "audio/wav",
            "pcm":  "audio/L16",
        }

    # ------------------------------------------------------------------
    # Public — synthesize with caching
    # ------------------------------------------------------------------
    async def synthesize(
        self,
        *,
        text: str,
        voice: str | None = None,
        speed: float = 1.0,
        style_instructions: str | None = None,
    ) -> SynthesisResult:
        """Get an audio URL for `text`. Hits cache on repeat calls.

        Returns a SynthesisResult with the public URL ready for the
        frontend to drop into <audio src=...>.

        Raises:
            TTSValidationError, TTSAuthError, TTSRateLimited,
            TTSTimeout, TTSProviderError, StorageError — bubbled up
            from the underlying provider / storage. Caller catches
            TTSError for "the synthesizer failed" and StorageError
            for "we couldn't save the file".
        """
        if not text or not text.strip():
            raise TTSValidationError("text must be non-empty")

        # Resolve effective voice / model so they're correctly hashed.
        # We mirror the same defaults the provider uses, so the cache
        # key matches the provider's actual call shape.
        effective_voice = voice or self._provider._voice  # noqa: SLF001
        effective_model = self._provider._model            # noqa: SLF001

        cache_key = _compute_cache_key(
            text=text,
            voice=effective_voice,
            speed=speed,
            style_instructions=style_instructions,
            model=effective_model,
            audio_format=self._audio_format,
        )

        # ---- 1. Cache check
        if await self._storage.exists(key=cache_key):
            logger.info("tts_cache_hit key=%s chars=%d", cache_key, len(text))
            # We don't read the bytes back — we just need the URL. The
            # storage layer will compute it from the key.
            # NOTE: this requires the storage backend to expose URLs
            # given just a key, which our LocalBlobStorage does via
            # _public_url_for(). We avoid reaching into a private method
            # by re-using the same path StoredBlob would publish.
            # Fastest way to get the URL: call put() with empty data?
            # No — we want a side-effect-free URL builder. Add a small
            # helper on the storage by going through put on miss only.
            return self._build_cached_result(cache_key)

        # ---- 2. Cache miss — synthesize then store
        logger.info("tts_cache_miss key=%s chars=%d", cache_key, len(text))
        audio_bytes, provider_result = await self._provider.synthesize(
            text=text,
            voice_id=effective_voice,
            speed=speed,
            style_instructions=style_instructions,
        )
        content_type = self._content_type_map.get(
            self._audio_format, "application/octet-stream"
        )
        stored = await self._storage.put(
            key=cache_key,
            data=audio_bytes,
            content_type=content_type,
        )

        return SynthesisResult(
            audio_url=stored["public_url"],
            duration_seconds=provider_result["duration_seconds"],
            cache_hit=False,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_cached_result(self, cache_key: str) -> SynthesisResult:
        """Build a SynthesisResult for a cache hit WITHOUT re-reading
        the bytes off disk.

        We rebuild the URL by leaning on the storage's public URL
        convention. Both LocalBlobStorage and any future S3 client
        compute URLs deterministically from keys, so this is safe.

        Duration is unknown on cache hits without a separate stat() +
        parse. We return 0.0 and let the frontend ignore it; if you
        need exact duration on cache hits later, persist it alongside
        the file (e.g. in a sidecar .json or a metadata key).
        """
        # The storage interface doesn't expose a "key -> url" function
        # directly, but our LocalBlobStorage builds URLs from keys via
        # `<prefix>/<key>`. We replicate that pattern here. When you add
        # an S3 backend, expose a public `url_for(key)` method on
        # IBlobStorage and switch this line to call it.
        from app.ai.storage.local_client import LocalBlobStorage

        if isinstance(self._storage, LocalBlobStorage):
            url = self._storage._public_url_for(cache_key)  # noqa: SLF001
        else:
            # Future-proofing — if a different storage is wired up
            # later without exposing url_for, surface a clear error.
            raise NotImplementedError(
                f"Storage backend {type(self._storage).__name__} does not "
                "expose a key→URL helper. Add `url_for(key)` to its "
                "interface and call it here."
            )

        return SynthesisResult(
            audio_url=url,
            duration_seconds=0.0,  # not tracked on cache hit
            cache_hit=True,
        )


# ---------------------------------------------------------------------------
# Process-wide singleton (lazy)
# ---------------------------------------------------------------------------
_default_service: CachedTTSService | None = None


def get_default_tts_service() -> CachedTTSService:
    """Return the shared default TTS service (provider + cache + storage).

    Lazy — first call wires up the provider singleton and the storage
    singleton. Tests can call `_reset_default_tts_service()` to force a
    fresh build with mocked dependencies.
    """
    global _default_service
    if _default_service is None:
        _default_service = CachedTTSService(
            provider=get_default_tts_client(),
            storage=get_default_blob_storage(),
        )
    return _default_service


def _reset_default_tts_service() -> None:
    """Test-only: drop the cached service so the next get_*() rebuilds."""
    global _default_service
    _default_service = None
