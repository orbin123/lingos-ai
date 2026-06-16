"""Canonical fake image-generation service.

Mirrors `generate(*, prompt, ...)` of the real imagegen client; records calls
and supports `fail=True` for fallback-path tests.
"""

from __future__ import annotations


class FakeImageGenService:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[dict] = []

    async def generate(self, *, prompt: str, **kwargs):
        self.calls.append({"prompt": prompt, **kwargs})
        if self.fail:
            raise RuntimeError("imagegen down")
        return {
            "image_url": "/images/ab/fake-scene.png",
            "width": 1536,
            "height": 1024,
            "cache_hit": False,
        }
