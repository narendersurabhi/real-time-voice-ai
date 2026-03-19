from __future__ import annotations

from app.models import AudioInput
from app.pipeline import VoicePipeline
from app.providers.mock import MockLLMProvider, MockSTTProvider, MockTTSProvider

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
except ModuleNotFoundError:  # pragma: no cover - optional runtime dependency in this environment
    FastAPI = None
    WebSocket = object
    WebSocketDisconnect = Exception

pipeline = VoicePipeline(
    stt=MockSTTProvider(),
    llm=MockLLMProvider(),
    tts=MockTTSProvider(),
)

if FastAPI is not None:
    app = FastAPI(title="Real-Time Voice AI Pipeline")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}


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
