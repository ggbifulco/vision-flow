import cv2
import logging
from src.config.settings import Settings

logger = logging.getLogger(__name__)

class StreamManager:
    """
    Gestisce più catture video contemporaneamente (Webcam, RTSP, File).
    """
    def __init__(self, sources=None):
        self.sources = sources if sources is not None else Settings.SOURCES
        self.caps = {}
        self.connect_all()

    def connect_all(self):
        """Inizializza la connessione per tutte le sorgenti configurate."""
        for name, src in self.sources.items():
            self.connect(name, src)

    def connect(self, name, source):
        """Apre una singola sorgente video."""
        logger.info(f"Connessione a '{name}' ({source})...")
        cap = cv2.VideoCapture(source)
        if isinstance(source, str) and source.startswith("rtsp"):
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.caps[name] = cap

    def get_frame(self, name):
        """Legge un frame da una specifica telecamera."""
        cap = self.caps.get(name)
        if cap is None or not cap.isOpened():
            self.connect(name, self.sources[name])
            return False, None

        ret, frame = cap.read()
        if not ret:
            logger.warning(f"Errore lettura '{name}'. Riprovo...")
            cap.release()
            self.connect(name, self.sources[name])
            return False, None

        return True, frame

    def release_all(self):
        for cap in self.caps.values():
            cap.release()
        cv2.destroyAllWindows()
