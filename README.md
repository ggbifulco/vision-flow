<div align="center">

# VisionFlow

### Real-time Multimodal Intelligent Monitoring

**English** · [Italiano](README_IT.md)

[![YOLO26](https://img.shields.io/badge/Detection-YOLO26-ef4444?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyeiIvPjwvc3ZnPg==)](https://ultralytics.com/)
[![Gemini](https://img.shields.io/badge/VLM-Gemini_3.1-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/VLM-Groq-F55036?style=for-the-badge)](https://groq.com/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PWA](https://img.shields.io/badge/PWA-Ready-5A0FC8?style=for-the-badge&logo=pwa)](https://web.dev/progressive-web-apps/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com/)

<br/>

> **YOLO26 detects. Gemini understands. Telegram alerts. You stay informed.**

https://github.com/user-attachments/assets/915285d2-06ec-45e6-b1bb-a0121b79a8b3

<br/>

</div>

---

## What is VisionFlow?

VisionFlow is a **self-hosted, real-time video intelligence system** that combines edge object detection with cloud-scale vision reasoning — all accessible from a clean web dashboard or your phone.

Point a camera at anything. VisionFlow watches 24/7, triggers an AI analysis when something interesting happens, and sends you a structured report over Telegram — complete with threat level, weapon detection, and scene description.

**No GPU needed.** Runs on any laptop, server, or Raspberry Pi.

---

## How it works

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐     ┌──────────────┐
│  Webcam /   │────▶│  YOLO26          │────▶│  Cloud VLM          │────▶│  Telegram    │
│  IP Camera  │     │  (local, 30 FPS) │     │  Gemini 3.1 / Groq  │     │  + Dashboard │
└─────────────┘     └──────────────────┘     └─────────────────────┘     └──────────────┘
                           │
                    Smart Trigger
                    (only fires when
                    relevant classes
                    are detected)
```

1. **YOLO26** runs locally, detects objects at 30+ FPS with zero cloud cost
2. When a trigger class is detected (person, vehicle, etc.) a frame is sent to the **VLM**
3. The VLM returns a structured analysis — threat level, weapons, scene description
4. If alert keywords match (e.g. `Armed: YES`), a **Telegram notification** is sent to all subscribers
5. Everything is visible live on the **Web Dashboard**

---

## Features

| Feature | Details |
|---|---|
| 🎯 **Smart Triggering** | VLM only runs when YOLO detects relevant classes — no wasted API calls |
| 🔀 **Multi-Provider VLM** | Switch between Gemini 3.1 Flash Lite and Groq at runtime, no restart |
| 📱 **Telegram Alerts** | Multi-subscriber, per-user missions, persistent across restarts |
| 🧠 **Personal AI Missions** | Each subscriber sets their own `/mission` — gets personalized analysis |
| 🌐 **Web Dashboard** | Live MJPEG stream, real-time AI analysis, full config panel |
| 📲 **PWA** | Install as a native app on iPhone / Android |
| 🔐 **API Key Auth** | All endpoints protected via header or query param |
| 🗃️ **Multi-Camera** | Webcams, RTSP streams, video files — all from one UI |
| 🧩 **Structured Output** | Default prompt returns people count, armed Y/N, weapon type, threat level |
| 💾 **Persistence** | Subscribers, token, and settings survive server restarts |
| 🧵 **Thread-Safe Engine** | Concurrent VLM analysis with bounded thread pool (max 4 workers) |
| 🔒 **HMAC Auth** | Timing-attack resistant API key comparison |

---

## Quick Start

### Docker (recommended)

```bash
git clone https://github.com/ggbifulco/vision-flow.git
cd vision-flow
cp .env.example .env
# Edit .env with your GEMINI_API_KEY
docker compose up -d
```

Open **http://localhost:8000**.

```bash
# Logs
docker compose logs -f

# Rebuild after code changes
docker compose up -d --build

# Stop
docker compose down
```

**Platform notes:**

| Platform | Camera setup |
|---|---|
| **Linux + USB webcam** | Uncomment the `devices` section in `docker-compose.yml` |
| **Windows / Mac** | Use an IP camera (RTSP URL) — add it from the dashboard |
| **Video file** | Point `Settings.SOURCES` to a file path |

### Local install

```bash
git clone https://github.com/ggbifulco/vision-flow.git
cd vision-flow
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
python main.py --mode web
```

Open **http://localhost:8000**.

> **Tip:** The YOLO model (`yolo26n.pt`, ~5 MB) is downloaded automatically on first run and cached locally.

---

## Configuration

### Environment variables

Edit `.env` before starting:

| Variable | Required | Default | Description |
|---|---|---|---|
| `VLM_PROVIDER` | No | `gemini` | VLM backend: `gemini` or `groq` |
| `GEMINI_API_KEY` | If using Gemini | — | [Google AI Studio](https://aistudio.google.com/apikey) key |
| `GROQ_API_KEY` | If using Groq | — | [Groq Console](https://console.groq.com/) key |
| `VISIONFLOW_API_KEY` | No | `visionflow_secret_123` | Dashboard / API authentication key |
| `TELEGRAM_TOKEN` | No | — | Set from dashboard, auto-saved to `.env` |
| `TELEGRAM_CHAT_IDS` | No | — | Auto-managed by the app |

> **Security:** Change `VISIONFLOW_API_KEY` in production. The default key is documented for convenience only.

### Dashboard settings

All settings below can be changed live from the web dashboard — **no restart needed**:

| Setting | Description |
|---|---|
| **VLM Provider** | Switch between Gemini and Groq |
| **Confidence Threshold** | YOLO minimum confidence (0.0–1.0) |
| **VLM Interval** | Minimum seconds between VLM analyses |
| **Trigger Classes** | Which YOLO class IDs trigger analysis (default: `[0]` = person) |
| **Alert Keywords** | Keywords in VLM output that trigger Telegram alerts |
| **Display Resolution** | MJPEG stream resolution |
| **Save Analysis** | Persist analysis results and screenshots to `./outputs/` |

---

## Telegram Setup

VisionFlow uses a **self-hosted bot model** — you own your bot, your subscribers, your data.

### For you (once)

1. Open the dashboard → Settings → Telegram section
2. Click **Open BotFather**, send `/newbot`, get your token
3. Paste the token → click **Connect Bot**
4. Token is saved to `.env` and persists across restarts

### For your users (one tap)

1. They scan the QR code shown in the dashboard (or tap the link)
2. Press **Start** in Telegram
3. They're subscribed — alerts arrive automatically

### Bot commands

| Command | Description |
|---|---|
| `/start` | Subscribe to alerts |
| `/stop` | Unsubscribe |
| `/mission <text>` | Set a personal AI mission |
| `/test` | Send a test message to verify connection |

> Each subscriber can set their own `/mission` and receive a personalized analysis. Users with the same mission share a single VLM call for efficiency.

---

## API Reference

All endpoints (except `/health` and `/`) require authentication:

```
X-API-Key: your_key
# or
?api_key=your_key
```

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web Dashboard |
| `GET` | `/health` | Health check (no auth) |
| `GET` | `/video_feed/{cam}` | Live MJPEG stream |
| `GET` | `/latest_analysis` | Current VLM result + thinking status |
| `POST` | `/ask` | One-shot VLM query on current frame |
| `GET` | `/mission` | Get current AI mission |
| `POST` | `/mission` | Update AI mission |
| `GET` | `/current_settings` | Get all current settings |
| `POST` | `/settings` | Update settings (provider, keywords, classes…) |
| `GET` | `/cameras` | List configured cameras |
| `GET` | `/telegram_status` | Bot status + subscriber count |
| `POST` | `/register_token` | Save Telegram bot token |
| `POST` | `/telegram_test` | Send test alert to all subscribers |
| `GET` | `/poll_chat_id` | Poll for new Telegram subscribers |

### Example: Ask the AI

```bash
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "How many people are in this room?"}'
```

### Example: Update settings

```bash
curl -X POST http://localhost:8000/settings \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"confidence_threshold": 0.6, "vlm_interval": 10}'
```

---

## Default AI Mission

Out of the box, VisionFlow uses a security-focused structured prompt:

```
Analyze this scene for security threats. Respond in this exact structured format:
- People detected: [number]
- Armed: [YES / NO]
- Weapon type: [type or N/A]
- Threat level: [LOW / MEDIUM / HIGH / CRITICAL]
- Description: [brief description of the scene and any suspicious behavior]
```

The default alert keyword is `Armed: YES` — a Telegram notification fires only when a weapon is detected.

You can customize both the mission and keywords from the dashboard. For example:

| Use case | Mission idea |
|---|---|
| **Retail analytics** | "Count customers, describe their behavior, estimate wait times" |
| **Wildlife monitoring** | "Identify animal species, count individuals, note behavior" |
| **Traffic analysis** | "Count vehicles by type, detect accidents, estimate congestion" |
| **Elderly care** | "Check if person is standing, fallen, or in distress" |

---

## Architecture

```
src/
├── api/
│   ├── app.py              # FastAPI application, Telegram worker, lifecycle events
│   ├── deps.py             # API key auth (HMAC), singleton factories (thread-safe)
│   └── routes/
│       ├── analysis.py     # /ask, /latest_analysis
│       ├── config.py       # /settings, /mission, /telegram_*, /cameras
│       └── video.py        # /video_feed/{cam} — MJPEG streaming
├── config/
│   └── settings.py         # Settings class (env-driven, type-annotated)
├── core/
│   ├── engine.py           # VisionFlowEngine — orchestrates YOLO + VLM + alerts
│   ├── notifier.py         # Telegram alert logic (send_message, send_photo)
│   ├── storage.py          # CSV logs + screenshot persistence
│   └── base_model.py       # Abstract base for YOLO and VLM models
├── inference/
│   └── yolo_detector.py    # YOLO26 wrapper (tracking + detection)
├── stream/
│   └── manager.py          # Multi-camera capture (webcam, RTSP, file)
└── vlm/
    └── visual_expert.py    # Multi-provider VLM (Gemini, Groq)
```

### Key design decisions

- **Thread-safe engine** — All shared state (`is_analyzing`, `last_analysis`, `frame_count`) protected by `threading.Lock`
- **Bounded thread pool** — VLM analyses use `ThreadPoolExecutor(max_workers=4)` to prevent runaway resource usage
- **Graceful shutdown** — FastAPI lifecycle events release camera handles and shut down the executor
- **HMAC API key comparison** — Prevents timing attacks on authentication
- **Double-checked locking** — Singleton initialization is thread-safe without unnecessary locking overhead

---

## Hardware Requirements

| Component | Requirement |
|---|---|
| CPU | Any modern x86/ARM — no GPU needed |
| RAM | ~500 MB idle, ~1 GB under load |
| Disk | ~200 MB (model + deps), more for saved screenshots |
| Camera | USB webcam, IP camera (RTSP), or video file |
| Network | Internet for VLM API calls (~1–2s latency per analysis) |
| Python | 3.11+ |
| Docker | 24+ (if using containerized deployment) |

YOLO26 runs locally and is optimized for CPU inference (43% faster than v11). The VLM runs in the cloud — analysis only triggers when something relevant is detected, so API costs stay low.

### Tested on

- Laptop (Windows 11, Python 3.12, USB webcam)
- Docker on Ubuntu 24.04 (RTSP IP camera)
- Raspberry Pi 5 (USB webcam, ~15 FPS)

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'cv2'` | Activate your venv or run `pip install opencv-python` |
| YOLO model download fails | Check internet connection; the model is ~5 MB. Alternatively, place `yolo26n.pt` in the project root |
| Camera not found | Verify the source in `Settings.SOURCES`. For USB webcams, try index `0`, `1`, `2`… |
| Telegram bot not responding | Make sure you pressed **Start** in the bot conversation. Check `/telegram_status` endpoint |
| VLM returns errors | Verify your API key in `.env`. Check quota/billing on your provider's dashboard |
| Port 8000 in use | Change the port: `uvicorn.run(app, port=8080)` or `docker compose` with modified ports |
| Docker permission denied for webcam | Add your user to the `video` group: `sudo usermod -aG video $USER` |

---

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Run tests (when available)
pytest
```

### Project conventions

- **Type hints** on all public functions
- **`logging`** module for all output (no `print`)
- **`pathlib.Path`** for filesystem paths
- **Pydantic `Field` validators** on all API input models
- **`hmac.compare_digest`** for any secret comparison

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## References

- [Ultralytics YOLO26](https://ultralytics.com/) — real-time object detection
- [Google Gemini API](https://ai.google.dev/) — multimodal vision-language model
- [Groq](https://groq.com/) — ultra-fast LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) — modern Python web framework
- [OpenCV](https://opencv.org/) — computer vision library

---

## License

This project is provided as-is for personal and commercial use.

---

<div align="center">

Made by **Giuseppe Gerardo Bifulco**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-ggbifulco-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ggbifulco/)
[![Portfolio](https://img.shields.io/badge/Portfolio-futureintelligence.space-black?style=for-the-badge&logo=vercel&logoColor=white)](https://futureintelligence.space/)

</div>
