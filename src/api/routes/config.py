import logging
import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import requests
from dotenv import set_key
from src.api.deps import get_api_key, get_engine
from src.config.settings import Settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Config"])


class TelegramSetupRequest(BaseModel):
    token: str = Field(..., min_length=10, max_length=100)


class MissionRequest(BaseModel):
    mission: str = Field(..., min_length=1, max_length=2000)


class SettingsUpdate(BaseModel):
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    vlm_interval: Optional[int] = Field(None, ge=1, le=3600)
    trigger_classes: Optional[list[int]] = None
    alert_keywords: Optional[list[str]] = None
    display_width: Optional[int] = Field(None, ge=160, le=3840)
    display_height: Optional[int] = Field(None, ge=120, le=2160)
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


@router.get("/telegram_status")
async def telegram_status(api_key: str = Depends(get_api_key)):
    has_token = bool(Settings.TELEGRAM_TOKEN)
    bot_username = None
    if has_token:
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{Settings.TELEGRAM_TOKEN}/getMe",
                timeout=5,
            )
            d = r.json()
            if d.get("ok"):
                bot_username = d["result"]["username"]
        except requests.RequestException:
            pass
    return {
        "has_token": has_token,
        "bot_username": bot_username,
        "subscriber_count": len(Settings.TELEGRAM_CHAT_IDS),
    }


@router.post("/telegram_test")
async def telegram_test(api_key: str = Depends(get_api_key)):
    token = Settings.TELEGRAM_TOKEN
    chat_ids = list(Settings.TELEGRAM_CHAT_IDS)
    if not token:
        return JSONResponse(
            content={"error": "No bot token configured."}, status_code=400
        )
    if not chat_ids:
        return JSONResponse(
            content={
                "error": "No subscribers yet. Open your bot in Telegram and press Start first."
            },
            status_code=400,
        )
    vfe = get_engine()
    sent = 0
    for cid in chat_ids:
        if vfe.notifier.send_message(
            cid, "🧪 VisionFlow test alert — connection is working!"
        ):
            sent += 1
    return {"sent": sent, "total": len(chat_ids)}


@router.get("/current_settings")
async def current_settings(api_key: str = Depends(get_api_key)):
    return {
        "confidence_threshold": Settings.CONFIDENCE_THRESHOLD,
        "vlm_interval": Settings.VLM_INTERVAL,
        "trigger_classes": Settings.TRIGGER_CLASSES,
        "alert_keywords": Settings.ALERT_KEYWORDS,
        "display_width": Settings.DISPLAY_WIDTH,
        "display_height": Settings.DISPLAY_HEIGHT,
        "save_analysis": Settings.SAVE_ANALYSIS,
        "vlm_provider": Settings.VLM_PROVIDER,
        "default_mission": Settings.DEFAULT_MISSION,
    }


@router.get("/cameras")
async def list_cameras(api_key: str = Depends(get_api_key)):
    return {"cameras": list(Settings.SOURCES.keys())}


@router.post("/register_token")
async def register_token(
    request: TelegramSetupRequest, api_key: str = Depends(get_api_key)
):
    url = f"https://api.telegram.org/bot{request.token}/getMe"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if not data.get("ok"):
            return JSONResponse(
                content={
                    "error": "Invalid token — make sure you copied it correctly from BotFather."
                },
                status_code=400,
            )
        # Persist token to .env so it survives restarts
        env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
        env_path.touch(exist_ok=True)
        set_key(str(env_path), "TELEGRAM_TOKEN", request.token, quote_mode="never")
        Settings.TELEGRAM_TOKEN = request.token
        os.environ["TELEGRAM_TOKEN"] = request.token

        vfe = get_engine()
        vfe.notifier.token = request.token
        logger.info(f"Telegram bot configured: @{data['result']['username']}")

        # Auto-register anyone who already interacted with this bot
        token = request.token
        try:
            upd = requests.get(
                f"https://api.telegram.org/bot{token}/getUpdates", timeout=5
            ).json()
            for update in upd.get("result", []):
                chat_id = str(update.get("message", {}).get("chat", {}).get("id", ""))
                if chat_id and chat_id not in Settings.TELEGRAM_CHAT_IDS:
                    Settings.TELEGRAM_CHAT_IDS.add(chat_id)
                    Settings.persist_chat_ids()
                    vfe.notifier.send_message(
                        chat_id,
                        "✅ Connected to VisionFlow! You'll receive alerts when threats are detected.\n\nSend /stop to unsubscribe.",
                    )
                    logger.info(f"Auto-registered existing subscriber: {chat_id}")
        except requests.RequestException as e:
            logger.warning(f"Could not fetch existing subscribers: {e}")

        return {
            "bot_username": data["result"]["username"],
            "subscribers": len(Settings.TELEGRAM_CHAT_IDS),
        }
    except requests.RequestException as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/poll_chat_id")
async def poll_chat_id(api_key: str = Depends(get_api_key)):
    token = Settings.TELEGRAM_TOKEN
    if not token:
        return JSONResponse(content={"error": "No token"}, status_code=400)
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getUpdates")
        data = response.json()
        if data.get("ok") and len(data["result"]) > 0:
            chat_id = str(data["result"][-1]["message"]["chat"]["id"])
            Settings.save_telegram_config(token, chat_id)
            if vfe := get_engine():
                vfe.notifier.token = token
                Settings.TELEGRAM_CHAT_IDS.add(chat_id)
                Settings.persist_chat_ids()
            return {"status": "success", "chat_id": chat_id}
        return {"status": "waiting"}
    except (requests.RequestException, KeyError, ValueError) as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
