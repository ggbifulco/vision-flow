import logging
import threading
import time

import cv2
import numpy as np

from src.config.settings import Settings

logger = logging.getLogger(__name__)

MAX_RECONNECT_DELAY = 30


class StreamManager:
    def __init__(self, sources: dict | None = None) -> None:
        self.sources = sources if sources is not None else Settings.SOURCES
        self.caps: dict[str, cv2.VideoCapture] = {}
        self._reconnect_attempts: dict[str, int] = {}
        self._reconnect_delay: dict[str, float] = {}
        self._reconnecting: dict[str, bool] = {}
        self.connect_all()

    def connect_all(self) -> None:
        for name, src in self.sources.items():
            self.connect(name, src)

    def connect(self, name: str, source) -> None:
        logger.info(f"Connessione a '{name}' ({source})...")
        cap = cv2.VideoCapture(source)
        if isinstance(source, str) and source.startswith("rtsp"):
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.caps[name] = cap

    def get_frame(self, name: str) -> tuple[bool, np.ndarray | None]:
        cap = self.caps.get(name)
        if cap is None or not cap.isOpened():
            self._schedule_reconnect(name)
            return False, None

        ret, frame = cap.read()
        if not ret:
            logger.warning(f"Errore lettura '{name}'. Riprovo...")
            cap.release()
            self._schedule_reconnect(name)
            return False, None

        self._reconnect_attempts[name] = 0
        self._reconnect_delay[name] = 0.0

        return True, frame

    def _schedule_reconnect(self, name: str) -> None:
        if name not in self.sources:
            logger.warning(f"Camera '{name}' not found in sources")
            return

        if self._reconnecting.get(name):
            return

        self._reconnecting[name] = True

        def _do_reconnect() -> None:
            try:
                attempts = self._reconnect_attempts.get(name, 0) + 1
                self._reconnect_attempts[name] = attempts
                delay = min(2 ** (attempts - 1), MAX_RECONNECT_DELAY)
                self._reconnect_delay[name] = delay
                logger.debug(f"Reconnect '{name}' attempt #{attempts}, waiting {delay:.1f}s")
                time.sleep(delay)
                self.connect(name, self.sources[name])
            finally:
                self._reconnecting[name] = False

        threading.Thread(target=_do_reconnect, daemon=True).start()

    def release_all(self) -> None:
        for name, cap in self.caps.items():
            cap.release()
            logger.debug(f"Released capture '{name}'")
        self.caps.clear()
        cv2.destroyAllWindows()
