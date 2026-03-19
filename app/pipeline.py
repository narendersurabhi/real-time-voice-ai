from __future__ import annotations

import time
from collections.abc import AsyncIterator

from app.models import AudioInput, PipelineEvent
from app.providers.base import StreamingLLMProvider, StreamingSTTProvider, StreamingTTSProvider


class VoicePipeline:
    def __init__(
        self,
        stt: StreamingSTTProvider,
        llm: StreamingLLMProvider,
        tts: StreamingTTSProvider,
    ) -> None:
        self.stt = stt
        self.llm = llm
        self.tts = tts

    async def process_audio(self, payload: AudioInput) -> AsyncIterator[PipelineEvent]:
        start = time.perf_counter()
        yield PipelineEvent(
            type="session_started",
            session_id=payload.session_id,
            content="session accepted",
            is_final=False,
        )

        transcript = await self.stt.transcribe(payload.audio, payload.is_final)
        transcript_type = "transcript_final" if payload.is_final else "transcript_partial"
        yield PipelineEvent(
            type=transcript_type,
            session_id=payload.session_id,
            content=transcript,
            is_final=payload.is_final,
            latency_ms=_elapsed_ms(start),
        )

        if not payload.is_final:
            return

        collected_tokens: list[str] = []
        async for token in self.llm.stream_reply(transcript):
            collected_tokens.append(token)
            yield PipelineEvent(
                type="llm_token",
                session_id=payload.session_id,
                content=token,
                latency_ms=_elapsed_ms(start),
            )

        final_text = " ".join(collected_tokens)
        yield PipelineEvent(
            type="llm_final",
            session_id=payload.session_id,
            content=final_text,
            is_final=True,
            latency_ms=_elapsed_ms(start),
        )

        async for audio_chunk in self.tts.synthesize(final_text):
            yield PipelineEvent(
                type="tts_chunk",
                session_id=payload.session_id,
                content=audio_chunk,
                latency_ms=_elapsed_ms(start),
            )

        yield PipelineEvent(
            type="turn_completed",
            session_id=payload.session_id,
            content="turn completed",
            is_final=True,
            latency_ms=_elapsed_ms(start),
        )


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)
