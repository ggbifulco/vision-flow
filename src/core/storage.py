import os
import logging
import cv2
import csv
from datetime import datetime
from src.config.settings import Settings

logger = logging.getLogger(__name__)

class StorageManager:
    """
    Gestisce il salvataggio delle analisi (testo) e degli screenshot (immagini).
    """
    def __init__(self):
        self.logs_path = Settings.LOGS_PATH
        self.screenshots_dir = Settings.SCREENSHOTS_DIR
        self._ensure_dirs()
        self._init_csv()

    def _ensure_dirs(self):
        """Crea le cartelle necessarie se non esistono."""
        os.makedirs(os.path.dirname(self.logs_path), exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def _init_csv(self):
        """Inizializza il file CSV con l'intestazione se è nuovo."""
        if not os.path.exists(self.logs_path):
            with open(self.logs_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Frame_ID', 'Analysis_Result', 'Screenshot_Path'])

    def save_record(self, frame, frame_id, analysis_text):
        """
        Salva l'analisi nel CSV e lo screenshot su disco.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Salva Screenshot
        screenshot_filename = f"capture_{file_timestamp}_f{frame_id}.jpg"
        screenshot_path = os.path.join(self.screenshots_dir, screenshot_filename)
        cv2.imwrite(screenshot_path, frame)
        
        # 2. Salva nel Log CSV
        with open(self.logs_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, frame_id, analysis_text, screenshot_path])
        
        logger.info(f"Salvataggio completato: {screenshot_filename}")
        return screenshot_path
