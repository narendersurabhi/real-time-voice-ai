from __future__ import annotations

from app.config import PipelineConfig
from app.evaluation import calculate_wer
from app.models import AudioInput
from app.pipeline import VoicePipeline
from app.providers.mock import MockLLMProvider, MockSTTProvider, MockTTSProvider

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
except ModuleNotFoundError:  # pragma: no cover - optional runtime dependency in this environment
    FastAPI = None
    WebSocket = object
    WebSocketDisconnect = Exception

config = PipelineConfig.from_env()
pipeline = VoicePipeline(
    stt=MockSTTProvider(),
    llm=MockLLMProvider(),
    tts=MockTTSProvider(),
    config=config,
)

if FastAPI is not None:
    app = FastAPI(title="Real-Time Voice AI Pipeline")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}


    @app.get("/sessions")
    async def list_sessions() -> dict[str, object]:
        return {"sessions": pipeline.session_store.all_snapshots()}


    @app.get("/sessions/{session_id}")
    async def get_session(session_id: str) -> dict[str, object]:
        return pipeline.session_store.snapshot(session_id)


    @app.get("/webrtc/config")
    async def webrtc_config() -> dict[str, object]:
        return {
            "iceServers": [{"urls": server} for server in config.ice_servers],
            "transport": "webrtc",
        }


    @app.get("/evaluate/wer")
    async def evaluate_wer(reference: str, hypothesis: str) -> dict[str, object]:
        return calculate_wer(reference, hypothesis).__dict__


    @app.websocket("/ws/voice")
    async def voice_socket(websocket: WebSocket) -> None:
        await websocket.accept()

        try:
            while True:
                message = await websocket.receive_json()
                payload = AudioInput.from_dict(message)
                async for event in pipeline.process_audio(payload):
                    await websocket.send_json(event.model_dump())
        except WebSocketDisconnect:
            return
else:
    app = None
