# VisionFlow: Real-time Multimodal Intelligent Monitoring

**English Version** | [Versione Italiana](README_IT.md)

[![YOLO26](https://img.shields.io/badge/Model-YOLO26-red.svg)](https://ultralytics.com/)
[![Gemini](https://img.shields.io/badge/VLM-Gemini_3.1-4285F4.svg)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/VLM-Groq_API-blue.svg)](https://groq.com/)
[![FastAPI](https://img.shields.io/badge/Interface-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![PWA](https://img.shields.io/badge/Interface-PWA-orange.svg)](#-mobile-experience-pwa)

VisionFlow is an advanced multimodal video monitoring engine. It uses **YOLO26** for real-time object detection as a smart trigger and a **cloud VLM** for deep semantic scene understanding — no local VLM model required.

**Supported VLM Providers** (switchable at runtime from the Dashboard):
- **Google Gemini 3.1 Flash Lite** — fast, lightweight, default
- **Groq (Llama 4 Scout 17B)** — high-quality reasoning

---

## Architecture

```
Camera → YOLO (local, real-time) → Smart Trigger → Cloud VLM (Gemini / Groq) → Alerts
```

- **YOLO26** runs locally and handles real-time object detection at 30+ FPS.
- When a trigger condition is met (people, vehicles, pets detected), a frame is sent to the selected **cloud VLM**.
- The VLM performs semantic scene analysis and returns a detailed description in ~1-2 seconds.
- Alerts are dispatched via the Web Dashboard and Telegram.

---

## Key Features

-   **Dual-Engine Inference**: Real-time object detection (YOLO26, local) combined with deep semantic reasoning (Gemini or Groq, cloud).
-   **Multi-Provider VLM**: Switch between **Google Gemini** and **Groq** at runtime from the Dashboard — no restart needed.
-   **Dynamic AI Mission**: Change the AI's "goal" in real-time via the Web Dashboard or **Telegram command** (`/mission <text>`).
-   **Multi-Camera Support**: Manage multiple video streams (Webcams, RTSP, Files) from a single UI.
-   **Smart Triggering**: The VLM analysis is triggered only when YOLO detects specific classes (people, vehicles, pets), keeping cloud calls efficient.
-   **Interactive Web Dashboard**: Modern Dark UI with live MJPEG streaming, provider selector, and interactive Q&A.
-   **Auto-Config Telegram**: Instant connection via **QR Code** to receive real-time alerts and screenshots.
-   **PWA Ready**: Install VisionFlow on your smartphone as a native app for a full-screen mobile experience.
-   **Security & Persistence**: Protected via **API Key** (Header/Query) with automated CSV logging and screenshots archive.

---

## Quick Start

### 1. Installation
```bash
git clone https://github.com/ggbifulco/vision-flow.git
cd vision-flow
pip install -r requirements.txt
```

### 2. Configuration
Copy the example environment file and add your keys:
```bash
cp .env.example .env
```
Edit `.env` with your values:
```env
# VLM Provider: "gemini" (default) or "groq"
VLM_PROVIDER=gemini

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key

# Groq (optional, only if using Groq)
GROQ_API_KEY=your_groq_api_key

# Telegram (optional)
TELEGRAM_TOKEN=your_bot_token

# API Security
VISIONFLOW_API_KEY=your_secret_key
```

### 3. Execution
- **Web Dashboard (default)**:
  ```bash
  python main.py --mode web
  ```
  Open `http://localhost:8000` (Default Key: `visionflow_secret_123`).

- **Local mode** (no web server, terminal output only):
  ```bash
  python main.py --mode local
  ```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web Dashboard |
| GET | `/video_feed/{cam_id}` | MJPEG stream for a camera |
| GET | `/latest_analysis` | Current VLM analysis result |
| POST | `/ask` | Custom VLM query on the latest frame |
| POST | `/mission` | Update the AI mission in real-time |
| POST | `/settings` | Update all settings (including VLM provider) |
| GET | `/cameras` | List all configured cameras |

---

## Telegram & Remote Control
- **Auto-Pairing**: Paste your token in the Dashboard, scan the **QR Code**, and press **Start**.
- **Remote Mission**: Send `/mission Is the cat eating the plants?` to change the AI's focus instantly from anywhere.

---

## Hardware Requirements

Since the VLM runs in the **cloud** (Gemini or Groq), VisionFlow is fast even on CPU-only machines. No GPU is needed.

- **YOLO** runs locally and is lightweight enough for any modern CPU.
- **VLM** runs on cloud — all you need is an API key and an internet connection.
- Expect 30+ FPS for YOLO detection and ~1-2s for semantic analysis.

---

## API Security
Access endpoints programmatically using:
- **Header**: `X-API-Key: your_key`
- **Query**: `?api_key=your_key`

---

**Author**: [Giuseppe Gerardo Bifulco](https://tuo-portfolio.vercel.app)
