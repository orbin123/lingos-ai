"""Image-generation contracts.

Phase 5 follows the same two-layer shape as TTS:

1. `IImageGenClient`
   The raw provider contract. It returns generated image bytes plus the
   image dimensions. It does NOT know about storage, public URLs, or
   cache-hit flags.

2. `ImageResult`
   The high-level service result returned by `CachedImageGenService`,
   after the provider output has been persisted and turned into a
   public URL.

Used by visual-context tasks:
  - storyboard_narration
  - vocabulary_visualisation
  - tone_scenario_visuals
"""

from __future__ import annotations

from typing import Literal, Protocol

from typing_extensions import TypedDict


# Shared size presets for the app's three supported aspect ratios.
# Sticking to fixed presets keeps frontend layouts predictable and keeps
# cache-hit dimensions deterministic without needing image-side metadata.
AspectRatio = Literal["square", "landscape", "portrait"]

_IMAGE_DIMENSIONS_BY_ASPECT_RATIO: dict[AspectRatio, tuple[int, int]] = {
    "square": (1024, 1024),
    "landscape": (1536, 1024),
    "portrait": (1024, 1536),
}


def dimensions_for_aspect_ratio(aspect_ratio: AspectRatio) -> tuple[int, int]:
    """Return the app's canonical pixel dimensions for one aspect ratio."""
    try:
        return _IMAGE_DIMENSIONS_BY_ASPECT_RATIO[aspect_ratio]
    except KeyError as exc:  # pragma: no cover - defensive runtime guard
        raise ValueError(
            f"Unsupported aspect_ratio {aspect_ratio!r}. "
            f"Supported: {sorted(_IMAGE_DIMENSIONS_BY_ASPECT_RATIO)}"
        ) from exc


def size_string_for_aspect_ratio(aspect_ratio: AspectRatio) -> str:
    """Return the OpenAI Image API `size` string for one aspect ratio."""
    width, height = dimensions_for_aspect_ratio(aspect_ratio)
    return f"{width}x{height}"


class ImageResult(TypedDict):
    """High-level image-generation result returned to routes/callers."""

    image_url: str
    width: int
    height: int
    cache_hit: bool


class GeneratedImage(TypedDict):
    """Raw provider output before storage/caching concerns are applied."""

    image_bytes: bytes
    width: int
    height: int


class IImageGenClient(Protocol):
    """Minimal provider-side image-generation contract."""

    @property
    def model_name(self) -> str:
        """Provider model used for generation, e.g. `gpt-image-2`."""
        ...

    @property
    def output_format(self) -> str:
        """Image format returned by the provider, e.g. `png`."""
        ...

    @property
    def default_quality(self) -> str:
        """Configured provider quality, e.g. `medium`."""
        ...

    async def generate(
        self,
        *,
        prompt: str,
        aspect_ratio: AspectRatio = "square",
        style: str | None = None,
    ) -> GeneratedImage:
        """Generate raw image bytes from a text prompt.

        Args:
            prompt: Plain-English description of the desired image.
            aspect_ratio: 'square' / 'landscape' / 'portrait'.
            style: Optional free-form stylistic guidance. Providers that
                do not expose a first-class style parameter may fold this
                into the prompt instead.
        """
        ...
