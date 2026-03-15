import os
from pathlib import Path
from dotenv import load_dotenv, set_key

# Load environment variables from .env file (for persistent config)
load_dotenv()

# Path to the .env file at project root
_ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings:
    # --- YOLO Settings ---
    YOLO_MODEL_PATH = "yolo26n.pt"  # Path to the YOLO model weights (auto-downloaded)
    CONFIDENCE_THRESHOLD = 0.45  # Minimum confidence for YOLO detections

    # --- VLM Settings (Multi-Provider) ---
    VLM_PROVIDER = os.getenv("VLM_PROVIDER", "gemini")  # "groq" or "gemini"
    VLM_MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"  # Groq-hosted VLM model
    GEMINI_MODEL_ID = "gemini-3.1-flash-lite-preview"  # Google Gemini model
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Groq API key loaded from .env
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Google Gemini API key loaded from .env

    # --- Notification Settings ---
    ENABLE_NOTIFICATIONS = True  # Enable/disable Telegram alert notifications
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")  # Telegram bot token
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")  # Legacy single chat ID (kept for .env compat)
    TELEGRAM_CHAT_IDS: set = set(
        cid.strip() for cid in os.getenv("TELEGRAM_CHAT_IDS", os.getenv("TELEGRAM_CHAT_ID", "")).split(",") if cid.strip()
    )  # Set of all subscribed chat IDs (supports multiple users)

    USER_MISSIONS: dict = {}  # Per-user mission: {chat_id: mission_text}
    ALERT_KEYWORDS = [  # Keywords that trigger alert notifications when found in VLM output
        "Armed: YES"
    ]

    # --- Storage Settings ---
    LOGS_PATH = "outputs/analysis_logs.csv"  # CSV log file path for analysis records
    SCREENSHOTS_DIR = "outputs/screenshots"  # Directory for saved alert screenshots
    SAVE_ANALYSIS = False  # Whether to persist analysis results to disk

    # --- Security Settings ---
    API_KEY = os.getenv("VISIONFLOW_API_KEY", "visionflow_secret_123")  # API key for the REST interface

    # --- Intelligence Settings ---
    DEFAULT_MISSION = (  # Default prompt sent to VLM when no user query is provided
        "Analyze this scene for security threats. Respond in this exact structured format:\n"
        "- People detected: [number]\n"
        "- Armed: [YES / NO]\n"
        "- Weapon type: [type or N/A]\n"
        "- Threat level: [LOW / MEDIUM / HIGH / CRITICAL]\n"
        "- Description: [brief description of the scene and any suspicious behavior]"
    )
    TRIGGER_CLASSES = [0]  # YOLO class IDs that trigger VLM analysis

    # --- Streaming Settings ---
    SOURCES = {  # Video source dictionary: {"name": source}
        "Main": 0,  # Local webcam
    }
    FRAME_SKIP = 2  # Process every Nth frame to reduce CPU load
    VLM_INTERVAL = 5  # Minimum seconds between consecutive VLM analyses
    DISPLAY_WIDTH = 640  # Display window width in pixels
    DISPLAY_HEIGHT = 480  # Display window height in pixels

    @classmethod
    def persist_chat_ids(cls):
        """Persist current TELEGRAM_CHAT_IDS to .env so they survive restarts."""
        _ENV_PATH.touch(exist_ok=True)
        set_key(str(_ENV_PATH), "TELEGRAM_CHAT_IDS", ",".join(cls.TELEGRAM_CHAT_IDS), quote_mode="never")

    @classmethod
    def save_telegram_config(cls, token: str, chat_id: str):
        """Persist Telegram credentials to .env without overwriting other keys."""
        # Ensure the .env file exists
        _ENV_PATH.touch(exist_ok=True)

        # Update only the Telegram keys, preserving everything else
        set_key(str(_ENV_PATH), "TELEGRAM_TOKEN", token)
        set_key(str(_ENV_PATH), "TELEGRAM_CHAT_ID", chat_id)

        # Also update the in-memory values for the current session
        cls.TELEGRAM_TOKEN = token
        cls.TELEGRAM_CHAT_ID = chat_id
        os.environ["TELEGRAM_TOKEN"] = token
        os.environ["TELEGRAM_CHAT_ID"] = chat_id
        import logging
        logging.getLogger(__name__).info("Telegram configuration saved successfully.")
