from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class PipelineConfig:
    llm_chunk_size: int = 3
    max_history_turns: int = 10
    ice_servers: tuple[str, ...] = ("stun:stun.l.google.com:19302",)

    @classmethod
    def from_env(cls) -> "PipelineConfig":
        chunk_size = int(os.getenv("VOICE_LLM_CHUNK_SIZE", "3"))
        history_turns = int(os.getenv("VOICE_MAX_HISTORY_TURNS", "10"))
        raw_ice_servers = os.getenv("VOICE_ICE_SERVERS", "stun:stun.l.google.com:19302")
        ice_servers = tuple(server.strip() for server in raw_ice_servers.split(",") if server.strip())
        return cls(
            llm_chunk_size=max(1, chunk_size),
            max_history_turns=max(1, history_turns),
            ice_servers=ice_servers or ("stun:stun.l.google.com:19302",),
        )
