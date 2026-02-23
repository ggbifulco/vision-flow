import cv2
from PIL import Image
from src.inference.yolo_detector import YOLODetector
from src.vlm.visual_expert import VisualExpert
from src.config.settings import Settings

class VisionFlowEngine:
    def __init__(self):
        self.detector = YOLODetector()
        self.expert = VisualExpert()
        self.last_analysis = "In attesa di analisi della scena..."
        self.frame_count = 0

    def process_frame(self, frame, user_query=None):
        """
        Processa un singolo frame: rileva oggetti e opzionalmente analizza con VLM.
        """
        self.frame_count += 1
        
        # 1. YOLO Detection (Real-time)
        results = self.detector.predict(frame)
        annotated_frame = results.plot() # Disegna box e label automaticamente

        # 2. VLM Analysis (Trigger basato su frame_count o query utente)
        # Analizziamo ogni 150 frame per bilanciare performance e intelligenza
        should_analyze = (self.frame_count % 150 == 0) or (user_query is not None)
        
        if should_analyze:
            print("[!] Avvio analisi profonda della scena con VLM...")
            # Convertiamo frame OpenCV (BGR) in PIL Image (RGB) per il VLM
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            
            query = user_query if user_query else "Cosa sta succedendo in questa scena? Descrivi brevemente l'azione principale."
            self.last_analysis = self.expert.predict(frame_pil, query)

        # 3. Overlay dell'analisi sul frame video
        cv2.putText(
            annotated_frame, 
            f"AI Analysis: {self.last_analysis[:100]}...", 
            (20, 40), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.7, 
            (0, 0, 255), 
            2
        )

        return annotated_frame, self.last_analysis
