<div align="center">

# 🤖 J.A.R.V.I.S v2.0

> **J**ust **A** **R**ather **V**ery **I**ntelligent **S**ystem

<p>
  <a href="#features"><strong>Features</strong></a> •
  <a href="#quick-start"><strong>Quick Start</strong></a> •
  <a href="#architecture"><strong>Architecture</strong></a> •
  <a href="#agents"><strong>Agents</strong></a> •
  <a href="#memory-system"><strong>Memory</strong></a> •
  <a href="#configuration"><strong>Configuration</strong></a> •
  <a href="#development"><strong>Development</strong></a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/Ollama-Local%20LLM-FF6F00?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

**Personal, locally-hosted, multi-agent AI assistant — zero cloud dependency.**

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Multi-Agent Architecture** | 8 specialized agents — coder, researcher, RPA, email, sysmon, clipboard, meeting, files |
| 🏠 **100% Local** | Runs entirely on your machine via Ollama. No API keys required. |
| 🧩 **3-Layer Memory** | Working → Long-Term (SQLite + ChromaDB) → Procedural — with decay & consolidation |
| 💻 **RPA Capabilities** | Screen capture, OCR, mouse/keyboard automation via pyautogui + mss + EasyOCR |
| 📧 **Email Assistant** | IMAP/SMTP async inbox reading, smart summarization, draft creation & sending |
| 🖥️ **System Monitor** | Real-time CPU/RAM/disk monitoring with proactive threshold alerts |
| 📋 **Clipboard Intelligence** | Auto-detects text/URL/code in clipboard — summarizes, translates, or reviews |
| 🎙️ **Meeting Transcription** | Live Whisper-based transcription with action item extraction |
| 📁 **File Organizer** | Watchdog-powered directory monitoring, content-based classification, duplicate detection |
| 🌐 **Multi-Provider LLM** | Ollama (primary) + optional fallbacks: OpenRouter, Groq, Gemini, Cloudflare, Together AI, OpenAI |
| 🎨 **Modern GUI** | React + Vite + Tailwind CSS desktop app via Tauri |
| 🔒 **Security First** | Scoped CORS, optional API key auth, rate limiting, structured logging |

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Python** | 3.10+ | Backend runtime |
| **Node.js** | 18+ | GUI build toolchain |
| **Ollama** | Latest | Local LLM runtime |

### One-Command Launch

```bash
# Windows — double-click or run:
start-jarvis-desktop.bat
```

That's it. The script:
1. ✅ Activates the virtual environment
2. 🚀 Starts the FastAPI backend (`:8000`)
3. ⏳ Waits for health check (auto-retry loop)
4. 🎨 Launches the React frontend (`:5173`)

### Manual Setup

```bash
# 1. Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS/Linux

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Install & run Ollama
ollama pull qwen2.5:14b          # Download model
ollama serve                     # Start server

# 4. Start backend
python -m uvicorn jarvis.api.main:app --host 127.0.0.1 --port 8000

# 5. Start frontend (in another terminal)
cd jarvis-desktop && npm install && npm run dev
```

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     J.A.R.V.I.S v2.0                          │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐         ┌──────────────────────┐   │
│  │   React + Vite GUI  │◄───────►│   FastAPI Backend    │   │
│  │   (port 5173)       │  HTTP   │   (port 8000)        │   │
│  └─────────────────────┘         └──────────┬───────────┘   │
│                                             │                │
│                                ┌────────────▼────────────┐   │
│                                │     Orchestrator        │   │
│                                │  (Intent Classification) │   │
│                                └────────────┬────────────┘   │
│                                             │                │
│              ┌──────────┬───────────┬───────┼───────┬────────┤
│              │          │           │       │       │        │
│  ┌───────────▼─┐ ┌─────▼─────┐ ┌───▼────┐ ┌▼──────┐│┌──────▼──────┐│
│  │  CoderAgent │ │Researcher │ │  RPA   │ │ Email │ │ SysMonitor  ││
│  │             │ │  Agent    │ │Operator│ │ Agent │ │   Agent     ││
│  └─────────────┘ └───────────┘ └────────┘ └───────┘ └─────────────┘│
│  ┌─────────────┐ ┌───────────┐ ┌─────────────────────────────────┐│
│  │  Clipboard  │ │  Meeting  │ │         File Organizer           ││
│  │   Agent     │ │  Agent    │ │            Agent                 ││
│  └─────────────┘ └───────────┘ └─────────────────────────────────┘│
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Memory System                             │   │
│  │  ┌──────────────┐ ┌──────────────────┐ ┌─────────────────┐ │   │
│  │  │   Working    │ │   Long-Term      │ │   Procedural    │ │   │
│  │  │   Memory     │ │ (SQLite+ChromaDB)│ │   Memory        │ │   │
│  │  │  (20 msgs)   │ │  (FTS5+RRF)      │ │  (Strategies)   │ │   │
│  │  └──────────────┘ └──────────────────┘ └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   LLM Router (Multi-Provider)                │   │
│  │  Ollama ──► OpenRouter ──► Groq ──► Gemini ──► OpenAI       │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Agents

### 1. CoderAgent 💻
Writes, debugs, and executes code with an auto-healing loop (up to 5 iterations).

```
"Python ile fibonacci yaz"
"Bu kodu düzelt"
```

### 2. ResearcherAgent 🔍
Multi-hop web research via DuckDuckGo + URL scraping + LLM synthesis with citations.

```
"Kuantum bilgi nedir?"
"En iyi Rust frameworklerini araştır"
```

### 3. RPAOperatorAgent 🖱️
Computer-use agent — screenshot, OCR, mouse click, keyboard input, app launching.

```
"Chrome'u aç"
"YouTube'u aç"
```

### 4. EmailAgent 📧
Async IMAP/SMTP inbox reading, smart summarization, draft creation & sending.

```
"Maillerimi özetle"              → Top 5 important emails
"Sabah özeti"                    → Morning briefing
"Ahmet'e toplantı saati yaz"     → Draft email
```

### 5. SystemMonitorAgent 🖥️
Real-time CPU/RAM/disk monitoring with proactive threshold alerts.

```
"Sistem durumu nedir?"           → Full metrics
"En çok RAM kullanan processler" → Top processes
```

### 6. ClipboardAgent 📋
Auto-detects clipboard content type (text/URL/code) and processes accordingly.

```
"Panodaki kodu analiz et"        → Code review
"Panodaki metni çevir"           → Translation
"Panodaki URL'yi özetle"         → Fetch + summarize
```

### 7. MeetingAgent 🎙️
Live Whisper-based transcription with action item extraction.

```
"Toplantıyı kaydet"              → Start recording
"Toplantıyı durdur"              → Stop & transcribe
"Özet çıkar"                     → Summary + action items
```

Output: `data/meetings/YYYY-MM-DD_HH-MM.md`

### 8. FileOrganizerAgent 📁
Content-based file classification, duplicate detection, desktop cleanup.

```
"Masaüstünü düzenle"             → Organize Desktop
"Yinelenen dosyaları bul"        → Find duplicates
"İndirilenleri düzenle"          → Organize Downloads
```

---

## 🧠 Memory System

### 3-Layer Unified Architecture

| Layer | Storage | Capacity | Purpose |
|-------|---------|----------|---------|
| **Working Memory** | In-memory (deque) | 20 messages / 4000 tokens | Active conversation context |
| **Long-Term Memory** | SQLite + FTS5 + ChromaDB | Unlimited | Episodic + semantic recall with hybrid search (RRF fusion) |
| **Procedural Memory** | SQLite | Unlimited | Learned strategies & patterns from successful task completions |

**Key features:**
- 🔥 **Decay**: Old/unimportant memories fade (`importance *= exp(-days / 90)`)
- 🌙 **Nightly Consolidation**: Auto-runs at 03:00 — clusters similar episodes, merges, cleans up
- 🔍 **Hybrid Search**: FTS5 lexical + ChromaDB vector search combined via Reciprocal Rank Fusion
- 📊 **Importance Scoring**: Heuristic-based (length, questions, keywords, dates) — only important memories persist

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# Email (optional)
JARVIS_EMAIL_USER=your@email.com
JARVIS_EMAIL_PASS=your_app_password

# API Key Protection (optional)
JARVIS_API_KEY=your_secret_key

# Allowed CORS Origins
JARVIS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# LLM (optional — defaults to Ollama)
OPENROUTER_API_KEY=sk-or-v1-...
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIzaSyD...
```

> 🔑 **No API keys are required.** All optional providers serve as fallbacks when Ollama is unavailable.

### Agent Configuration (`config/agents.yaml`)

```yaml
agents:
  email:
    check_interval_minutes: 30
    max_emails_summary: 5
  sysmon:
    poll_interval_seconds: 5
    alert_thresholds:
      cpu_percent: 85
      ram_percent: 90
      disk_percent: 95
  meeting:
    whisper_model: "base"    # tiny/base/small/medium/large
    language: "tr"
  files:
    watch_dirs:
      - "~/Downloads"
      - "~/Desktop"

memory:
  working:
    max_messages: 20
  long_term:
    db_path: "data/memory.db"
    decay_days: 90
    min_importance_to_store: 0.3
  consolidation:
    run_at: "03:00"
```

---

## 🔌 API Endpoints

| Endpoint | Method | Rate Limit | Description |
|----------|--------|------------|-------------|
| `/health` | `GET` | 60/min | Health check — returns status & uptime |
| `/` | `GET` | — | API info & docs link |
| `/docs` | `GET` | — | Interactive Swagger UI |
| `/chat` | `POST` | 30/min | Send a message, get AI response |
| `/agents` | `GET` | — | List all active agents |
| `/status` | `GET` | — | System & agent status |

### API Key Authentication (Optional)

When `JARVIS_API_KEY` is set in `.env`:

```bash
curl -H "X-API-Key: your_secret_key" http://localhost:8000/chat
```

---

## 🛠️ Development

### Run Tests

```bash
pytest tests/ -v --cov=jarvis
```

**88 tests** covering memory system, API endpoints, and agent structure — all passing.

### Project Structure

```
Jarvis/
├── config/                     # YAML configurations
│   ├── agents.yaml             # Agent settings
│   └── config.template.yaml    # Template
├── jarvis/
│   ├── api/                    # FastAPI backend
│   │   ├── main.py             # App entry + middleware
│   │   └── routes/             # Endpoint routers
│   ├── v2/                     # Core v2 system
│   │   ├── core/               # LLM router, orchestrator, event bus
│   │   ├── agents/             # 8 specialized agents
│   │   └── memory/             # 3-layer unified memory
│   └── actions/                # Local tools (weather, apps, etc.)
├── jarvis-desktop/             # React + Vite + Tauri GUI
│   ├── src/
│   └── package.json
├── tests/                      # Pytest test suite
├── docs/                       # Documentation
├── pyproject.toml              # Project metadata + deps
└── start-jarvis-desktop.bat    # One-click launcher
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, Uvicorn, Pydantic |
| **LLM** | Ollama, LangChain, tiktoken |
| **Memory** | ChromaDB, SQLite + FTS5, sentence-transformers |
| **Agents** | Custom multi-agent framework with event bus + blackboard |
| **RPA** | pyautogui, mss, EasyOCR, OpenCV |
| **Voice** | Whisper, SpeechRecognition, edge-tts |
| **Frontend** | React 18, TypeScript, Vite 5, Tailwind CSS |
| **Desktop** | Tauri |

---

## 📜 License

[MIT License](LICENSE) — Copyright (c) 2025 WexyS

Free to use, modify, and distribute. No warranty.

---

<div align="center">

**Built with ❤️ and local compute.**

</div>
