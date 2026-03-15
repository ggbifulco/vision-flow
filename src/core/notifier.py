import logging
import requests
import os
from src.config.settings import Settings

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        self.token = Settings.TELEGRAM_TOKEN
        self.enabled = Settings.ENABLE_NOTIFICATIONS
        self.keywords = Settings.ALERT_KEYWORDS

    def should_alert(self, text):
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)

    def send_telegram_alert(self, text, photo_path=None, chat_ids=None):
        """Send alert to the given chat_ids (or all subscribers if None)."""
        if not self.enabled or not self.token:
            logger.warning(f"Alert detected but Telegram not configured: {text[:50]}...")
            return False

        chat_ids = chat_ids if chat_ids is not None else list(Settings.TELEGRAM_CHAT_IDS)
        if not chat_ids:
            logger.warning("Alert triggered but no subscribers yet (no one pressed /start).")
            return False

        sent = 0
        for chat_id in chat_ids:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{self.token}/sendMessage",
                    data={"chat_id": chat_id, "text": f"🚨 VisionFlow ALERT:\n{text}"},
                    timeout=5,
                )
                if photo_path and os.path.exists(photo_path):
                    with open(photo_path, "rb") as photo:
                        requests.post(
                            f"https://api.telegram.org/bot{self.token}/sendPhoto",
                            data={"chat_id": chat_id},
                            files={"photo": photo},
                            timeout=10,
                        )
                sent += 1
            except Exception as e:
                logger.error(f"Failed to send alert to {chat_id}: {e}")

        logger.info(f"Alert sent to {sent}/{len(chat_ids)} subscribers.")
        return sent > 0
