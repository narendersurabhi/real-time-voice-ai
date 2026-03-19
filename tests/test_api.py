import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_webrtc_config() -> None:
    response = client.get("/webrtc/config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["transport"] == "webrtc"
    assert payload["iceServers"]
