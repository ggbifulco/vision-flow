<div align="center">

# VisionFlow

### Monitoraggio Intelligente Multimodale in Tempo Reale

[English](README.md) · **Italiano**

[![YOLO26](https://img.shields.io/badge/Detection-YOLO26-ef4444?style=for-the-badge)](https://ultralytics.com/)
[![Gemini](https://img.shields.io/badge/VLM-Gemini_3.1-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/VLM-Groq-F55036?style=for-the-badge)](https://groq.com/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PWA](https://img.shields.io/badge/PWA-Ready-5A0FC8?style=for-the-badge&logo=pwa)](https://web.dev/progressive-web-apps/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com/)

<br/>

> **YOLO26 rileva. Gemini capisce. Telegram avvisa. Tu sei sempre informato.**

<br/>

</div>

---

## Cos'è VisionFlow?

VisionFlow è un **sistema di video intelligence in tempo reale, self-hosted**, che combina rilevamento oggetti edge con ragionamento visivo cloud — accessibile da una dashboard web o dal tuo telefono.

Punta una camera su qualsiasi cosa. VisionFlow monitora 24/7, avvia un'analisi AI quando succede qualcosa di interessante e ti manda un report strutturato su Telegram — con livello di minaccia, rilevamento armi e descrizione della scena.

**Nessuna GPU necessaria.** Gira su qualsiasi laptop, server o Raspberry Pi.

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
| 🧠 **Missioni AI Personali** | Ogni subscriber imposta la propria `/mission` — riceve l'analisi personalizzata |
| 🌐 **Dashboard Web** | Stream MJPEG live, analisi AI in tempo reale, pannello config completo |
| 📲 **PWA** | Installabile come app nativa su iPhone / Android |
| 🔐 **API Key Auth** | Tutti gli endpoint protetti via header o query param |
| 🗃️ **Multi-Camera** | Webcam, stream RTSP, file video — tutto da un'unica UI |
| 🧩 **Output Strutturato** | Il prompt default restituisce conteggio persone, armato S/N, tipo arma, livello minaccia |
| 💾 **Persistenza** | Subscriber, token e impostazioni sopravvivono ai riavvii del server |
| 🧵 **Thread-Safe Engine** | Analisi VLM concorrenti con thread pool limitato (max 4 worker) |
| 🔒 **HMAC Auth** | Confronto chiave API resistente ai timing attack |

---

## Guida Rapida

### Docker (raccomandato)

```bash
git clone https://github.com/ggbifulco/vision-flow.git
cd vision-flow
cp .env.example .env
# Modifica .env con la tua GEMINI_API_KEY
docker compose up -d
```

Apri **http://localhost:8000**.

```bash
# Log
docker compose logs -f

# Rebuild dopo modifiche al codice
docker compose up -d --build

# Stop
docker compose down
```

**Note per piattaforma:**

| Piattaforma | Setup camera |
|---|---|
| **Linux + webcam USB** | Decommenta la sezione `devices` in `docker-compose.yml` |
| **Windows / Mac** | Usa una IP camera (URL RTSP) — aggiungila dalla dashboard |
| **File video** | Imposta `Settings.SOURCES` con il path del file |

### Installazione locale

```bash
git clone https://github.com/ggbifulco/vision-flow.git
cd vision-flow
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
cp .env.example .env
# Modifica .env con la tua API key
python main.py --mode web
```

Apri **http://localhost:8000**.

> **Suggerimento:** Il modello YOLO (`yolo26n.pt`, ~5 MB) viene scaricato automaticamente al primo avvio e cachato localmente.

---

## Configurazione

### Variabili d'ambiente

Modifica `.env` prima di avviare:

| Variabile | Richiesta | Default | Descrizione |
|---|---|---|---|
| `VLM_PROVIDER` | No | `gemini` | Backend VLM: `gemini` o `groq` |
| `GEMINI_API_KEY` | Se usi Gemini | — | Chiave [Google AI Studio](https://aistudio.google.com/apikey) |
| `GROQ_API_KEY` | Se usi Groq | — | Chiave [Groq Console](https://console.groq.com/) |
| `VISIONFLOW_API_KEY` | No | `visionflow_secret_123` | Chiave auth dashboard / API |
| `TELEGRAM_TOKEN` | No | — | Impostato dalla dashboard, auto-salvato |
| `TELEGRAM_CHAT_IDS` | No | — | Gestito automaticamente dall'app |

> **Sicurezza:** Cambia `VISIONFLOW_API_KEY` in produzione. La chiave default è documentata solo per comodità.

### Impostazioni dashboard

Tutte le impostazioni qui sotto possono essere modificate live dalla dashboard web — **senza riavviare**:

| Impostazione | Descrizione |
|---|---|
| **VLM Provider** | Passa tra Gemini e Groq |
| **Confidence Threshold** | Confidenza minima YOLO (0.0–1.0) |
| **VLM Interval** | Secondi minimi tra le analisi VLM |
| **Trigger Classes** | Quali classi YOLO attivano l'analisi (default: `[0]` = persona) |
| **Alert Keywords** | Keyword nell'output VLM che triggerano gli alert Telegram |
| **Display Resolution** | Risoluzione stream MJPEG |
| **Save Analysis** | Salva risultati analisi e screenshot in `./outputs/` |

---

## Setup Telegram

VisionFlow usa un **modello bot self-hosted** — il bot è tuo, i subscriber sono tuoi, i dati sono tuoi.

### Per te (una volta sola)

1. Apri la dashboard → Settings → sezione Telegram
2. Clicca **Open BotFather**, invia `/newbot`, ottieni il token
3. Incolla il token → clicca **Connect Bot**
4. Il token viene salvato nel `.env` e persiste ai riavvii

### Per i tuoi utenti (un tap)

1. Scansionano il QR code mostrato nella dashboard (o toccano il link)
2. Premono **Start** su Telegram
3. Sono iscritti — gli alert arrivano automaticamente

### Comandi bot

| Comando | Descrizione |
|---|---|
| `/start` | Iscriviti agli alert |
| `/stop` | Disiscriviti |
| `/mission <testo>` | Imposta una missione AI personale |
| `/test` | Invia un messaggio di test per verificare la connessione |

> Ogni subscriber può impostare la propria `/mission` e ricevere un'analisi personalizzata. Gli utenti con la stessa missione condividono una singola chiamata VLM per efficienza.

---

## API Reference

Tutti gli endpoint (tranne `/health` e `/`) richiedono autenticazione:

```
X-API-Key: tua_chiave
# oppure
?api_key=tua_chiave
```

| Metodo | Endpoint | Descrizione |
|---|---|---|
| `GET` | `/` | Dashboard Web |
| `GET` | `/health` | Health check (no auth) |
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
| `GET` | `/poll_chat_id` | Poll per nuovi subscriber Telegram |

### Esempio: Chiedi all'AI

```bash
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: tua_chiave" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Quante persone ci sono in questa stanza?"}'
```

### Esempio: Aggiorna impostazioni

```bash
curl -X POST http://localhost:8000/settings \
  -H "X-API-Key: tua_chiave" \
  -H "Content-Type: application/json" \
  -d '{"confidence_threshold": 0.6, "vlm_interval": 10}'
```

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

La keyword di alert di default è `Armed: YES` — la notifica Telegram scatta solo quando viene rilevata un'arma.

Puoi personalizzare sia la missione che le keyword dalla dashboard. Esempi:

| Caso d'uso | Idea per la missione |
|---|---|
| **Analisi retail** | "Conta i clienti, descrivi il loro comportamento, stima i tempi di attesa" |
| **Monitoraggio fauna** | "Identifica le specie animali, conta gli individui, nota il comportamento" |
| **Analisi traffico** | "Conta i veicoli per tipo, incidenti, stima la congestione" |
| **Assistenza anziani** | "Controlla se la persona è in piedi, a terra, o in difficoltà" |

---

## Architettura

```
src/
├── api/
│   ├── app.py              # Applicazione FastAPI, worker Telegram, lifecycle events
│   ├── deps.py             # Auth API key (HMAC), factory singleton (thread-safe)
│   └── routes/
│       ├── analysis.py     # /ask, /latest_analysis
│       ├── config.py       # /settings, /mission, /telegram_*, /cameras
│       └── video.py        # /video_feed/{cam} — streaming MJPEG
├── config/
│   └── settings.py         # Classe Settings (driven da env, type-annotated)
├── core/
│   ├── engine.py           # VisionFlowEngine — orchestra YOLO + VLM + alert
│   ├── notifier.py         # Logica alert Telegram (send_message, send_photo)
│   ├── storage.py          # Log CSV + persistenza screenshot
│   └── base_model.py       # Classe base astratta per modelli YOLO e VLM
├── inference/
│   └── yolo_detector.py    # Wrapper YOLO26 (tracking + detection)
├── stream/
│   └── manager.py          # Cattura multi-camera (webcam, RTSP, file)
└── vlm/
    └── visual_expert.py    # VLM multi-provider (Gemini, Groq)
```

### Decisioni architetturali chiave

- **Engine thread-safe** — Tutto lo stato condiviso (`is_analyzing`, `last_analysis`, `frame_count`) protetto da `threading.Lock`
- **Thread pool limitato** — Le analisi VLM usano `ThreadPoolExecutor(max_workers=4)` per prevenire uso eccessivo di risorse
- **Graceful shutdown** — Gli eventi lifecycle di FastAPI rilasciano le handle delle camere e spengono l'executor
- **Confronto chiave API con HMAC** — Previene timing attack sull'autenticazione
- **Double-checked locking** — L'inizializzazione dei singleton è thread-safe senza locking inutile

---

## Requisiti Hardware

| Componente | Requisito |
|---|---|
| CPU | Qualsiasi x86/ARM moderno — nessuna GPU richiesta |
| RAM | ~500 MB a riposo, ~1 GB sotto carico |
| Disco | ~200 MB (modello + dipendenze), di più per screenshot salvati |
| Camera | Webcam USB, IP camera (RTSP), o file video |
| Rete | Internet per chiamate API VLM (~1–2s latenza per analisi) |
| Python | 3.11+ |
| Docker | 24+ (se usi deploy containerizzato) |

YOLO26 gira localmente ed è ottimizzato per l'inferenza CPU (43% più veloce della v11). Il VLM gira nel cloud — l'analisi si attiva solo quando viene rilevato qualcosa di rilevante, quindi i costi API restano bassi.

### Testato su

- Laptop (Windows 11, Python 3.12, webcam USB)
- Docker su Ubuntu 24.04 (IP camera RTSP)
- Raspberry Pi 5 (webcam USB, ~15 FPS)

---

## Risoluzione Problemi

| Problema | Soluzione |
|---|---|
| `ModuleNotFoundError: No module named 'cv2'` | Attiva il venv o esegui `pip install opencv-python` |
| Download modello YOLO fallito | Controlla la connessione; il modello è ~5 MB. In alternativa, metti `yolo26n.pt` nella root del progetto |
| Camera non trovata | Verifica la sorgente in `Settings.SOURCES`. Per webcam USB, prova indice `0`, `1`, `2`… |
| Bot Telegram non risponde | Assicurati di aver premuto **Start** nella conversazione del bot. Controlla l'endpoint `/telegram_status` |
| VLM restituisce errori | Verifica la API key in `.env`. Controlla quota/billing sulla dashboard del provider |
| Porta 8000 occupata | Cambia porta: `uvicorn.run(app, port=8080)` o `docker compose` con porte modificate |
| Docker permesso negato per webcam | Aggiungi il tuo utente al gruppo `video`: `sudo usermod -aG video $USER` |

---

## Sviluppo

```bash
# Installa dipendenze di sviluppo
pip install -r requirements.txt

# Esegui con auto-reload
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Esegui i test (quando disponibili)
pytest
```

### Convenzioni del progetto

- **Type hint** su tutte le funzioni pubbliche
- Modulo **`logging`** per tutti gli output (niente `print`)
- **`pathlib.Path`** per i path filesystem
- **Validatori Pydantic `Field`** su tutti i modelli di input API
- **`hmac.compare_digest`** per qualsiasi confronto di segreti

---

## Contributing

1. Fai un fork del repository
2. Crea un branch per la feature (`git checkout -b feature/nuova-feature`)
3. Commita le modifiche (`git commit -m 'Aggiunta nuova feature'`)
4. Pusha il branch (`git push origin feature/nuova-feature`)
5. Apri una Pull Request

---

## Riferimenti

- [Ultralytics YOLO26](https://ultralytics.com/) — rilevamento oggetti in tempo reale
- [Google Gemini API](https://ai.google.dev/) — modello vision-language multimodale
- [Groq](https://groq.com/) — inferenza LLM ultra-veloce
- [FastAPI](https://fastapi.tiangolo.com/) — framework web Python moderno
- [OpenCV](https://opencv.org/) — libreria computer vision

---

## Licenza

Questo progetto è fornito così com'è per uso personale e commerciale.

---

<div align="center">

Realizzato da **Giuseppe Gerardo Bifulco**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-ggbifulco-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ggbifulco/)
[![Portfolio](https://img.shields.io/badge/Portfolio-futureintelligence.space-black?style=for-the-badge&logo=vercel&logoColor=white)](https://futureintelligence.space/)

</div>
