from __future__ import annotations

import time
from collections.abc import AsyncIterator

from app.config import PipelineConfig
from app.models import AudioInput, PipelineEvent
from app.providers.base import StreamingLLMProvider, StreamingSTTProvider, StreamingTTSProvider
from app.session_store import SessionStore


class VoicePipeline:
    def __init__(
        self,
        stt: StreamingSTTProvider,
        llm: StreamingLLMProvider,
        tts: StreamingTTSProvider,
        *,
        config: PipelineConfig | None = None,
        session_store: SessionStore | None = None,
    ) -> None:
        self.stt = stt
        self.llm = llm
        self.tts = tts
        self.config = config or PipelineConfig.from_env()
        self.session_store = session_store or SessionStore(self.config.max_history_turns)

    async def process_audio(self, payload: AudioInput) -> AsyncIterator[PipelineEvent]:
        start = time.perf_counter()
        yield PipelineEvent(
            type="session_started",
            session_id=payload.session_id,
            content="session accepted",
        )

        stt_start = time.perf_counter()
        transcript = await self.stt.transcribe(payload.audio, payload.is_final)
        stt_latency_ms = _elapsed_ms(stt_start)
        state = self.session_store.record_audio_message(payload.session_id, transcript, payload.is_final)
        transcript_type = "transcript_final" if payload.is_final else "transcript_partial"
        yield PipelineEvent(
            type=transcript_type,
            session_id=payload.session_id,
            content=transcript,
            is_final=payload.is_final,
            latency_ms=_elapsed_ms(start),
            metadata={
                "stt_latency_ms": stt_latency_ms,
                "partial_transcript": state.partial_transcript,
            },
        )

        if not payload.is_final:
            return

        llm_start = time.perf_counter()
        collected_tokens: list[str] = []
        buffered_tokens: list[str] = []
        async for token in self.llm.stream_reply(transcript):
            collected_tokens.append(token)
            buffered_tokens.append(token)
            if len(buffered_tokens) >= self.config.llm_chunk_size:
                yield PipelineEvent(
                    type="llm_chunk",
                    session_id=payload.session_id,
                    content=" ".join(buffered_tokens),
                    latency_ms=_elapsed_ms(start),
                    metadata={"chunk_size": len(buffered_tokens)},
                )
                buffered_tokens = []

        if buffered_tokens:
            yield PipelineEvent(
                type="llm_chunk",
                session_id=payload.session_id,
                content=" ".join(buffered_tokens),
                latency_ms=_elapsed_ms(start),
                metadata={"chunk_size": len(buffered_tokens)},
            )

        final_text = " ".join(collected_tokens)
        llm_latency_ms = _elapsed_ms(llm_start)
        yield PipelineEvent(
            type="llm_final",
            session_id=payload.session_id,
            content=final_text,
            is_final=True,
            latency_ms=_elapsed_ms(start),
            metadata={"llm_latency_ms": llm_latency_ms, "token_count": len(collected_tokens)},
        )

        tts_start = time.perf_counter()
        tts_chunks = 0
        async for audio_chunk in self.tts.synthesize(final_text):
            tts_chunks += 1
            yield PipelineEvent(
                type="tts_chunk",
                session_id=payload.session_id,
                content=audio_chunk,
                latency_ms=_elapsed_ms(start),
                metadata={"chunk_index": tts_chunks},
            )
        tts_latency_ms = _elapsed_ms(tts_start)

        total_latency_ms = _elapsed_ms(start)
        state = self.session_store.record_turn(payload.session_id, transcript, final_text, total_latency_ms)
        yield PipelineEvent(
            type="turn_metrics",
            session_id=payload.session_id,
            content="turn metrics recorded",
            latency_ms=total_latency_ms,
            metadata={
                "stt_latency_ms": stt_latency_ms,
                "llm_latency_ms": llm_latency_ms,
                "tts_latency_ms": tts_latency_ms,
                "total_latency_ms": total_latency_ms,
                "history_turns": len(state.turns),
            },
        )
        yield PipelineEvent(
            type="turn_completed",
            session_id=payload.session_id,
            content="turn completed",
            is_final=True,
            latency_ms=total_latency_ms,
            metadata={
                "turns_completed": state.turns_completed,
                "last_response": state.last_response,
            },
        )



def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)
