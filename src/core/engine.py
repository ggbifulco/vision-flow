import cv2
import time
import logging
import threading
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
        self.last_analysis = "In attesa di analisi della scena..."
        self.frame_count = 0
        self.is_analyzing = False
        self.last_vlm_time = 0  # Timestamp ultima analisi VLM

    def _run_vlm_analysis(self, frame_original, frame_pil, query):
        """Metodo interno eseguito in un thread separato."""
        self.is_analyzing = True
        try:
            logger.info("Analisi VLM in background avviata...")
            result = self.expert.predict(frame_pil, query)
            self.last_analysis = result

            # 1. Persistenza dati
            screenshot_path = None
            if Settings.SAVE_ANALYSIS:
                screenshot_path = self.storage.save_record(frame_original, self.frame_count, result)

            # 2. Controllo Alert e Notifiche
            if self.notifier.should_alert(result):
                logger.warning(f"ALERT RILEVATO: {result[:50]}...")
                self.notifier.send_telegram_alert(result, screenshot_path)

            logger.info("Analisi VLM completata.")
        except Exception as e:
            logger.error(f"Errore durante l'analisi VLM: {e}", exc_info=True)
            self.last_analysis = f"Errore durante l'analisi VLM: {e}"
        finally:
            self.is_analyzing = False

    def process_frame(self, frame, user_query=None):
        """
        Processa un frame: YOLO (sync) -> Trigger (check) -> VLM (async).
        """
        self.frame_count += 1
        
        # 1. YOLO Detection (Real-time)
        results = self.detector.predict(frame)
        annotated_frame = results.plot()

        # 2. Smart Trigger: YOLO rileva oggetti di interesse -> VLM analizza la scena
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
            
            query = user_query if user_query else Settings.DEFAULT_MISSION
            
            vlm_thread = threading.Thread(
                target=self._run_vlm_analysis, 
                args=(frame_original, frame_pil, query),
                daemon=True
            )
            vlm_thread.start()

        # 3. UI Overlay
        status_label = "Thinking..." if self.is_analyzing else ("Monitoring" if has_interest else "Idle")
        status_color = (0, 165, 255) if self.is_analyzing else ((0, 255, 0) if has_interest else (200, 200, 200))

        cv2.putText(
            annotated_frame,
            f"Mode: YOLO26 + Groq VLM",
            (20, 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
        )
        
        cv2.putText(
            annotated_frame, 
            f"Status: {status_label}", 
            (20, 45), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2
        )

        cv2.putText(
            annotated_frame, 
            f"Last AI: {self.last_analysis[:70]}...", 
            (20, 75), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1
        )

        return annotated_frame, self.last_analysis
