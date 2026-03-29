import json
import logging
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from src.config.settings import Settings

logger = logging.getLogger(__name__)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS analyses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    frame_id INTEGER,
    result TEXT NOT NULL,
    threat_level TEXT,
    is_alert INTEGER DEFAULT 0,
    screenshot_path TEXT
);

CREATE INDEX IF NOT EXISTS idx_analyses_ts ON analyses(timestamp);
CREATE INDEX IF NOT EXISTS idx_analyses_alert ON analyses(is_alert);
"""


class StorageManager:
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = Path(db_path or Settings.DB_PATH)
        self.screenshots_dir = Path(Settings.SCREENSHOTS_DIR)
        self._ensure_dirs()
        self._lock = threading.Lock()
        self._init_db()

    def _ensure_dirs(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            conn.executescript(_SCHEMA)

    def _extract_threat_level(self, text: str) -> Optional[str]:
        for level in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
            if level in text.upper():
                return level
        return None

    def save_record(self, frame: np.ndarray, frame_id: int, analysis_text: str) -> Optional[str]:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        threat_level = self._extract_threat_level(analysis_text)

        screenshot_filename = f"capture_{file_timestamp}_f{frame_id}.jpg"
        screenshot_path = self.screenshots_dir / screenshot_filename
        cv2.imwrite(str(screenshot_path), frame)

        with self._lock:
            with self._get_conn() as conn:
                conn.execute(
                    "INSERT INTO analyses (timestamp, frame_id, result, threat_level, screenshot_path) VALUES (?, ?, ?, ?, ?)",
                    (timestamp, frame_id, analysis_text, threat_level, str(screenshot_path)),
                )

        logger.debug(f"Saved analysis record: {screenshot_filename}")
        return str(screenshot_path)

    def save_alert(
        self, frame: np.ndarray, frame_id: int, analysis_text: str, screenshot_path: str
    ) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        threat_level = self._extract_threat_level(analysis_text)

        with self._lock:
            with self._get_conn() as conn:
                conn.execute(
                    "INSERT INTO analyses (timestamp, frame_id, result, threat_level, is_alert, screenshot_path) VALUES (?, ?, ?, ?, 1, ?)",
                    (timestamp, frame_id, analysis_text, threat_level, screenshot_path),
                )

    def get_history(self, limit: int = 50, alerts_only: bool = False) -> list[dict]:
        query = "SELECT id, timestamp, frame_id, result, threat_level, is_alert, screenshot_path FROM analyses"
        if alerts_only:
            query += " WHERE is_alert = 1"
        query += " ORDER BY id DESC LIMIT ?"

        with self._lock:
            with self._get_conn() as conn:
                rows = conn.execute(query, (limit,)).fetchall()

        return [
            {
                "id": r[0],
                "timestamp": r[1],
                "frame_id": r[2],
                "result": r[3],
                "threat_level": r[4],
                "is_alert": bool(r[5]),
                "screenshot_path": r[6],
            }
            for r in rows
        ]

    def get_stats(self) -> dict:
        with self._lock:
            with self._get_conn() as conn:
                total = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
                alerts = conn.execute(
                    "SELECT COUNT(*) FROM analyses WHERE is_alert = 1"
                ).fetchone()[0]
                last_ts = conn.execute(
                    "SELECT timestamp FROM analyses ORDER BY id DESC LIMIT 1"
                ).fetchone()
        return {
            "total_analyses": total,
            "total_alerts": alerts,
            "last_analysis": last_ts[0] if last_ts else None,
        }
