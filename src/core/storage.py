import csv
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import cv2
import numpy as np
from src.config.settings import Settings

logger = logging.getLogger(__name__)


class StorageManager:
    def __init__(self) -> None:
        self.logs_path = Path(Settings.LOGS_PATH)
        self.screenshots_dir = Path(Settings.SCREENSHOTS_DIR)
        self._ensure_dirs()
        self._init_csv()

    def _ensure_dirs(self) -> None:
        self.logs_path.parent.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def _init_csv(self) -> None:
        if not self.logs_path.exists():
            with open(self.logs_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["Timestamp", "Frame_ID", "Analysis_Result", "Screenshot_Path"]
                )

    def save_record(
        self, frame: np.ndarray, frame_id: int, analysis_text: str
    ) -> Optional[str]:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        screenshot_filename = f"capture_{file_timestamp}_f{frame_id}.jpg"
        screenshot_path = self.screenshots_dir / screenshot_filename
        cv2.imwrite(str(screenshot_path), frame)

        with open(self.logs_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, frame_id, analysis_text, str(screenshot_path)])

        logger.debug(f"Salvataggio completato: {screenshot_filename}")
        return str(screenshot_path)
