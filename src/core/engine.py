import cv2
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from typing import Optional
import numpy as np
from PIL import Image
from src.inference.yolo_detector import YOLODetector
from src.vlm.visual_expert import VisualExpert
from src.core.storage import StorageManager
from src.core.notifier import NotificationManager
from src.config.settings import Settings

logger = logging.getLogger(__name__)

MAX_VLM_WORKERS = 4


class VisionFlowEngine:
    def __init__(self) -> None:
        self.detector = YOLODetector()
        self.expert = VisualExpert()
        self.storage = StorageManager()
        self.notifier = NotificationManager()
        self._last_analysis: str = "Waiting for first analysis..."
        self._frame_count: int = 0
        self._is_analyzing: bool = False
        self._last_vlm_time: float = 0.0
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(
            max_workers=MAX_VLM_WORKERS, thread_name_prefix="vlm"
        )

    # --- Thread-safe properties ---

    @property
    def last_analysis(self) -> str:
        with self._lock:
            return self._last_analysis

    @last_analysis.setter
    def last_analysis(self, value: str) -> None:
        with self._lock:
            self._last_analysis = value

    @property
    def frame_count(self) -> int:
        with self._lock:
            return self._frame_count

    @frame_count.setter
    def frame_count(self, value: int) -> None:
        with self._lock:
            self._frame_count = value

    @property
    def is_analyzing(self) -> bool:
        with self._lock:
            return self._is_analyzing

    @is_analyzing.setter
    def is_analyzing(self, value: bool) -> None:
        with self._lock:
            self._is_analyzing = value

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)

    def _run_vlm_analysis(
        self,
        frame_original: np.ndarray,
        frame_pil: Image.Image,
        query: str,
        target_chat_ids: Optional[list[str]] = None,
    ) -> None:
        self.is_analyzing = True
        try:
            logger.info(f"VLM analysis started (mission: {query[:40]}...)")
            result = self.expert.predict(frame_pil, query)
            self.last_analysis = result

            screenshot_path: Optional[str] = None
            if Settings.SAVE_ANALYSIS:
                screenshot_path = self.storage.save_record(
                    frame_original, self.frame_count, result
                )

            logger.debug(f"VLM result: {result[:120]}")
            logger.debug(f"Keywords: {self.notifier.keywords}")
            logger.debug(f"Subscribers: {Settings.TELEGRAM_CHAT_IDS}")

            if self.notifier.should_alert(result):
                logger.warning(
                    f"ALERT triggered, sending to {target_chat_ids or Settings.TELEGRAM_CHAT_IDS}..."
                )
                self.notifier.send_telegram_alert(
                    result, screenshot_path, chat_ids=target_chat_ids
                )
            else:
                logger.debug("No alert keywords matched — notification skipped.")

            logger.info("VLM analysis complete.")
        except Exception as e:
            logger.error(f"VLM analysis error: {e}", exc_info=True)
            self.last_analysis = f"VLM error: {e}"
        finally:
            self.is_analyzing = False

    def process_frame(
        self, frame: np.ndarray, user_query: Optional[str] = None
    ) -> tuple[np.ndarray, str]:
        self.frame_count += 1

        results = self.detector.predict(frame)

        detected_classes: list[int] = []
        if hasattr(results, "boxes") and results.boxes is not None:
            detected_classes = results.boxes.cls.cpu().numpy().tolist()

        has_interest = any(
            cls_id in Settings.TRIGGER_CLASSES for cls_id in detected_classes
        )
        with self._lock:
            elapsed = time.time() - self._last_vlm_time

        should_trigger_vlm = (user_query is not None) or (
            has_interest and elapsed >= Settings.VLM_INTERVAL and not self.is_analyzing
        )

        if should_trigger_vlm:
            with self._lock:
                self._last_vlm_time = time.time()
            frame_original = frame.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)

            if user_query:
                self._executor.submit(
                    self._run_vlm_analysis, frame_original, frame_pil, user_query
                )
            else:
                mission_to_users: dict[str, list[str]] = defaultdict(list)
                for chat_id in Settings.TELEGRAM_CHAT_IDS:
                    mission = Settings.USER_MISSIONS.get(
                        chat_id, Settings.DEFAULT_MISSION
                    )
                    mission_to_users[mission].append(chat_id)

                if not mission_to_users:
                    mission_to_users[Settings.DEFAULT_MISSION] = []

                for mission, chat_ids in mission_to_users.items():
                    self._executor.submit(
                        self._run_vlm_analysis,
                        frame_original,
                        frame_pil,
                        mission,
                        chat_ids if chat_ids else None,
                    )

        return frame, self.last_analysis
