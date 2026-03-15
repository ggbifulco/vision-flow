<div align="center">

# 🔭 VisionFlow

### Real-time Multimodal Intelligent Monitoring

**English** · [Italiano](README_IT.md)

[![YOLO26](https://img.shields.io/badge/Detection-YOLO26-ef4444?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyeiIvPjwvc3ZnPg==)](https://ultralytics.com/)
[![Gemini](https://img.shields.io/badge/VLM-Gemini_3.1-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/VLM-Groq-F55036?style=for-the-badge)](https://groq.com/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PWA](https://img.shields.io/badge/PWA-Ready-5A0FC8?style=for-the-badge&logo=pwa)](https://web.dev/progressive-web-apps/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

<br/>

> **YOLO26 detects. Gemini understands. Telegram alerts. You stay informed.**

<br/>

</div>

---

## What is VisionFlow?

VisionFlow is a self-hosted, real-time video intelligence system that combines **edge object detection** with **cloud-scale vision reasoning** — all accessible from a clean web dashboard or your phone.

Point a camera at anything. VisionFlow watches 24/7, triggers an AI analysis when something interesting happens, and sends you a structured report over Telegram — complete with threat level, weapon detection, and scene description.

No GPU needed. Runs on any laptop or Raspberry Pi.

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
| 🎯 **Personal AI Missions** | Each Telegram subscriber sets their own `/mission` — gets their own analysis |
| 🌐 **Web Dashboard** | Live MJPEG stream, real-time AI analysis, full config panel |
| 📲 **PWA** | Install as a native app on iPhone/Android |
| 🔐 **API Key Auth** | All endpoints protected via header or query param |
| 🗃️ **Multi-Camera** | Webcams, RTSP streams, video files — all from one UI |
| 🧠 **Structured Output** | Default prompt returns people count, armed Y/N, weapon type, threat level |
| 💾 **Persistence** | Subscribers, token, and settings survive server restarts |

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/ggbifulco/vision-flow.git
cd vision-flow
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

Minimum required — edit `.env`:

```env
# VLM Provider: "gemini" (default) or "groq"
VLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
```

Everything else (Telegram token, alert keywords, VLM interval) can be configured live from the dashboard.

### 3. Run

```bash
# Web dashboard (recommended)
python main.py --mode web
```

Open **http://localhost:8000** — default API key: `visionflow_secret_123`

```bash
# Local OpenCV window (no browser needed)
python main.py --mode local
```

---

## Telegram Setup

VisionFlow uses a self-hosted bot model — you own your bot, your subscribers, your data.

**For you (once):**
1. Open the dashboard → Settings → Telegram section
2. Click **Open BotFather**, send `/newbot`, get your token
3. Paste the token → click **Connect Bot**
4. Token is saved to `.env` and persists across restarts

**For your users (one tap):**
1. They scan the QR code shown in the dashboard (or tap the link)
2. Press **Start** in Telegram
3. They're subscribed — alerts arrive automatically

**Bot commands available to subscribers:**

| Command | Description |
|---|---|
| `/start` | Subscribe to alerts |
| `/stop` | Unsubscribe |
| `/mission <text>` | Set a personal AI mission for your alerts |
| `/test` | Send a test message to verify connection |

> Each subscriber can set their own `/mission` and receive a personalized analysis. Users with the same mission share a single VLM call for efficiency.

---

## Dashboard

The web dashboard gives you full control:

- **Live feed** — clean MJPEG stream, no YOLO boxes cluttering the view
- **AI Analysis panel** — structured output updates in real-time
- **Ask AI** — type a question and get an immediate VLM analysis of the current frame
- **Settings panel** (slide-out):
  - VLM provider selector (Gemini / Groq)
  - Confidence threshold & VLM interval sliders
  - Trigger classes grid (select which YOLO classes activate analysis)
  - Alert keywords editor (tags)
  - Resolution selector
  - Telegram setup wizard with QR sharing
  - API key management

All settings apply instantly without restarting the server.

---

## API Reference

All endpoints require auth: `?api_key=your_key` or `X-API-Key: your_key` header.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web Dashboard |
| `GET` | `/health` | Health check |
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

The default alert keyword is `Armed: YES` — a Telegram notification fires only when a weapon is detected. You can change both the mission and keywords from the dashboard.

---

## Hardware Requirements

| Component | Requirement |
|---|---|
| CPU | Any modern x86/ARM — no GPU needed |
| RAM | ~500MB idle |
| Camera | USB webcam, IP camera (RTSP), or video file |
| Network | Internet connection for VLM API calls |
| Python | 3.11+ |

YOLO26 runs locally and is optimized for CPU inference (43% faster than v11). The VLM runs in the cloud — latency is ~1-2s per analysis, but analysis only triggers when something relevant is detected.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `VLM_PROVIDER` | No | `gemini` | VLM backend: `gemini` or `groq` |
| `GEMINI_API_KEY` | If using Gemini | — | Google AI Studio key |
| `GROQ_API_KEY` | If using Groq | — | Groq Console key |
| `TELEGRAM_TOKEN` | No | — | Set from dashboard, auto-saved |
| `TELEGRAM_CHAT_IDS` | No | — | Auto-managed, persisted by app |
| `VISIONFLOW_API_KEY` | No | `visionflow_secret_123` | Dashboard/API auth key |

---

<div align="center">

Made by [Giuseppe Gerardo Bifulco](https://tuo-portfolio.vercel.app)

</div>
