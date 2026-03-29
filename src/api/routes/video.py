import time
from typing import Generator

import cv2
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from src.api.deps import limiter, get_api_key, get_engine, get_stream_manager
from src.config.settings import Settings

router = APIRouter(prefix="/video_feed", tags=["Video"])

JPEG_QUALITY = 75
RESIZE_PARAMS = [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]


def generate_frames(cam_id: str) -> Generator[bytes, None, None]:
    vfe = get_engine()
    sm = get_stream_manager()
    target_w = Settings.DISPLAY_WIDTH
    target_h = Settings.DISPLAY_HEIGHT
    while True:
        success, frame = sm.get_frame(cam_id)
        if not success:
            time.sleep(0.05)
            continue

        h, w = frame.shape[:2]
        if w != target_w or h != target_h:
            frame = cv2.resize(frame, (target_w, target_h))

        processed_frame, _ = vfe.process_frame(frame)
        ret, buffer = cv2.imencode(".jpg", processed_frame, RESIZE_PARAMS)
        if not ret:
            continue
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")


@router.get("/{cam_id}")
@limiter.limit("60/minute")
async def video_feed(
    request: Request, cam_id: str, api_key: str = Depends(get_api_key)
) -> StreamingResponse:
    if cam_id not in Settings.SOURCES:
        raise HTTPException(status_code=404, detail="Camera not found")
    return StreamingResponse(
        generate_frames(cam_id),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
