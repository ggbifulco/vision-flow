import argparse
import logging
import sys

import cv2
import uvicorn

from src.api.app import app
from src.config.settings import Settings
from src.core.engine import VisionFlowEngine


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        import json

        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging() -> None:
    import os

    handler = logging.StreamHandler(sys.stdout)
    if os.getenv("LOG_FORMAT", "").lower() == "json":
        handler.setFormatter(JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%S"))
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S"
            )
        )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers = [handler]


setup_logging()

logger = logging.getLogger(__name__)


def run_local_window() -> None:
    logger.info("VisionFlow: Avvio in modalita Local Window...")
    engine = VisionFlowEngine()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        logger.error("Impossibile accedere alla webcam.")
        return

    logger.info("Stream avviato. Premi 'q' per uscire.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (Settings.DISPLAY_WIDTH, Settings.DISPLAY_HEIGHT))
            processed_frame, _ = engine.process_frame(frame)

            cv2.imshow("VisionFlow - YOLO26 + VLM", processed_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        engine.shutdown()
        logger.info("VisionFlow terminato correttamente.")


def run_web_api() -> None:
    logger.info("VisionFlow: Avvio in modalita Web Server (FastAPI)...")
    logger.info("Endpoint streaming: http://localhost:8000/video_feed")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VisionFlow: Real-time Multimodal Engine")
    parser.add_argument(
        "--mode",
        choices=["local", "web"],
        default="local",
        help="Modalita: 'local' per finestra OpenCV, 'web' per FastAPI server (default: local)",
    )
    args = parser.parse_args()

    if args.mode == "local":
        run_local_window()
    else:
        run_web_api()
