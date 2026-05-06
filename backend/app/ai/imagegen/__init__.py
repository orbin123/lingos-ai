"""Image generation package — STUB for Phase 5.

Only the abstract interface lives here today. Concrete provider
(DALL·E or similar) will be added in Phase 5.
"""

from app.ai.imagegen.interface import IImageGenClient, ImageResult

__all__ = ["IImageGenClient", "ImageResult"]
