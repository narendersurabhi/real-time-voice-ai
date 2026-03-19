# Real-Time Voice AI Pipeline

A starter implementation of a low-latency conversational voice system that connects streaming speech-to-text (STT), large language model (LLM) reasoning, and text-to-speech (TTS) behind FastAPI and WebSocket APIs.

## Highlights
- Streaming-friendly FastAPI application with WebSocket transport.
- Async pipeline stages for audio ingestion, transcription, response generation, and speech synthesis.
- Pluggable provider interfaces for STT, LLM, and TTS integrations.
- Mock providers included for local development, testing, and architecture validation.
- In-memory session tracking, latency metrics, and WER evaluation helpers.
- WebRTC-ready ICE configuration endpoint for browser clients.

## Architecture

```text
Client audio -> WebSocket -> VoicePipeline
                         -> STT provider -> partial/final transcript events
                         -> LLM provider -> chunked response events
                         -> TTS provider -> synthesized audio events
                         -> SessionStore -> turn history and latency metrics
                         -> WebSocket -> client
```

## Implemented Next Steps
- **Session state and conversation history**: sessions now track partial transcripts, completed turns, and the latest assistant response.
- **Latency instrumentation**: each final turn reports STT, LLM, TTS, and total latency metrics.
- **Response chunking**: LLM tokens are batched into configurable chunks before being emitted to clients.
- **WER-style evaluation**: `/evaluate/wer` provides a lightweight word error rate utility for ASR benchmarking.
- **WebRTC bootstrap support**: `/webrtc/config` returns ICE server configuration suitable for browser-side WebRTC setup.

## Project Layout

```text
app/
  config.py            Environment-driven pipeline configuration
  evaluation.py        WER-style evaluation helpers
  main.py              FastAPI application and routes
  models.py            Shared event and request models
  pipeline.py          Async orchestration logic
  session_store.py     In-memory session history and metrics
  providers/
    base.py            Provider protocols/interfaces
    mock.py            Mock implementations for development

tests/
  test_api.py          Health and utility endpoint coverage
  test_pipeline.py     Pipeline flow and session tracking coverage
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

## Available HTTP Endpoints
- `GET /health` — basic liveness check.
- `GET /sessions` — returns all in-memory session snapshots.
- `GET /sessions/{session_id}` — returns a specific session snapshot.
- `GET /webrtc/config` — returns ICE server configuration for browser clients.
- `GET /evaluate/wer?reference=...&hypothesis=...` — computes word error rate style metrics.

## Configuration
- `VOICE_LLM_CHUNK_SIZE` — number of streamed LLM tokens per emitted chunk event.
- `VOICE_MAX_HISTORY_TURNS` — max turns retained in memory per session.
- `VOICE_ICE_SERVERS` — comma-separated ICE/STUN/TURN URLs for WebRTC clients.

## Next Steps
- Replace mock providers with production STT/LLM/TTS integrations.
- Add persistent storage for conversation state and evaluation runs.
- Add structured tracing/export for latency dashboards.
- Add browser WebRTC signaling and media forwarding.
