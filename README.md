# Real-Time Voice AI Pipeline

A starter implementation of a low-latency conversational voice system that connects streaming speech-to-text (STT), large language model (LLM) reasoning, and text-to-speech (TTS) behind FastAPI and WebSocket APIs.

## Highlights
- Streaming-friendly FastAPI application with WebSocket transport.
- Async pipeline stages for audio ingestion, transcription, response generation, and speech synthesis.
- Pluggable provider interfaces for STT, LLM, and TTS integrations.
- Mock providers included for local development, testing, and architecture validation.
- Structured events for incremental transcript, token, and audio chunk delivery.

## Architecture

```text
Client audio -> WebSocket -> VoicePipeline
                         -> STT provider -> partial/final transcript events
                         -> LLM provider -> streaming token events
                         -> TTS provider -> synthesized audio events
                         -> WebSocket -> client
```

## Project Layout

```text
app/
  main.py              FastAPI application and routes
  models.py            Shared event and request models
  pipeline.py          Async orchestration logic
  providers/
    base.py            Provider protocols/interfaces
    mock.py            Mock implementations for development

tests/
  test_api.py          Health endpoint coverage
  test_pipeline.py     Pipeline flow coverage
```

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

Open a WebSocket connection to `/ws/voice` and send JSON messages in this shape:

```json
{
  "type": "audio_chunk",
  "audio": "hello from microphone",
  "is_final": true,
  "session_id": "demo-session"
}
```

The mock implementation treats the `audio` field as already-decoded text so you can test the event flow without a media stack.

## Next Steps
- Replace mock providers with production STT/LLM/TTS integrations.
- Add WebRTC signaling/media ingestion for browser-native audio transport.
- Persist conversation state and evaluation metrics.
- Add latency instrumentation and WER-style evaluation jobs.
