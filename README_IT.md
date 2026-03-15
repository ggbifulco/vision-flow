<div align="center">

# 🔭 VisionFlow

### Monitoraggio Intelligente Multimodale in Tempo Reale

[English](README.md) · **Italiano**

[![YOLO26](https://img.shields.io/badge/Detection-YOLO26-ef4444?style=for-the-badge)](https://ultralytics.com/)
[![Gemini](https://img.shields.io/badge/VLM-Gemini_3.1-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/VLM-Groq-F55036?style=for-the-badge)](https://groq.com/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PWA](https://img.shields.io/badge/PWA-Ready-5A0FC8?style=for-the-badge&logo=pwa)](https://web.dev/progressive-web-apps/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

<br/>

> **YOLO26 rileva. Gemini capisce. Telegram avvisa. Tu sei sempre informato.**

<br/>

</div>

---

## Cos'è VisionFlow?

VisionFlow è un sistema di video intelligence in tempo reale, self-hosted, che combina **rilevamento oggetti edge** con **ragionamento visivo cloud** — accessibile da una dashboard web o dal tuo telefono.

Punta una camera su qualsiasi cosa. VisionFlow monitora 24/7, avvia un'analisi AI quando succede qualcosa di interessante e ti manda un report strutturato su Telegram — con livello di minaccia, rilevamento armi e descrizione della scena.

Nessuna GPU necessaria. Gira su qualsiasi laptop o Raspberry Pi.

---

## Come funziona

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐     ┌──────────────┐
│  Webcam /   │────▶│  YOLO26          │────▶│  Cloud VLM          │────▶│  Telegram    │
│  IP Camera  │     │  (locale, 30FPS) │     │  Gemini 3.1 / Groq  │     │  + Dashboard │
└─────────────┘     └──────────────────┘     └─────────────────────┘     └──────────────┘
                           │
                    Smart Trigger
                    (si attiva solo quando
                    vengono rilevate classi
                    di interesse)
```

1. **YOLO26** gira localmente, rileva oggetti a 30+ FPS senza costi cloud
2. Quando viene rilevata una classe trigger (persona, veicolo, ecc.) un frame viene inviato al **VLM**
3. Il VLM restituisce un'analisi strutturata — livello di minaccia, armi, descrizione scena
4. Se le keyword di alert matchano (es. `Armed: YES`), viene inviata una **notifica Telegram** a tutti i subscriber
5. Tutto è visibile in tempo reale sulla **Dashboard Web**

---

## Funzionalità

| Funzione | Dettagli |
|---|---|
| 🎯 **Smart Triggering** | Il VLM si attiva solo quando YOLO rileva classi rilevanti — nessuna chiamata API sprecata |
| 🔀 **VLM Multi-Provider** | Passa tra Gemini 3.1 Flash Lite e Groq a runtime, senza riavvio |
| 📱 **Alert Telegram** | Multi-subscriber, missioni per utente, persistenti ai riavvii |
| 🎯 **Missioni AI Personali** | Ogni subscriber Telegram imposta la propria `/mission` — riceve la sua analisi personalizzata |
| 🌐 **Dashboard Web** | Stream MJPEG live, analisi AI in tempo reale, pannello config completo |
| 📲 **PWA** | Installabile come app nativa su iPhone/Android |
| 🔐 **API Key Auth** | Tutti gli endpoint protetti via header o query param |
| 🗃️ **Multi-Camera** | Webcam, stream RTSP, file video — tutto da un'unica UI |
| 🧠 **Output Strutturato** | Il prompt default restituisce conteggio persone, armato S/N, tipo arma, livello minaccia |
| 💾 **Persistenza** | Subscriber, token e impostazioni sopravvivono ai riavvii del server |

---

## Guida Rapida

### 1. Clona e installa

```bash
git clone https://github.com/ggbifulco/vision-flow.git
cd vision-flow
pip install -r requirements.txt
```

### 2. Configura

```bash
cp .env.example .env
```

Minimo richiesto — modifica `.env`:

```env
# Provider VLM: "gemini" (default) o "groq"
VLM_PROVIDER=gemini
GEMINI_API_KEY=la_tua_chiave_gemini
```

Tutto il resto (token Telegram, keyword alert, intervallo VLM) si configura live dalla dashboard.

### 3. Avvia

```bash
# Web dashboard (raccomandato)
python main.py --mode web
```

Apri **http://localhost:8000** — chiave API di default: `visionflow_secret_123`

```bash
# Finestra OpenCV locale (senza browser)
python main.py --mode local
```

---

## Setup Telegram

VisionFlow usa un modello bot self-hosted — il bot è tuo, i subscriber sono tuoi, i dati sono tuoi.

**Per te (una volta sola):**
1. Apri la dashboard → Settings → sezione Telegram
2. Clicca **Open BotFather**, invia `/newbot`, ottieni il token
3. Incolla il token → clicca **Connect Bot**
4. Il token viene salvato nel `.env` e persiste ai riavvii

**Per i tuoi utenti (un tap):**
1. Scansionano il QR code mostrato nella dashboard (o toccano il link)
2. Premono **Start** su Telegram
3. Sono iscritti — gli alert arrivano automaticamente

**Comandi bot disponibili ai subscriber:**

| Comando | Descrizione |
|---|---|
| `/start` | Iscriviti agli alert |
| `/stop` | Disiscriviti |
| `/mission <testo>` | Imposta una missione AI personale per i tuoi alert |
| `/test` | Invia un messaggio di test per verificare la connessione |

> Ogni subscriber può impostare la propria `/mission` e ricevere un'analisi personalizzata. Gli utenti con la stessa missione condividono una singola chiamata VLM per efficienza.

---

## Dashboard

La dashboard web ti dà il controllo completo:

- **Feed live** — stream MJPEG pulito, senza box YOLO che disturbano la visuale
- **Pannello AI Analysis** — output strutturato che si aggiorna in tempo reale
- **Chiedi all'AI** — scrivi una domanda e ottieni un'analisi VLM immediata sul frame corrente
- **Pannello Settings** (slide-out):
  - Selettore provider VLM (Gemini / Groq)
  - Slider confidenza e intervallo VLM
  - Griglia classi trigger (scegli quali classi YOLO attivano l'analisi)
  - Editor keyword alert (tag)
  - Selettore risoluzione
  - Wizard setup Telegram con condivisione QR
  - Gestione API key

Tutte le impostazioni si applicano istantaneamente senza riavviare il server.

---

## API Reference

Tutti gli endpoint richiedono auth: `?api_key=tua_chiave` o header `X-API-Key: tua_chiave`.

| Metodo | Endpoint | Descrizione |
|---|---|---|
| `GET` | `/` | Dashboard Web |
| `GET` | `/health` | Health check |
| `GET` | `/video_feed/{cam}` | Stream MJPEG live |
| `GET` | `/latest_analysis` | Risultato VLM corrente + stato thinking |
| `POST` | `/ask` | Query VLM one-shot sul frame corrente |
| `GET` | `/mission` | Ottieni missione AI corrente |
| `POST` | `/mission` | Aggiorna missione AI |
| `GET` | `/current_settings` | Ottieni tutte le impostazioni correnti |
| `POST` | `/settings` | Aggiorna impostazioni (provider, keyword, classi…) |
| `GET` | `/cameras` | Lista camere configurate |
| `GET` | `/telegram_status` | Stato bot + contatore subscriber |
| `POST` | `/register_token` | Salva token bot Telegram |
| `POST` | `/telegram_test` | Invia alert di test a tutti i subscriber |

---

## Missione AI di Default

Di default, VisionFlow usa un prompt strutturato orientato alla sicurezza:

```
Analyze this scene for security threats. Respond in this exact structured format:
- People detected: [number]
- Armed: [YES / NO]
- Weapon type: [type or N/A]
- Threat level: [LOW / MEDIUM / HIGH / CRITICAL]
- Description: [brief description of the scene and any suspicious behavior]
```

La keyword di alert di default è `Armed: YES` — la notifica Telegram scatta solo quando viene rilevata un'arma. Puoi cambiare sia la missione che le keyword dalla dashboard.

---

## Requisiti Hardware

| Componente | Requisito |
|---|---|
| CPU | Qualsiasi x86/ARM moderno — nessuna GPU richiesta |
| RAM | ~500MB a riposo |
| Camera | Webcam USB, IP camera (RTSP), o file video |
| Rete | Connessione internet per le chiamate API VLM |
| Python | 3.11+ |

YOLO26 gira localmente ed è ottimizzato per l'inferenza CPU (43% più veloce della v11). Il VLM gira nel cloud — latenza ~1-2s per analisi, ma l'analisi si attiva solo quando viene rilevato qualcosa di rilevante.

---

## Variabili d'Ambiente

| Variabile | Richiesta | Default | Descrizione |
|---|---|---|---|
| `VLM_PROVIDER` | No | `gemini` | Backend VLM: `gemini` o `groq` |
| `GEMINI_API_KEY` | Se usi Gemini | — | Chiave Google AI Studio |
| `GROQ_API_KEY` | Se usi Groq | — | Chiave Groq Console |
| `TELEGRAM_TOKEN` | No | — | Impostato dalla dashboard, auto-salvato |
| `TELEGRAM_CHAT_IDS` | No | — | Gestito automaticamente dall'app |
| `VISIONFLOW_API_KEY` | No | `visionflow_secret_123` | Chiave auth dashboard/API |

---

<div align="center">

Realizzato da [Giuseppe Gerardo Bifulco](https://tuo-portfolio.vercel.app)

</div>
