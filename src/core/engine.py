import cv2
import time
import logging
import threading
from collections import defaultdict
from PIL import Image
from src.inference.yolo_detector import YOLODetector
from src.vlm.visual_expert import VisualExpert
from src.core.storage import StorageManager
from src.core.notifier import NotificationManager
from src.config.settings import Settings

logger = logging.getLogger(__name__)

class VisionFlowEngine:
    def __init__(self):
        self.detector = YOLODetector()
        self.expert = VisualExpert()
        self.storage = StorageManager()
        self.notifier = NotificationManager()
        self.last_analysis = "Waiting for first analysis..."
        self.frame_count = 0
        self.is_analyzing = False
        self.last_vlm_time = 0

    def _run_vlm_analysis(self, frame_original, frame_pil, query, target_chat_ids=None):
        """Run VLM for a given mission and notify only the subscribers of that mission."""
        self.is_analyzing = True
        try:
            logger.info(f"VLM analysis started (mission: {query[:40]}...)")
            result = self.expert.predict(frame_pil, query)
            self.last_analysis = result

            screenshot_path = None
            if Settings.SAVE_ANALYSIS:
                screenshot_path = self.storage.save_record(frame_original, self.frame_count, result)

            logger.info(f"VLM result: {result[:120]}")
            logger.info(f"Keywords: {self.notifier.keywords}")
            logger.info(f"Subscribers: {Settings.TELEGRAM_CHAT_IDS}")
            if self.notifier.should_alert(result):
                logger.warning(f"ALERT triggered, sending to {target_chat_ids or Settings.TELEGRAM_CHAT_IDS}...")
                self.notifier.send_telegram_alert(result, screenshot_path, chat_ids=target_chat_ids)
            else:
                logger.info("No alert keywords matched — notification skipped.")

            logger.info("VLM analysis complete.")
        except Exception as e:
            logger.error(f"VLM analysis error: {e}", exc_info=True)
            self.last_analysis = f"VLM error: {e}"
        finally:
            self.is_analyzing = False

    def process_frame(self, frame, user_query=None):
        """
        Process a frame: YOLO (sync) -> Trigger (check) -> VLM per-mission (async).
        """
        self.frame_count += 1

        # 1. YOLO Detection (internal trigger only, no overlay on stream)
        results = self.detector.predict(frame)

        detected_classes = []
        if hasattr(results, 'boxes') and results.boxes is not None:
            detected_classes = results.boxes.cls.cpu().numpy().tolist()

        has_interest = any(cls_id in Settings.TRIGGER_CLASSES for cls_id in detected_classes)
        elapsed = time.time() - self.last_vlm_time

        should_trigger_vlm = (user_query is not None) or (
            has_interest and elapsed >= Settings.VLM_INTERVAL and not self.is_analyzing
        )

        if should_trigger_vlm:
            self.last_vlm_time = time.time()
            frame_original = frame.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)

            if user_query:
                # Dashboard query: use default mission, no per-user targeting
                threading.Thread(
                    target=self._run_vlm_analysis,
                    args=(frame_original, frame_pil, user_query),
                    daemon=True,
                ).start()
            else:
                # Group subscribers by their mission, fire one VLM call per unique mission
                mission_to_users = defaultdict(list)
                for chat_id in Settings.TELEGRAM_CHAT_IDS:
                    mission = Settings.USER_MISSIONS.get(chat_id, Settings.DEFAULT_MISSION)
                    mission_to_users[mission].append(chat_id)

                # If no subscribers, still run with the default mission for the dashboard
                if not mission_to_users:
                    mission_to_users[Settings.DEFAULT_MISSION] = []

                for mission, chat_ids in mission_to_users.items():
                    threading.Thread(
                        target=self._run_vlm_analysis,
                        args=(frame_original, frame_pil, mission, chat_ids if chat_ids else None),
                        daemon=True,
                    ).start()

        # 2. Return clean frame (no boxes, no text overlay)
        return frame, self.last_analysis
