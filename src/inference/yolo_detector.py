from ultralytics import YOLO
from src.core.base_model import BaseModel
from src.config.settings import Settings

class YOLODetector(BaseModel):
    def load_model(self):
        print(f"[*] Caricamento YOLOv11 su {self.device}...")
        self.model = YOLO(Settings.YOLO_MODEL_PATH).to(self.device)

    def predict(self, frame):
        results = self.model.track(
            frame, 
            persist=True, 
            conf=Settings.CONFIDENCE_THRESHOLD,
            verbose=False
        )
        return results[0]
