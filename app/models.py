from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal, Optional


@dataclass(slots=True)
class AudioInput:
    type: Literal["audio_chunk"] = "audio_chunk"
    session_id: str = "default-session"
    audio: str = ""
    is_final: bool = False

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "AudioInput":
        return cls(
            type=str(payload.get("type", "audio_chunk")),
            session_id=str(payload.get("session_id", "default-session")),
            audio=str(payload.get("audio", "")),
            is_final=bool(payload.get("is_final", False)),
        )


@dataclass(slots=True)
class PipelineEvent:
    type: Literal[
        "session_started",
        "transcript_partial",
        "transcript_final",
        "llm_token",
        "llm_final",
        "tts_chunk",
        "turn_completed",
        "error",
    ]
    session_id: str
    content: str
    is_final: bool = False
    latency_ms: Optional[float] = None

    def model_dump(self) -> dict[str, object]:
        return asdict(self)
