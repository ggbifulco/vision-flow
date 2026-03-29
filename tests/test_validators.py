import pytest
from src.api.routes.config import SettingsUpdate, MissionRequest, TelegramSetupRequest
from pydantic import ValidationError


class TestSettingsUpdate:
    def test_valid_confidence(self):
        s = SettingsUpdate(confidence_threshold=0.5)
        assert s.confidence_threshold == 0.5

    def test_rejects_confidence_above_1(self):
        with pytest.raises(ValidationError):
            SettingsUpdate(confidence_threshold=1.5)

    def test_rejects_confidence_below_0(self):
        with pytest.raises(ValidationError):
            SettingsUpdate(confidence_threshold=-0.1)

    def test_valid_interval(self):
        s = SettingsUpdate(vlm_interval=10)
        assert s.vlm_interval == 10

    def test_rejects_interval_zero(self):
        with pytest.raises(ValidationError):
            SettingsUpdate(vlm_interval=0)

    def test_rejects_interval_negative(self):
        with pytest.raises(ValidationError):
            SettingsUpdate(vlm_interval=-5)

    def test_valid_display_width(self):
        s = SettingsUpdate(display_width=1920)
        assert s.display_width == 1920

    def test_rejects_display_width_too_small(self):
        with pytest.raises(ValidationError):
            SettingsUpdate(display_width=50)

    def test_rejects_display_width_too_large(self):
        with pytest.raises(ValidationError):
            SettingsUpdate(display_width=99999)

    def test_allows_none_values(self):
        s = SettingsUpdate()
        assert s.confidence_threshold is None
        assert s.vlm_interval is None


class TestMissionRequest:
    def test_valid_mission(self):
        m = MissionRequest(mission="Count people")
        assert m.mission == "Count people"

    def test_rejects_empty_mission(self):
        with pytest.raises(ValidationError):
            MissionRequest(mission="")

    def test_rejects_too_long_mission(self):
        with pytest.raises(ValidationError):
            MissionRequest(mission="x" * 3000)


class TestTelegramSetupRequest:
    def test_valid_token(self):
        t = TelegramSetupRequest(token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        assert t.token.startswith("1234567890")

    def test_rejects_short_token(self):
        with pytest.raises(ValidationError):
            TelegramSetupRequest(token="short")
