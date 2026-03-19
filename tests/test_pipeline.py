import asyncio

from app.config import PipelineConfig
from app.models import AudioInput
from app.pipeline import VoicePipeline
from app.providers.mock import MockLLMProvider, MockSTTProvider, MockTTSProvider
from app.session_store import SessionStore


def test_partial_audio_only_returns_transcript() -> None:
    pipeline = VoicePipeline(
        MockSTTProvider(),
        MockLLMProvider(),
        MockTTSProvider(),
        config=PipelineConfig(llm_chunk_size=2, max_history_turns=3),
        session_store=SessionStore(max_history_turns=3),
    )
    payload = AudioInput(session_id="s1", audio="hello world", is_final=False)

    events = asyncio.run(_collect_events(pipeline, payload))

    assert [event.type for event in events] == ["session_started", "transcript_partial"]
    assert events[-1].content == "partial: hello world"
    assert events[-1].metadata["partial_transcript"] == "partial: hello world"


def test_final_audio_runs_full_pipeline_and_updates_session_state() -> None:
    store = SessionStore(max_history_turns=3)
    pipeline = VoicePipeline(
        MockSTTProvider(),
        MockLLMProvider(),
        MockTTSProvider(),
        config=PipelineConfig(llm_chunk_size=2, max_history_turns=3),
        session_store=store,
    )
    payload = AudioInput(session_id="s2", audio="hello world", is_final=True)

    events = asyncio.run(_collect_events(pipeline, payload))
    event_types = [event.type for event in events]

    assert event_types[0:2] == ["session_started", "transcript_final"]
    assert event_types.count("llm_chunk") >= 1
    assert "llm_final" in event_types
    assert "tts_chunk" in event_types
    assert "turn_metrics" in event_types
    assert event_types[-1] == "turn_completed"

    snapshot = store.snapshot("s2")
    assert snapshot["turns_completed"] == 1
    assert snapshot["last_transcript"] == "final: hello world"
    assert snapshot["last_response"].startswith("Assistant response")


async def _collect_events(pipeline: VoicePipeline, payload: AudioInput):
    return [event async for event in pipeline.process_audio(payload)]
