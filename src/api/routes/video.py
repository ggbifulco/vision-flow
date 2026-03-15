import time
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import cv2
from src.api.deps import get_api_key, get_engine, get_stream_manager
from src.config.settings import Settings

router = APIRouter(prefix="/video_feed", tags=["Video"])

def generate_frames(cam_id: str):
    vfe = get_engine()
    sm = get_stream_manager()
    while True:
        success, frame = sm.get_frame(cam_id)
        if not success:
            time.sleep(0.05)
            continue
        frame = cv2.resize(frame, (Settings.DISPLAY_WIDTH, Settings.DISPLAY_HEIGHT))
        processed_frame, _ = vfe.process_frame(frame)
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@router.get("/{cam_id}")
async def video_feed(cam_id: str, api_key: str = Depends(get_api_key)):
    if cam_id not in Settings.SOURCES:
        raise HTTPException(status_code=404, detail="Camera not found")
    return StreamingResponse(generate_frames(cam_id), media_type="multipart/x-mixed-replace; boundary=frame")
