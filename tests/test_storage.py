import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
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
