import os
import logging
import threading
import time
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, Response
from src.api.routes import video, analysis, config
from src.config.settings import Settings

logger = logging.getLogger(__name__)

app = FastAPI(title="VisionFlow AI", description="Real-time Multimodal Monitoring")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}

# --- Path Configuration ---
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates", "index.html")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# --- PWA & Static Endpoints ---
@app.get("/manifest.json")
async def get_manifest():
    return FileResponse(os.path.join(STATIC_DIR, "manifest.json"))

@app.get("/sw.js")
async def get_sw():
    return FileResponse(os.path.join(STATIC_DIR, "sw.js"))

@app.get("/", response_class=HTMLResponse)
async def index():
    if not os.path.exists(TEMPLATE_PATH):
        return HTMLResponse(content="<h1>Template not found</h1>", status_code=404)
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return Response(
            content=f.read(),
            media_type="text/html",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )

# --- Mounting Routes ---
app.include_router(video.router)
app.include_router(analysis.router)
app.include_router(config.router)

def _tg_send(token, chat_id, text):
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": text},
        timeout=5,
    )

def telegram_worker():
    """Background thread: listens for Telegram commands and auto-registers subscribers."""
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
                            logger.info(f"New Telegram subscriber: {chat_id} (total: {len(Settings.TELEGRAM_CHAT_IDS)})")
                            _tg_send(token, chat_id,
                                "✅ Subscribed to VisionFlow alerts!\n"
                                "You'll receive notifications when threats are detected.\n\n"
                                "Commands:\n"
                                "  /mission <text> — set your personal AI mission\n"
                                "  /stop — unsubscribe"
                            )
                        else:
                            _tg_send(token, chat_id, "✅ You're already subscribed to VisionFlow alerts.")

                    elif text.startswith("/test"):
                        _tg_send(token, chat_id, "🧪 VisionFlow test — connection is working!\nYou'll receive alerts when threats are detected.")

                    elif text.startswith("/stop"):
                        Settings.TELEGRAM_CHAT_IDS.discard(chat_id)
                        Settings.persist_chat_ids()
                        logger.info(f"Telegram subscriber removed: {chat_id}")
                        _tg_send(token, chat_id, "🔕 Unsubscribed from VisionFlow alerts.")

                    elif text.startswith("/mission"):
                        new_mission = text.replace("/mission", "", 1).strip()
                        if new_mission:
                            Settings.USER_MISSIONS[chat_id] = new_mission
                            _tg_send(token, chat_id, f"✅ Your mission updated:\n_{new_mission}_")
                            logger.info(f"User {chat_id} set mission: {new_mission}")
                        else:
                            current = Settings.USER_MISSIONS.get(chat_id, Settings.DEFAULT_MISSION)
                            _tg_send(token, chat_id,
                                f"Your current mission:\n_{current}_\n\n"
                                "To change it: /mission <your mission>"
                            )

        except Exception as e:
            logger.error(f"Telegram Worker Error: {e}")
            time.sleep(5)

        time.sleep(2)

# Avvio del worker in un thread separato
threading.Thread(target=telegram_worker, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
