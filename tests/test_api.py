from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.app import app
from src.config.settings import Settings


@pytest.fixture
def valid_headers():
    return {"X-API-Key": Settings.API_KEY, "Content-Type": "application/json"}


@pytest.fixture
async def client():
    mock_engine = MagicMock()
    mock_engine.last_analysis = "Test analysis"
    mock_engine.is_analyzing = False
    mock_engine.frame_count = 42
    mock_engine.notifier = MagicMock()
    mock_engine.notifier.keywords = ["Armed: YES"]
    mock_engine.notifier.send_message.return_value = True
    mock_engine.storage = MagicMock()
    mock_engine.storage.get_stats.return_value = {
        "total_analyses": 0,
        "total_alerts": 0,
        "last_analysis": None,
    }
    mock_engine.storage.get_history.return_value = []
    mock_engine.expert = MagicMock()

    mock_sm = MagicMock()
    mock_sm.caps = {"Main": MagicMock(isOpened=lambda: True)}
    mock_sm.get_frame.return_value = (False, None)

    with patch("src.api.deps._engine", mock_engine), patch("src.api.deps._stream_manager", mock_sm):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


class TestHealthEndpoint:
    @pytest.mark.anyio
    async def test_health_returns_200(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "version" in data
        assert "cameras" in data

    @pytest.mark.anyio
    async def test_health_no_auth_required(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200


class TestAuthEndpoints:
    @pytest.mark.anyio
    async def test_mission_requires_api_key(self, client):
        resp = await client.get("/mission")
        assert resp.status_code == 403

    @pytest.mark.anyio
    async def test_mission_with_valid_key(self, client, valid_headers):
        resp = await client.get("/mission", headers=valid_headers)
        assert resp.status_code == 200
        assert "mission" in resp.json()

    @pytest.mark.anyio
    async def test_mission_with_wrong_key(self, client):
        resp = await client.get("/mission", headers={"X-API-Key": "wrong"})
        assert resp.status_code == 403


class TestSettingsEndpoints:
    @pytest.mark.anyio
    async def test_get_current_settings(self, client, valid_headers):
        resp = await client.get("/current_settings", headers=valid_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "confidence_threshold" in data
        assert "vlm_interval" in data
        assert "vlm_provider" in data

    @pytest.mark.anyio
    async def test_update_settings_valid(self, client, valid_headers):
        resp = await client.post(
            "/settings",
            json={"confidence_threshold": 0.5, "vlm_interval": 10},
            headers=valid_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

    @pytest.mark.anyio
    async def test_update_settings_invalid_confidence(self, client, valid_headers):
        resp = await client.post(
            "/settings", json={"confidence_threshold": 99.0}, headers=valid_headers
        )
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_update_settings_invalid_interval(self, client, valid_headers):
        resp = await client.post("/settings", json={"vlm_interval": -5}, headers=valid_headers)
        assert resp.status_code == 422


class TestMissionEndpoints:
    @pytest.mark.anyio
    async def test_update_mission_valid(self, client, valid_headers):
        resp = await client.post(
            "/mission", json={"mission": "Count people in the scene"}, headers=valid_headers
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

    @pytest.mark.anyio
    async def test_update_mission_empty(self, client, valid_headers):
        resp = await client.post("/mission", json={"mission": ""}, headers=valid_headers)
        assert resp.status_code == 422

    @pytest.mark.anyio
    async def test_update_mission_too_long(self, client, valid_headers):
        resp = await client.post("/mission", json={"mission": "x" * 3000}, headers=valid_headers)
        assert resp.status_code == 422


class TestAnalysisEndpoints:
    @pytest.mark.anyio
    async def test_latest_analysis(self, client, valid_headers):
        resp = await client.get("/latest_analysis", headers=valid_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "analysis" in data
        assert "is_thinking" in data
        assert "frame_count" in data

    @pytest.mark.anyio
    async def test_ask_validates_prompt_length(self, client, valid_headers):
        resp = await client.post("/ask", json={"prompt": ""}, headers=valid_headers)
        assert resp.status_code == 422


class TestVideoEndpoints:
    @pytest.mark.anyio
    async def test_video_invalid_camera(self, client, valid_headers):
        resp = await client.get("/video_feed/nonexistent", headers=valid_headers)
        assert resp.status_code == 404


class TestCamerasEndpoint:
    @pytest.mark.anyio
    async def test_list_cameras(self, client, valid_headers):
        resp = await client.get("/cameras", headers=valid_headers)
        assert resp.status_code == 200
        assert "cameras" in resp.json()


class TestTelegramEndpoints:
    @pytest.mark.anyio
    async def test_telegram_status(self, client, valid_headers):
        resp = await client.get("/telegram_status", headers=valid_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "has_token" in data
        assert "subscriber_count" in data
