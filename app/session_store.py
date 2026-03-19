from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class ConversationTurn:
    transcript: str
    response: str
    total_latency_ms: float


@dataclass(slots=True)
class SessionState:
    session_id: str
    turns: deque[ConversationTurn] = field(default_factory=deque)
    partial_transcript: str = ""
    last_transcript: str = ""
    last_response: str = ""
    turns_completed: int = 0
    total_audio_messages: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "partial_transcript": self.partial_transcript,
            "last_transcript": self.last_transcript,
            "last_response": self.last_response,
            "turns_completed": self.turns_completed,
            "total_audio_messages": self.total_audio_messages,
            "turns": [asdict(turn) for turn in self.turns],
        }


class SessionStore:
    def __init__(self, max_history_turns: int = 10) -> None:
        self.max_history_turns = max_history_turns
        self._sessions: dict[str, SessionState] = {}

    def get_or_create(self, session_id: str) -> SessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(session_id=session_id)
            self._sessions[session_id].turns = deque(maxlen=self.max_history_turns)
        return self._sessions[session_id]

    def record_audio_message(self, session_id: str, transcript: str, is_final: bool) -> SessionState:
        state = self.get_or_create(session_id)
        state.total_audio_messages += 1
        if is_final:
            state.partial_transcript = ""
            state.last_transcript = transcript
        else:
            state.partial_transcript = transcript
        return state

    def record_turn(self, session_id: str, transcript: str, response: str, latency_ms: float) -> SessionState:
        state = self.get_or_create(session_id)
        state.turns.append(
            ConversationTurn(
                transcript=transcript,
                response=response,
                total_latency_ms=latency_ms,
            )
        )
        state.last_transcript = transcript
        state.last_response = response
        state.turns_completed += 1
        state.partial_transcript = ""
        return state

    def snapshot(self, session_id: str) -> dict[str, object]:
        return self.get_or_create(session_id).to_dict()

    def all_snapshots(self) -> list[dict[str, object]]:
        return [state.to_dict() for state in self._sessions.values()]
