import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
from src.api.deps import get_api_key, get_engine
from src.config.settings import Settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Config"])

from typing import Optional

class TelegramSetupRequest(BaseModel):
    token: str

class MissionRequest(BaseModel):
    mission: str

class SettingsUpdate(BaseModel):
    confidence_threshold: Optional[float] = None
    vlm_interval: Optional[int] = None
    trigger_classes: Optional[list[int]] = None
    alert_keywords: Optional[list[str]] = None
    display_width: Optional[int] = None
    display_height: Optional[int] = None
    save_analysis: Optional[bool] = None
    vlm_provider: Optional[str] = None

@router.get("/mission")
async def get_mission(api_key: str = Depends(get_api_key)):
    return {"mission": Settings.DEFAULT_MISSION}

@router.post("/mission")
async def update_mission(request: MissionRequest, api_key: str = Depends(get_api_key)):
    Settings.DEFAULT_MISSION = request.mission
    logger.info(f"New AI mission: {request.mission}")
    return {"status": "success", "new_mission": request.mission}

@router.post("/settings")
async def update_settings(request: SettingsUpdate, api_key: str = Depends(get_api_key)):
    if request.confidence_threshold is not None:
        Settings.CONFIDENCE_THRESHOLD = request.confidence_threshold
    if request.vlm_interval is not None:
        Settings.VLM_INTERVAL = request.vlm_interval
    if request.trigger_classes is not None:
        Settings.TRIGGER_CLASSES = request.trigger_classes
    if request.alert_keywords is not None:
        Settings.ALERT_KEYWORDS = request.alert_keywords
        vfe = get_engine()
        if vfe:
            vfe.notifier.keywords = request.alert_keywords
    if request.display_width is not None:
        Settings.DISPLAY_WIDTH = request.display_width
    if request.display_height is not None:
        Settings.DISPLAY_HEIGHT = request.display_height
    if request.save_analysis is not None:
        Settings.SAVE_ANALYSIS = request.save_analysis
    if request.vlm_provider is not None and request.vlm_provider in ("groq", "gemini"):
        vfe = get_engine()
        if vfe:
            vfe.expert.switch_provider(request.vlm_provider)
    logger.info("Settings updated from dashboard")
    return {"status": "success"}

@router.get("/cameras")
async def list_cameras(api_key: str = Depends(get_api_key)):
    return {"cameras": list(Settings.SOURCES.keys())}

@router.post("/register_token")
async def register_token(request: TelegramSetupRequest, api_key: str = Depends(get_api_key)):
    url = f"https://api.telegram.org/bot{request.token}/getMe"
    try:
        response = requests.get(url)
        data = response.json()
        if not data.get("ok"): return JSONResponse(content={"error": "Invalid"}, status_code=400)
        Settings.TELEGRAM_TOKEN = request.token
        return {"bot_username": data["result"]["username"]}
    except Exception as e: return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/poll_chat_id")
async def poll_chat_id(api_key: str = Depends(get_api_key)):
    token = Settings.TELEGRAM_TOKEN
    if not token: return JSONResponse(content={"error": "No token"}, status_code=400)
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getUpdates")
        data = response.json()
        if data.get("ok") and len(data["result"]) > 0:
            chat_id = str(data["result"][-1]["message"]["chat"]["id"])
            Settings.save_telegram_config(token, chat_id)
            if vfe := get_engine():
                vfe.notifier.token = token
                vfe.notifier.chat_id = chat_id
            return {"status": "success", "chat_id": chat_id}
        return {"status": "waiting"}
    except Exception as e: return JSONResponse(content={"error": str(e)}, status_code=500)
