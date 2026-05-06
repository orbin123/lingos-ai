"""Image generation contract — STUB for Phase 5.

Implementation lands in Phase 5 (likely DALL·E via OpenAI, or a
cheaper alternative if cost matters more than quality).

Used by visual-context tasks:
  - storyboard_narration  (give learner a generated scene to describe)
  - vocabulary_visualisation (illustrate target vocab in context)
  - tone_scenario_visuals (show a workplace / casual setting)

Like TTS, implementations MUST cache by prompt hash. Image generation
is one of the most expensive AI calls in the stack — a cache hit is
the difference between $0.04 and $0.00.
"""

from __future__ import annotations

from typing import Literal, Protocol

from typing_extensions import TypedDict


class ImageResult(TypedDict):
    """What every image-generation call returns."""
    image_url: str        # public URL or local path served by our app
    width: int
    height: int
    cache_hit: bool       # True if served from our hash-cache


# Common aspect ratios the app uses. Providers map these to their own
# size strings (e.g. DALL·E uses "1024x1024", "1792x1024", ...).
AspectRatio = Literal["square", "landscape", "portrait"]


class IImageGenClient(Protocol):
    """Minimal image-generation contract."""

    async def generate(
        self,
        *,
        prompt: str,
        aspect_ratio: AspectRatio = "square",
        style: str | None = None,
    ) -> ImageResult:
        """Generate one image from a text prompt.

        Args:
            prompt: Plain-English description of the desired image.
            aspect_ratio: 'square' / 'landscape' / 'portrait'.
            style: Optional provider-specific style hint (e.g. 'flat',
                'photographic'). Implementations may ignore.

        Returns:
            ImageResult — URL + dimensions + cache flag.
        """
        ...
