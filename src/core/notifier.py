import logging
import os
from collections import deque

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import Settings

logger = logging.getLogger(__name__)

_TG_MAX_RETRIES = 3
_FAILED_QUEUE_MAX = 100


class NotificationManager:
    def __init__(self) -> None:
        self.token: str = Settings.TELEGRAM_TOKEN
        self.enabled: bool = Settings.ENABLE_NOTIFICATIONS
        self.keywords: list[str] = Settings.ALERT_KEYWORDS
        self._failed_alerts: deque[dict] = deque(maxlen=_FAILED_QUEUE_MAX)

    def should_alert(self, text: str) -> bool:
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)

    @retry(
        stop=stop_after_attempt(_TG_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _post_message(self, chat_id: str, text: str) -> None:
        resp = requests.post(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=5,
        )
        resp.raise_for_status()

    @retry(
        stop=stop_after_attempt(_TG_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _post_photo(self, chat_id: str, photo_path: str) -> None:
        with open(photo_path, "rb") as photo:
            resp = requests.post(
                f"https://api.telegram.org/bot{self.token}/sendPhoto",
                data={"chat_id": chat_id},
                files={"photo": photo},
                timeout=10,
            )
            resp.raise_for_status()

    def send_message(self, chat_id: str, text: str) -> bool:
        if not self.token:
            return False
        try:
            self._post_message(chat_id, text)
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False

    def send_telegram_alert(
        self,
        text: str,
        photo_path: str | None = None,
        chat_ids: list[str] | None = None,
    ) -> bool:
        if not self.enabled or not self.token:
            logger.warning(f"Alert detected but Telegram not configured: {text[:50]}...")
            return False

        target_ids = chat_ids if chat_ids is not None else list(Settings.TELEGRAM_CHAT_IDS)
        if not target_ids:
            logger.warning("Alert triggered but no subscribers yet (no one pressed /start).")
            return False

        sent = 0
        for chat_id in target_ids:
            try:
                self._post_message(chat_id, f"🚨 VisionFlow ALERT:\n{text}")
                if photo_path and os.path.exists(photo_path):
                    self._post_photo(chat_id, photo_path)
                sent += 1
            except requests.RequestException as e:
                logger.error(f"Failed to send alert to {chat_id} after retries: {e}")
                self._failed_alerts.append(
                    {"chat_id": chat_id, "text": text, "photo_path": photo_path}
                )

        logger.info(f"Alert sent to {sent}/{len(target_ids)} subscribers.")
        return sent > 0

    def retry_failed(self) -> int:
        if not self._failed_alerts:
            return 0
        retried = 0
        pending = list(self._failed_alerts)
        self._failed_alerts.clear()
        for alert in pending:
            try:
                self._post_message(alert["chat_id"], f"🚨 VisionFlow ALERT:\n{alert['text']}")
                if alert.get("photo_path") and os.path.exists(alert["photo_path"]):
                    self._post_photo(alert["chat_id"], alert["photo_path"])
                retried += 1
            except requests.RequestException:
                self._failed_alerts.append(alert)
        if retried:
            logger.info(f"Retried {retried} previously failed alerts.")
        return retried
