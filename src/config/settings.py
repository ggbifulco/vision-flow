import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv, set_key

load_dotenv()

logger = logging.getLogger(__name__)

_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
_STATE_PATH = Path(__file__).resolve().parent.parent.parent / "outputs" / "state.json"
_STATE_LOCK = threading.Lock()


def _load_state() -> dict[str, Any]:
    if _STATE_PATH.exists():
        try:
            return json.loads(_STATE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load state file: {e}")
    return {}


def _save_state(data: dict[str, Any]) -> None:
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _STATE_LOCK:
        _STATE_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


_state = _load_state()


class Settings:
    # --- YOLO Settings ---
    YOLO_MODEL_PATH: str = "yolo26n.pt"
    CONFIDENCE_THRESHOLD: float = _state.get("confidence_threshold", 0.45)

    # --- VLM Settings (Multi-Provider) ---
    VLM_PROVIDER: str = os.getenv("VLM_PROVIDER", _state.get("vlm_provider", "gemini"))
    VLM_MODEL_ID: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    GEMINI_MODEL_ID: str = "gemini-3.1-flash-lite-preview"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # --- Notification Settings ---
    ENABLE_NOTIFICATIONS: bool = True
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    TELEGRAM_CHAT_IDS: set[str] = set(
        cid.strip()
        for cid in os.getenv("TELEGRAM_CHAT_IDS", os.getenv("TELEGRAM_CHAT_ID", "")).split(",")
        if cid.strip()
    )

    USER_MISSIONS: dict[str, str] = _state.get("user_missions", {})
    ALERT_KEYWORDS: list[str] = _state.get("alert_keywords", ["Armed: YES"])

    # --- Storage Settings ---
    DB_PATH: str = "outputs/visionflow.db"
    SCREENSHOTS_DIR: str = "outputs/screenshots"
    SAVE_ANALYSIS: bool = _state.get("save_analysis", False)

    # --- Security Settings ---
    API_KEY: str = os.getenv("VISIONFLOW_API_KEY", "visionflow_secret_123")

    # --- CORS Settings ---
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")

    # --- Intelligence Settings ---
    DEFAULT_MISSION: str = _state.get(
        "default_mission",
        "Analyze this scene for security threats. Respond in this exact structured format:\n"
        "- People detected: [number]\n"
        "- Armed: [YES / NO]\n"
        "- Weapon type: [type or N/A]\n"
        "- Threat level: [LOW / MEDIUM / HIGH / CRITICAL]\n"
        "- Description: [brief description of the scene and any suspicious behavior]",
    )
    TRIGGER_CLASSES: list[int] = _state.get("trigger_classes", [0])

    # --- Streaming Settings ---
    SOURCES: dict[str, int | str] = _state.get("sources", {"Main": 0})
    FRAME_SKIP: int = 2
    VLM_INTERVAL: int = _state.get("vlm_interval", 5)
    DISPLAY_WIDTH: int = _state.get("display_width", 640)
    DISPLAY_HEIGHT: int = _state.get("display_height", 480)

    # --- Metrics (in-memory counters) ---
    _metrics: dict[str, int | float] = {
        "frames_processed": 0,
        "vlm_calls": 0,
        "alerts_triggered": 0,
        "vlm_errors": 0,
        "uptime_start": time.time(),
    }
    _metrics_lock = threading.Lock()

    @classmethod
    def increment_metric(cls, key: str, value: int = 1) -> None:
        with cls._metrics_lock:
            cls._metrics[key] = cls._metrics.get(key, 0) + value

    @classmethod
    def get_metrics(cls) -> dict[str, Any]:
        with cls._metrics_lock:
            return {**cls._metrics, "uptime_seconds": time.time() - cls._metrics["uptime_start"]}

    @classmethod
    def persist_chat_ids(cls) -> None:
        _ENV_PATH.touch(exist_ok=True)
        set_key(
            str(_ENV_PATH),
            "TELEGRAM_CHAT_IDS",
            ",".join(cls.TELEGRAM_CHAT_IDS),
            quote_mode="never",
        )

    @classmethod
    def save_telegram_config(cls, token: str, chat_id: str) -> None:
        _ENV_PATH.touch(exist_ok=True)
        set_key(str(_ENV_PATH), "TELEGRAM_TOKEN", token)
        set_key(str(_ENV_PATH), "TELEGRAM_CHAT_ID", chat_id)
        cls.TELEGRAM_TOKEN = token
        cls.TELEGRAM_CHAT_ID = chat_id
        os.environ["TELEGRAM_TOKEN"] = token
        os.environ["TELEGRAM_CHAT_ID"] = chat_id
        logger.info("Telegram configuration saved successfully.")

    @classmethod
    def save_state(cls) -> None:
        data = {
            "confidence_threshold": cls.CONFIDENCE_THRESHOLD,
            "vlm_provider": cls.VLM_PROVIDER,
            "vlm_interval": cls.VLM_INTERVAL,
            "trigger_classes": cls.TRIGGER_CLASSES,
            "alert_keywords": cls.ALERT_KEYWORDS,
            "display_width": cls.DISPLAY_WIDTH,
            "display_height": cls.DISPLAY_HEIGHT,
            "save_analysis": cls.SAVE_ANALYSIS,
            "default_mission": cls.DEFAULT_MISSION,
            "user_missions": cls.USER_MISSIONS,
        }
        _save_state(data)
        logger.debug("Application state persisted to disk.")
