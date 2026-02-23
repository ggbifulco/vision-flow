import torch

class Settings:
    # Hardware
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    # YOLO Settings
    YOLO_MODEL_PATH = "yolo11n.pt" # Verrà scaricato automaticamente
    CONFIDENCE_THRESHOLD = 0.45
    
    # VLM Settings
    VLM_MODEL_ID = "vikhyatk/moondream2"
    REVISION = "2024-05-20"
    
    # Streaming Settings
    FRAME_SKIP = 2 # Processa 1 frame ogni 2 per risparmiare risorse
    DISPLAY_WIDTH = 1280
    DISPLAY_HEIGHT = 720
