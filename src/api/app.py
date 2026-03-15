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

def telegram_worker():
    """Thread di background per ascoltare comandi da Telegram."""
    last_update_id = 0
    logger.info("Telegram Worker avviato (In ascolto comandi...)")
    
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
                    if "message" in update and "text" in update["message"]:
                        text = update["message"]["text"]
                        chat_id = update["message"]["chat"]["id"]
                        
                        if text.startswith("/mission"):
                            new_mission = text.replace("/mission", "").strip()
                            if new_mission:
                                Settings.DEFAULT_MISSION = new_mission
                                msg = f"✅ Missione aggiornata: {new_mission}"
                                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                                             data={"chat_id": chat_id, "text": msg})
                                logger.info(f"Nuova missione da Telegram: {new_mission}")
                            else:
                                msg = "Uso: /mission <tua nuova missione>"
                                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                                             data={"chat_id": chat_id, "text": msg})
        except Exception as e:
            logger.error(f"Telegram Worker Error: {e}")
            time.sleep(5)
        
        time.sleep(2)

# Avvio del worker in un thread separato
threading.Thread(target=telegram_worker, daemon=True).start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
