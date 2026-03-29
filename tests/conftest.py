from unittest.mock import patch

import pytest


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def no_state_persistence():
    """Prevent tests from writing to state.json or .env."""
    with (
        patch("src.config.settings.Settings.save_state"),
        patch("src.config.settings.Settings.persist_chat_ids"),
        patch("src.config.settings.Settings.save_telegram_config"),
    ):
        yield
