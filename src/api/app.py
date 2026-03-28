import logging
import threading
import time
from pathlib import Path

import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, Response
from src.api.routes import video, analysis, config
from src.config.settings import Settings

logger = logging.getLogger(__name__)

app = FastAPI(title="VisionFlow AI", description="Real-time Multimodal Monitoring")

# --- Path Configuration ---
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"

# --- Mounting Routes ---
app.include_router(video.router)
app.include_router(analysis.router)
app.include_router(config.router)

# --- Telegram helpers (centralized) ---


def _tg_send(token: str, chat_id: str, text: str) -> None:
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=5,
        )
    except requests.RequestException as e:
        logger.error(f"Telegram send failed for {chat_id}: {e}")


def telegram_worker() -> None:
    last_update_id = 0
    logger.info("Telegram Worker started (listening for commands...)")

    while True:
        token = Settings.TELEGRAM_TOKEN
        if not token:
            time.sleep(10)
            continue

        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            params = {"offset": last_update_id + 1, "timeout": 30}
            response = requests.get(url, params=params, timeout=35)
            data = response.json()

            if data.get("ok"):
                for update in data["result"]:
                    last_update_id = update["update_id"]
                    msg = update.get("message", {})
                    text = msg.get("text", "")
                    chat_id = str(msg.get("chat", {}).get("id", ""))
                    if not chat_id:
                        continue

                    if text.startswith("/start"):
                        if chat_id not in Settings.TELEGRAM_CHAT_IDS:
                            Settings.TELEGRAM_CHAT_IDS.add(chat_id)
                            Settings.persist_chat_ids()
                            logger.info(
                                f"New Telegram subscriber: {chat_id} "
                                f"(total: {len(Settings.TELEGRAM_CHAT_IDS)})"
                            )
                            _tg_send(
                                token,
                                chat_id,
                                "✅ Subscribed to VisionFlow alerts!\n"
                                "You'll receive notifications when threats are detected.\n\n"
                                "Commands:\n"
                                "  /mission <text> — set your personal AI mission\n"
                                "  /stop — unsubscribe",
                            )
                        else:
                            _tg_send(
                                token,
                                chat_id,
                                "✅ You're already subscribed to VisionFlow alerts.",
                            )

                    elif text.startswith("/test"):
                        _tg_send(
                            token,
                            chat_id,
                            "🧪 VisionFlow test — connection is working!\nYou'll receive alerts when threats are detected.",
                        )

                    elif text.startswith("/stop"):
                        Settings.TELEGRAM_CHAT_IDS.discard(chat_id)
                        Settings.persist_chat_ids()
                        logger.info(f"Telegram subscriber removed: {chat_id}")
                        _tg_send(
                            token, chat_id, "🔕 Unsubscribed from VisionFlow alerts."
                        )

                    elif text.startswith("/mission"):
                        new_mission = text.replace("/mission", "", 1).strip()
                        if new_mission:
                            Settings.USER_MISSIONS[chat_id] = new_mission
                            _tg_send(
                                token,
                                chat_id,
                                f"✅ Your mission updated:\n{new_mission}",
                            )
                            logger.info(f"User {chat_id} set mission: {new_mission}")
                        else:
                            current = Settings.USER_MISSIONS.get(
                                chat_id, Settings.DEFAULT_MISSION
                            )
                            _tg_send(
                                token,
                                chat_id,
                                f"Your current mission:\n{current}\n\n"
                                "To change it: /mission <your mission>",
                            )

        except requests.RequestException as e:
            logger.error(f"Telegram Worker network error: {e}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Telegram Worker error: {e}", exc_info=True)
            time.sleep(5)

        time.sleep(2)


_telegram_thread: threading.Thread | None = None


@app.on_event("startup")
async def startup_event() -> None:
    global _telegram_thread
    _telegram_thread = threading.Thread(
        target=telegram_worker, daemon=True, name="telegram-worker"
    )
    _telegram_thread.start()
    logger.info("VisionFlow application started.")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    from src.api.deps import _engine, _stream_manager

    if _engine is not None:
        _engine.shutdown()
    if _stream_manager is not None:
        _stream_manager.release_all()
    logger.info("VisionFlow application shut down.")


# --- Health & PWA ---


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": "1.0.0"}


@app.get("/manifest.json")
async def get_manifest() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "manifest.json"))


@app.get("/sw.js")
async def get_sw() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "sw.js"))


@app.get("/", response_class=HTMLResponse)
async def index() -> Response:
    template_path = TEMPLATE_DIR / "index.html"
    if not template_path.exists():
        return HTMLResponse(content="<h1>Template not found</h1>", status_code=404)
    return Response(
        content=template_path.read_text(encoding="utf-8"),
        media_type="text/html",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
    )
