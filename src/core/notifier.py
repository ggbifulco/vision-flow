import logging
import os
from typing import Optional
import requests
from src.config.settings import Settings

logger = logging.getLogger(__name__)


class NotificationManager:
    def __init__(self) -> None:
        self.token: str = Settings.TELEGRAM_TOKEN
        self.enabled: bool = Settings.ENABLE_NOTIFICATIONS
        self.keywords: list[str] = Settings.ALERT_KEYWORDS

    def should_alert(self, text: str) -> bool:
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)

    def send_message(self, chat_id: str, text: str) -> bool:
        if not self.token:
            return False
        try:
            requests.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                data={"chat_id": chat_id, "text": text},
                timeout=5,
            )
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False

    def send_telegram_alert(
        self,
        text: str,
        photo_path: Optional[str] = None,
        chat_ids: Optional[list[str]] = None,
    ) -> bool:
        if not self.enabled or not self.token:
            logger.warning(
                f"Alert detected but Telegram not configured: {text[:50]}..."
            )
            return False

        target_ids = (
            chat_ids if chat_ids is not None else list(Settings.TELEGRAM_CHAT_IDS)
        )
        if not target_ids:
            logger.warning(
                "Alert triggered but no subscribers yet (no one pressed /start)."
            )
            return False

        sent = 0
        for chat_id in target_ids:
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
            except requests.RequestException as e:
                logger.error(f"Failed to send alert to {chat_id}: {e}")

        logger.info(f"Alert sent to {sent}/{len(target_ids)} subscribers.")
        return sent > 0
