import asyncio
import logging
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

import requests
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response

from src.api.deps import get_engine, get_stream_manager, limiter
from src.api.routes import analysis, config, video
from src.config.settings import Settings

logger = logging.getLogger(__name__)

# --- Telegram helpers ---


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
                                "Commands:\n"
                                "  /mission <text> — set your personal AI mission\n"
                                "  /stop — unsubscribe",
                            )
                        else:
                            _tg_send(token, chat_id, "✅ You're already subscribed.")

                    elif text.startswith("/test"):
                        _tg_send(
                            token,
                            chat_id,
                            "🧪 VisionFlow test — connection is working!",
                        )

                    elif text.startswith("/stop"):
                        Settings.TELEGRAM_CHAT_IDS.discard(chat_id)
                        Settings.persist_chat_ids()
                        _tg_send(token, chat_id, "🔕 Unsubscribed.")

                    elif text.startswith("/mission"):
                        new_mission = text.replace("/mission", "", 1).strip()
                        if new_mission:
                            Settings.USER_MISSIONS[chat_id] = new_mission
                            Settings.save_state()
                            _tg_send(token, chat_id, f"✅ Mission updated:\n{new_mission}")
                        else:
                            current = Settings.USER_MISSIONS.get(chat_id, Settings.DEFAULT_MISSION)
                            _tg_send(
                                token,
                                chat_id,
                                f"Current mission:\n{current}\n\nChange: /mission <text>",
                            )

        except requests.RequestException as e:
            logger.error(f"Telegram Worker network error: {e}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Telegram Worker error: {e}", exc_info=True)
            time.sleep(5)

        time.sleep(2)


# --- WebSocket broadcast ---

_ws_clients: list[WebSocket] = []
_ws_lock = threading.Lock()


async def _ws_broadcast(data: dict) -> None:
    with _ws_lock:
        dead: list[WebSocket] = []
        for ws in _ws_clients:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            _ws_clients.remove(ws)


# --- Lifespan ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    tg_thread = threading.Thread(target=telegram_worker, daemon=True, name="telegram-worker")
    tg_thread.start()
    logger.info("VisionFlow application started.")
    yield
    vfe = get_engine()
    vfe.shutdown()
    sm = get_stream_manager()
    sm.release_all()
    Settings.save_state()
    logger.info("VisionFlow application shut down.")


# --- App ---
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="VisionFlow AI",
    description=(
        "Real-time multimodal video intelligence API. "
        "Combines YOLO26 edge detection with cloud VLM analysis (Gemini / Groq) "
        "and Telegram alerting."
    ),
    version="1.0.0",
    contact={"name": "Giuseppe Gerardo Bifulco"},
    lifespan=lifespan,
)

app.state.limiter = limiter

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' fonts.googleapis.com; "
        "font-src fonts.gstatic.com; "
        "img-src 'self' api.qrserver.com data:; "
        "script-src 'self' 'unsafe-inline'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


# --- Routes ---
app.include_router(video.router)
app.include_router(analysis.router)
app.include_router(config.router)


# --- Health ---


@app.get("/health")
async def health() -> dict:
    from src.vlm.visual_expert import get_vlm_circuit

    sm = get_stream_manager()
    circuit = get_vlm_circuit()
    cameras = {name: cap.isOpened() for name, cap in sm.caps.items()}
    return {
        "status": "degraded" if circuit.is_open else "ok",
        "version": "1.0.0",
        "cameras": cameras,
        "vlm_provider": Settings.VLM_PROVIDER,
        "vlm_circuit_open": circuit.is_open,
        "telegram_configured": bool(Settings.TELEGRAM_TOKEN),
        "subscribers": len(Settings.TELEGRAM_CHAT_IDS),
    }


# --- Metrics ---


@app.get("/metrics")
async def metrics() -> dict:
    vfe = get_engine()
    storage_stats = vfe.storage.get_stats()
    return {
        **Settings.get_metrics(),
        **storage_stats,
    }


# --- Alert History ---


@app.get("/history")
async def history(limit: int = 50, alerts_only: bool = False) -> dict:
    vfe = get_engine()
    records = vfe.storage.get_history(limit=limit, alerts_only=alerts_only)
    return {"records": records, "count": len(records)}


# --- WebSocket ---


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    with _ws_lock:
        _ws_clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)
            vfe = get_engine()
            await websocket.send_json(
                {
                    "analysis": vfe.last_analysis,
                    "is_thinking": vfe.is_analyzing,
                    "frame_count": vfe.frame_count,
                }
            )
    except WebSocketDisconnect:
        with _ws_lock:
            if websocket in _ws_clients:
                _ws_clients.remove(websocket)


# --- PWA ---


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
