# VisionFlow: Monitoraggio Intelligente Multimodale in Tempo Reale

[English Version](README.md) | **Versione Italiana**

[![YOLO26](https://img.shields.io/badge/Model-YOLO26-red.svg)](https://ultralytics.com/)
[![Gemini](https://img.shields.io/badge/VLM-Gemini_3.1-4285F4.svg)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/VLM-Groq_API-blue.svg)](https://groq.com/)
[![FastAPI](https://img.shields.io/badge/Interface-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![PWA](https://img.shields.io/badge/Interface-PWA-orange.svg)](#-mobile-experience-pwa)

VisionFlow è un motore di monitoraggio e analisi video multimodale avanzato. Utilizza **YOLO26** per il rilevamento oggetti in tempo reale come trigger intelligente e un **VLM cloud** per la comprensione semantica profonda della scena — nessun modello VLM locale richiesto.

**Provider VLM supportati** (selezionabili a runtime dalla Dashboard):
- **Google Gemini 3.1 Flash Lite** — veloce, leggero, default
- **Groq (Llama 4 Scout 17B)** — ragionamento di alta qualità

---

## Architettura

```
Camera → YOLO (locale, tempo reale) → Smart Trigger → Cloud VLM (Gemini / Groq) → Alert
```

- **YOLO26** gira localmente e gestisce il rilevamento oggetti in tempo reale a 30+ FPS.
- Quando una condizione di trigger viene soddisfatta (persone, veicoli, animali rilevati), un frame viene inviato al **VLM cloud** selezionato.
- Il VLM esegue l'analisi semantica della scena e restituisce una descrizione dettagliata in ~1-2 secondi.
- Gli alert vengono inviati tramite la Dashboard Web e Telegram.

---

## Caratteristiche Principali

-   **Dual-Engine Inference**: Rilevamento oggetti in tempo reale (YOLO26, locale) combinato con ragionamento semantico profondo (Gemini o Groq, cloud).
-   **VLM Multi-Provider**: Passa tra **Google Gemini** e **Groq** a runtime dalla Dashboard — nessun riavvio necessario.
-   **Missione IA Dinamica**: Cambia l'obiettivo dell'IA in tempo reale via Dashboard Web o tramite **comando Telegram** (`/mission <testo>`).
-   **Supporto Multi-Camera**: Gestisci più flussi video (Webcam, RTSP, File) da un'unica interfaccia.
-   **Smart Triggering**: L'analisi VLM si attiva solo quando YOLO rileva classi specifiche (persone, veicoli, animali), mantenendo efficienti le chiamate cloud.
-   **Dashboard Web Interattiva**: UI moderna Dark con streaming live MJPEG, selettore provider e Q&A interattivo.
-   **Auto-Config Telegram**: Collegamento istantaneo tramite **QR Code** per ricevere alert e screenshot sul cellulare.
-   **PWA Ready**: Installa VisionFlow sul tuo smartphone come app nativa per un'esperienza mobile a tutto schermo.
-   **Sicurezza e Persistenza**: Protetto da **API Key** (Header/Query) con logging CSV automatico e archivio screenshot.

---

## Guida Rapida

### 1. Installazione
```bash
git clone https://github.com/ggbifulco/vision-flow.git
cd vision-flow
pip install -r requirements.txt
```

### 2. Configurazione
Copia il file di ambiente di esempio e aggiungi le tue chiavi:
```bash
cp .env.example .env
```
Modifica `.env` con i tuoi valori:
```env
# Provider VLM: "gemini" (default) o "groq"
VLM_PROVIDER=gemini

# Google Gemini
GEMINI_API_KEY=tua_chiave_api_gemini

# Groq (opzionale, solo se usi Groq)
GROQ_API_KEY=tua_chiave_api_groq

# Telegram (opzionale)
TELEGRAM_TOKEN=tuo_token_bot

# Sicurezza API
VISIONFLOW_API_KEY=tua_chiave_segreta
```

### 3. Avvio
- **Web Dashboard (predefinita)**:
  ```bash
  python main.py --mode web
  ```
  Apri `http://localhost:8000` (Chiave Default: `visionflow_secret_123`).

- **Modalità locale** (senza web server, solo output nel terminale):
  ```bash
  python main.py --mode local
  ```

---

## Endpoint API

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/` | Dashboard Web |
| GET | `/video_feed/{cam_id}` | Stream MJPEG di una camera |
| GET | `/latest_analysis` | Risultato attuale dell'analisi VLM |
| POST | `/ask` | Query VLM personalizzata sull'ultimo frame |
| POST | `/mission` | Aggiorna la missione IA in tempo reale |
| POST | `/settings` | Aggiorna tutte le impostazioni (incluso provider VLM) |
| GET | `/cameras` | Elenco di tutte le camere configurate |

---

## Telegram e Controllo Remoto
- **Auto-Pairing**: Incolla il token nella Dashboard, scansiona il **QR Code**, e premi **Start**.
- **Missione Remota**: Invia `/mission Controlla se il cane sta dormendo` per cambiare il focus dell'IA istantaneamente da ovunque.

---

## Requisiti Hardware

Dato che il VLM gira nel **cloud** (Gemini o Groq), VisionFlow è veloce anche su macchine con sola CPU. Nessuna GPU necessaria.

- **YOLO** gira localmente ed è sufficientemente leggero per qualsiasi CPU moderna.
- **VLM** gira sul cloud — tutto ciò che serve è una chiave API e una connessione internet.
- Aspettati 30+ FPS per il rilevamento YOLO e ~1-2s per l'analisi semantica.

---

## Sicurezza API
Accedi agli endpoint programmaticamente usando:
- **Header**: `X-API-Key: tua_chiave`
- **Query**: `?api_key=tua_chiave`

---

**Autore**: [Giuseppe Gerardo Bifulco](https://tuo-portfolio.vercel.app)
