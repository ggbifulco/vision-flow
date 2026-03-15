import logging
import requests
import os
from src.config.settings import Settings

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Gestisce l'invio di notifiche a Telegram o altri servizi (WebHook, Email).
    """
    def __init__(self):
        self.token = Settings.TELEGRAM_TOKEN
        self.chat_id = Settings.TELEGRAM_CHAT_ID
        self.enabled = Settings.ENABLE_NOTIFICATIONS
        self.keywords = Settings.ALERT_KEYWORDS

    def should_alert(self, text):
        """Controlla se il testo dell'analisi contiene parole chiave di allerta."""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.keywords)

    def send_telegram_alert(self, text, photo_path=None):
        """Invia un messaggio (e opzionalmente una foto) su Telegram."""
        if not self.enabled or not self.token or not self.chat_id:
            logger.warning(f"Allerta rilevata ma Telegram non configurato: {text[:50]}...")
            return False

        try:
            # 1. Invia il testo
            url_msg = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {"chat_id": self.chat_id, "text": f"🚨 VisionFlow ALERT:\n{text}"}
            requests.post(url_msg, data=payload)

            # 2. Invia la foto se presente
            if photo_path and os.path.exists(photo_path):
                url_photo = f"https://api.telegram.org/bot{self.token}/sendPhoto"
                with open(photo_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {'chat_id': self.chat_id}
                    requests.post(url_photo, data=data, files=files)
            
            logger.info("Notifica Telegram inviata con successo.")
            return True
        except Exception as e:
            logger.error(f"Impossibile inviare notifica: {e}")
            return False
