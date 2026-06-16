"""Canonical fake text-to-speech service.

Mirrors the `synthesize(*, text, ...)` surface of the real TTS client and
records calls for assertions. `fail=True` simulates a provider outage so
agents' fallback paths can be exercised offline.
"""

from __future__ import annotations


class FakeTTSService:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[dict] = []

    async def synthesize(self, *, text: str, **kwargs):
        self.calls.append({"text": text, **kwargs})
        if self.fail:
            raise RuntimeError("tts down")
        return {
            "audio_url": "/audio/fake-listening.mp3",
            "duration_seconds": 12.4,
        }
