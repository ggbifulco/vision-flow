import logging
from typing import Any
from ultralytics import YOLO
from src.core.base_model import BaseModel
from src.config.settings import Settings

logger = logging.getLogger(__name__)


class YOLODetector(BaseModel):
    def load_model(self) -> None:
        logger.info(f"Loading YOLO ({Settings.YOLO_MODEL_PATH})...")
        self.model = YOLO(Settings.YOLO_MODEL_PATH)

    def predict(self, frame: Any) -> Any:
        results = self.model.track(
            frame,
            persist=True,
            conf=Settings.CONFIDENCE_THRESHOLD,
            verbose=False,
        )
        return results[0]
