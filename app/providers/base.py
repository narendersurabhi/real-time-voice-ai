from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class StreamingSTTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio: str, is_final: bool) -> str:
        raise NotImplementedError


class StreamingLLMProvider(ABC):
    @abstractmethod
    async def stream_reply(self, prompt: str) -> AsyncIterator[str]:
        raise NotImplementedError


class StreamingTTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str) -> AsyncIterator[str]:
        raise NotImplementedError
