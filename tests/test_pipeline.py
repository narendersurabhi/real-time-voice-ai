import asyncio

from app.models import AudioInput
from app.pipeline import VoicePipeline
from app.providers.mock import MockLLMProvider, MockSTTProvider, MockTTSProvider


def test_partial_audio_only_returns_transcript() -> None:
    pipeline = VoicePipeline(MockSTTProvider(), MockLLMProvider(), MockTTSProvider())
    payload = AudioInput(session_id="s1", audio="hello world", is_final=False)

    events = asyncio.run(_collect_events(pipeline, payload))

    assert [event.type for event in events] == ["session_started", "transcript_partial"]
    assert events[-1].content == "partial: hello world"


def test_final_audio_runs_full_pipeline() -> None:
    pipeline = VoicePipeline(MockSTTProvider(), MockLLMProvider(), MockTTSProvider())
    payload = AudioInput(session_id="s2", audio="hello world", is_final=True)

    events = asyncio.run(_collect_events(pipeline, payload))
    event_types = [event.type for event in events]

    assert event_types[0:2] == ["session_started", "transcript_final"]
    assert "llm_final" in event_types
    assert "tts_chunk" in event_types
    assert event_types[-1] == "turn_completed"


async def _collect_events(pipeline: VoicePipeline, payload: AudioInput):
    return [event async for event in pipeline.process_audio(payload)]
