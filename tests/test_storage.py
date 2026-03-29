from unittest.mock import patch

import pytest

from src.core.storage import StorageManager


@pytest.fixture
def temp_storage(tmp_path):
    db_path = str(tmp_path / "test.db")
    screenshots_dir = str(tmp_path / "screenshots")
    with (
        patch("src.config.settings.Settings.DB_PATH", db_path),
        patch("src.config.settings.Settings.SCREENSHOTS_DIR", screenshots_dir),
    ):
        sm = StorageManager()
        yield sm


class TestStorageManager:
    def test_save_record(self, temp_storage):
        import numpy as np

        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        path = temp_storage.save_record(frame, 1, "Test analysis - Threat level: HIGH")
        assert path is not None

    def test_save_record_extracts_threat_level(self, temp_storage):
        import numpy as np

        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        temp_storage.save_record(frame, 1, "Threat level: CRITICAL")
        history = temp_storage.get_history(limit=1)
        assert history[0]["threat_level"] == "CRITICAL"

    def test_save_alert(self, temp_storage):
        import numpy as np

        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        temp_storage.save_alert(frame, 1, "Armed: YES", "/tmp/test.jpg")
        history = temp_storage.get_history(alerts_only=True)
        assert len(history) == 1
        assert history[0]["is_alert"] is True

    def test_get_history_limit(self, temp_storage):
        import numpy as np

        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        for i in range(10):
            temp_storage.save_record(frame, i, f"Analysis {i}")
        history = temp_storage.get_history(limit=5)
        assert len(history) == 5
        assert history[0]["result"] == "Analysis 9"

    def test_get_history_alerts_only(self, temp_storage):
        import numpy as np

        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        temp_storage.save_record(frame, 1, "Normal")
        temp_storage.save_alert(frame, 2, "Armed: YES", "")
        temp_storage.save_record(frame, 3, "Normal")
        alerts = temp_storage.get_history(alerts_only=True)
        assert len(alerts) == 1
        assert alerts[0]["frame_id"] == 2

    def test_get_stats(self, temp_storage):
        import numpy as np

        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        temp_storage.save_record(frame, 1, "Test")
        temp_storage.save_alert(frame, 2, "Alert", "")
        stats = temp_storage.get_stats()
        assert stats["total_analyses"] == 2
        assert stats["total_alerts"] == 1
        assert stats["last_analysis"] is not None
