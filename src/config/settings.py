import logging
import os
from pathlib import Path
from dotenv import load_dotenv, set_key

load_dotenv()

logger = logging.getLogger(__name__)

_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings:
    # --- YOLO Settings ---
    YOLO_MODEL_PATH: str = "yolo26n.pt"
    CONFIDENCE_THRESHOLD: float = 0.45

    # --- VLM Settings (Multi-Provider) ---
    VLM_PROVIDER: str = os.getenv("VLM_PROVIDER", "gemini")
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
        for cid in os.getenv(
            "TELEGRAM_CHAT_IDS", os.getenv("TELEGRAM_CHAT_ID", "")
        ).split(",")
        if cid.strip()
    )

    USER_MISSIONS: dict[str, str] = {}
    ALERT_KEYWORDS: list[str] = ["Armed: YES"]

    # --- Storage Settings ---
    LOGS_PATH: str = "outputs/analysis_logs.csv"
    SCREENSHOTS_DIR: str = "outputs/screenshots"
    SAVE_ANALYSIS: bool = False

    # --- Security Settings ---
    API_KEY: str = os.getenv("VISIONFLOW_API_KEY", "visionflow_secret_123")

    # --- Intelligence Settings ---
    DEFAULT_MISSION: str = (
        "Analyze this scene for security threats. Respond in this exact structured format:\n"
        "- People detected: [number]\n"
        "- Armed: [YES / NO]\n"
        "- Weapon type: [type or N/A]\n"
        "- Threat level: [LOW / MEDIUM / HIGH / CRITICAL]\n"
        "- Description: [brief description of the scene and any suspicious behavior]"
    )
    TRIGGER_CLASSES: list[int] = [0]

    # --- Streaming Settings ---
    SOURCES: dict[str, int | str] = {"Main": 0}
    FRAME_SKIP: int = 2
    VLM_INTERVAL: int = 5
    DISPLAY_WIDTH: int = 640
    DISPLAY_HEIGHT: int = 480

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
