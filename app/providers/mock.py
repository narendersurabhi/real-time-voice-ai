from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from app.providers.base import StreamingLLMProvider, StreamingSTTProvider, StreamingTTSProvider


class MockSTTProvider(StreamingSTTProvider):
    async def transcribe(self, audio: str, is_final: bool) -> str:
        await asyncio.sleep(0)
        prefix = "final" if is_final else "partial"
        return f"{prefix}: {audio.strip()}"


class MockLLMProvider(StreamingLLMProvider):
    async def stream_reply(self, prompt: str) -> AsyncIterator[str]:
        response = f"Assistant response to '{prompt}'"
        for token in response.split():
            await asyncio.sleep(0)
            yield token


class MockTTSProvider(StreamingTTSProvider):
    async def synthesize(self, text: str) -> AsyncIterator[str]:
        for index, word in enumerate(text.split(), start=1):
            await asyncio.sleep(0)
            yield f"audio_chunk_{index}:{word}"
