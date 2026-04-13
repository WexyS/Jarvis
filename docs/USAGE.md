# Ultron v2.1 — Usage Guide

> **Last updated:** April 13, 2026  
> **Model:** Qwen 2.5 14B (local) + 12 cloud fallbacks  
> **Architecture:** Multi-Agent (8 agents) + Voice Pipeline + 3-Panel GUI

---

## Quick Start

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Python** | 3.10+ | Backend runtime |
| **Node.js** | 18+ | GUI build toolchain |
| **Ollama** | Latest | Local LLM runtime |

### One-Command Launch (Windows)

```bash
# Double-click or run:
start-ultron-desktop.bat
```

The script automatically:
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

# 3. Install Playwright Chromium (for workspace cloning)
playwright install chromium

# 4. Install & run Ollama
ollama pull qwen2.5:14b          # Download model
ollama serve                     # Start server

# 5. Start backend
python -m uvicorn ultron.api.main:app --host 127.0.0.1 --port 8000

# 6. Start frontend (in another terminal)
cd ultron-desktop && npm install && npm run dev
```

---

## 🖥️ GUI Usage

The GUI features a modern 3-panel layout:

```
┌─────────────────────────────────────────────────────────────────┐
│  Ultron v2.1                                    [⚡ Providers: 13]│
├──────────┬──────────────────────────────┬───────────────────────┤
│ Sidebar  │   Chat / Workspace           │   Inspector Panel     │
│ (240px)  │                              │   (300px)             │
│          │   ┌──────────────────────┐   │                       │
│ • Agents │   │  AI Response         │   │  • Agent Status       │
│ • Toggle │   │  (streaming)         │   │  • System Monitor     │
│          │   └──────────────────────┘   │  • Memory Stats       │
│          │   ┌──────────────────────┐   │  • Workspace Items    │
│          │   │  Your message...     │   │  • Provider Status    │
│          │   └──────────────────────┘   │                       │
├──────────┴──────────────────────────────┴───────────────────────┤
│  Status: ● Connected  |  Provider: Ollama  |  Latency: 312ms    │
└─────────────────────────────────────────────────────────────────┘
```

### Panel Toggle

Click the toggle button in the sidebar to switch between **Chat** and **Workspace** views in the center panel.

### Workspace Panel

Three tabs for workspace operations:

| Tab | Function | Description |
|-----|----------|-------------|
| **Clone** | Website Cloning | Clone any website URL, extracts UI components |
| **Generate** | App Generation | Generate a complete app from a text description |
| **Synthesize** | RAG Synthesis | Combine existing templates to create new apps |

---

## 🤖 Agents & Commands

Ultron uses **8 specialized agents** that are automatically selected based on your intent:

| Agent | Description | Example Commands |
|-------|-------------|------------------|
| **CoderAgent** | Code writing, debugging, execution | "Write fibonacci in Python" |
| **ResearcherAgent** | Web research, synthesis | "What is quantum computing?" |
| **RPAOperatorAgent** | Computer control (screen, OCR, input) | "Open Chrome" |
| **EmailAgent** | Email reading, summarization, sending | "Summarize my emails" |
| **SystemMonitorAgent** | CPU/RAM/disk monitoring | "What's the system status?" |
| **ClipboardAgent** | Clipboard content analysis | "Analyze the code in clipboard" |
| **MeetingAgent** | Meeting recording and transcription | "Start recording meeting" |
| **FileOrganizerAgent** | File organization, duplicate detection | "Organize my desktop" |

### Email Agent

```
"read my emails"           → List last 10 emails
"morning briefing"         → Summarize top 5 important emails
"write this to ahmet"      → Draft email
"send"                    → Send the draft
```

### Meeting Agent

```
"start recording"          → Start microphone recording
"stop meeting"            → Stop recording and transcribe
"summarize"               → Generate summary + action items
```

Output saved to: `data/meetings/YYYY-MM-DD_HH-MM.md`

### File Organizer

```
"organize desktop"        → Categorize desktop files
"find duplicates"         → Detect duplicate files
"organize downloads"      → Sort the Downloads folder
```

---

## 🧠 Memory System

Ultron uses a **3-layer unified memory** architecture:

### 1. Working Memory (Short-Term)
- Holds the last **20 messages** (deque)
- Token limit: **4000 tokens**
- Auto-summarizes when exceeded

### 2. Long-Term Memory
- **SQLite + FTS5**: Full-text lexical search
- **ChromaDB**: Vector-based semantic search
- **Hybrid search**: Combined via Reciprocal Rank Fusion (RRF)
- **Decay**: Unimportant memories older than 90 days fade away
- **Consolidation**: Auto-consolidation runs nightly at 03:00

### 3. Procedural Memory (Strategies)
- Stores successful task completion patterns
- Tracks exponential moving average success rates
- Recommends the best strategy for similar tasks

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# Email (optional)
ULTRON_EMAIL_USER=your@email.com
ULTRON_EMAIL_PASS=your_app_password

# API Key Protection (optional)
ULTRON_API_KEY=your_secret_key

# Ollama (default: local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b

# Cloud AI Providers (optional fallbacks)
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIzaSyD...
OPENROUTER_API_KEY=sk-or-v1-...
# ... add any provider keys you want
```

> 🔑 **No API keys are required.** Ollama runs locally. All cloud providers are optional fallbacks.

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
    whisper_model: "base"
    language: "en"
  files:
    watch_dirs:
      - "~/Downloads"
      - "~/Desktop"
```

---

## 🌐 13 AI Providers

Ultron routes to **13 AI providers** with task-aware selection and automatic fallback:

| # | Provider | Type | Cost | Best For |
|---|----------|------|------|----------|
| 1 | **Ollama** | Local | 🆓 Free | Privacy, code generation |
| 2 | **Groq** | Cloud | 🆓 Free | Speed (500 tok/s) |
| 3 | **DeepSeek** | Cloud | 💰 Cheap ($0.14/M tok) | Code, reasoning |
| 4 | **Anthropic** | Cloud | 💳 Paid | Understanding, analysis |
| 5 | **OpenRouter** | Cloud | 🆓+💳 Mixed | 200+ models, variety |
| 6 | **Gemini** | Cloud | 🆓 Free | Long context (1M) |
| 7 | **Mistral** | Cloud | 💳 Paid | GDPR compliance |
| 8 | **Fireworks** | Cloud | 💳 Paid | Fast inference |
| 9 | **Cloudflare** | Cloud | 🆓 Free (10K/day) | Reliable fallback |
| 10 | **Together** | Cloud | 💳 Free ($25 credit) | YLlama models |
| 11 | **Cohere** | Cloud | 💳 Paid | RAG reranking |
| 12 | **HuggingFace** | Cloud | 🆓 Free tier | Last free fallback |
| 13 | **OpenAI** | Cloud | 💳 Paid | Ultimate fallback |

### Smart Task Routing

| Task Type | Priority Order |
|-----------|---------------|
| `fast` | Groq → DeepSeek → Fireworks → Ollama → Cloudflare → OpenRouter |
| `code` | Ollama → DeepSeek → Anthropic → OpenRouter → Groq → Together |
| `long` | Gemini → OpenRouter → Anthropic → Ollama |
| `cheap` | Ollama → DeepSeek → Cloudflare → HuggingFace → Groq |
| `creative` | Anthropic → OpenRouter → Mistral → Ollama → Gemini |
| `private` | Ollama → Mistral → Cohere |
| `default` | All 13 in priority order |

---

## 🎙️ Voice & Language

Ultron supports **voice input and output** with multi-language support:

| Component | English | Turkish |
|-----------|---------|---------|
| **STT (Speech-to-Text)** | Google Web Speech API (en-US) + Whisper fallback | Google Web Speech API (tr-TR) + Whisper fallback |
| **TTS (Text-to-Speech)** | edge-tts `en-US-JennyNeural` | edge-tts `tr-TR-EmelNeural` |
| **VAD (Voice Activity)** | Silero VAD (universal) | Silero VAD (universal) |

### Setup Voice

```bash
# 1. Install voice dependencies
pip install SpeechRecognition openai-whisper torch edge-tts pygame sounddevice silero-vad

# 2. Set language in .env
ULTRON_LANGUAGE=en    # or "tr" for Turkish
```

### Voice Pipeline Flow

```
Microphone → Silero VAD → Google STT → Ollama LLM → edge-tts → Speaker
                            ↓ (fallback)
                        Whisper STT
```

- **Barge-in**: Ultron stops speaking when you start talking
- **Auto-detection**: Language is set via `ULTRON_LANGUAGE` in `.env`
- **Offline option**: Whisper STT works entirely offline

---

## 💼 Workspace + RAG

### Clone a Website

```bash
curl -X POST http://localhost:8000/api/v2/workspace/clone \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "extract_components": true}'
```

Downloads the full rendered HTML (via Playwright), detects UI components (navbar, hero, cards, footer), and saves to `workspace/cloned_templates/`.

### Generate an App from an Idea

```bash
curl -X POST http://localhost:8000/api/v2/workspace/generate \
  -H "Content-Type: application/json" \
  -d '{"idea": "Todo list application", "tech_stack": "html-css-js"}'
```

Ollama writes a complete, working app saved to `workspace/generated_apps/`.

### RAG Synthesis

```bash
curl -X POST http://localhost:8000/api/v2/workspace/synthesize \
  -H "Content-Type: application/json" \
  -d '{"user_command": "Create a dark-themed dashboard", "target_project": "my-dashboard"}'
```

ChromaDB finds the most relevant templates semantically, then LLM synthesizes a new app from them.

---

## 🔌 API Endpoints

### Core Endpoints

| Endpoint | Method | Rate Limit | Description |
|----------|--------|------------|-------------|
| `/` | `GET` | — | API info |
| `/health` | `GET` | 60/min | Health check — status + uptime |
| `/docs` | `GET` | — | Interactive Swagger UI |
| `/status` | `GET` | — | System, agents & providers status |

### AI Provider Endpoints

| Endpoint | Method | Rate Limit | Description |
|----------|--------|------------|-------------|
| `POST /api/v2/chat` | `POST` | 30/min | Multi-provider chat with smart routing |
| `GET /api/v2/providers/status` | `GET` | — | All providers availability + latency |

### Workspace Endpoints

| Endpoint | Method | Rate Limit | Description |
|----------|--------|------------|-------------|
| `POST /api/v2/workspace/clone` | `POST` | 5/min | Clone a website URL |
| `POST /api/v2/workspace/generate` | `POST` | 10/min | Generate app from idea |
| `POST /api/v2/workspace/synthesize` | `POST` | 10/min | RAG synthesis from templates |
| `GET /api/v2/workspace/list` | `GET` | — | List all workspace items |
| `GET /api/v2/workspace/search?q=...` | `GET` | — | Semantic search via ChromaDB |

### Example: Multi-Provider Chat

```bash
curl -X POST http://localhost:8000/api/v2/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "task_type": "fast",
    "preferred_provider": "groq"
  }'
```

Response:
```json
{
  "success": true,
  "content": "Hello! How can I help you today?",
  "provider": "groq",
  "model": "llama-3.3-70b-versatile",
  "tokens_used": 24,
  "latency_ms": 312
}
```

---

## 🛠️ Development

### Run Tests

```bash
pytest tests/ -v --cov=ultron
```

### Project Structure

```
Ultron/
├── config/                         # YAML configurations
├── ultron/
│   ├── api/                        # FastAPI backend
│   │   ├── main.py                 # App entry + 19 routes
│   │   └── routes/                 # chat, agents, status
│   ├── v2/                         # Core v2 system
│   │   ├── core/                   # Orchestrator, LLM router, Hermes TAO
│   │   ├── agents/                 # 8 specialized agents
│   │   ├── memory/                 # 3-layer unified memory
│   │   ├── providers/              # 13 AI providers + router + fallback
│   │   └── workspace/              # Playwright clone, code gen, RAG
│   └── actions/                    # Local tools
├── ultron-desktop/                 # React + Vite GUI
│   ├── src/
│   │   ├── App.tsx                 # 3-panel layout
│   │   ├── components/
│   │   │   ├── InspectorPanel.tsx  # 5-tab inspector
│   │   │   ├── WorkspacePanel.tsx  # Clone/Generate/Synthesize
│   │   │   └── Sidebar.tsx         # Agent status + panel switch
│   │   └── hooks/useUltron.ts      # WebSocket streaming
│   └── package.json
├── workspace/                      # Generated/cloned projects
├── data/                           # Memory, ChromaDB, meetings
├── tests/                          # Pytest test suite
├── pyproject.toml                  # Project metadata + deps
└── start-ultron-desktop.bat        # One-click launcher
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, Uvicorn, Pydantic |
| **LLM** | Ollama, LangChain, tiktoken |
| **Providers** | 13 providers with smart routing + auto-fallback |
| **Memory** | ChromaDB, SQLite + FTS5, sentence-transformers |
| **Workspace** | Playwright, ChromaDB, CodeGenerator, RAG Synthesizer |
| **Agents** | Custom multi-agent framework with event bus + blackboard |
| **RPA** | pyautogui, mss, EasyOCR, OpenCV |
| **Voice** | Whisper, SpeechRecognition, edge-tts |
| **Frontend** | React 18, TypeScript, Vite 5, Tailwind CSS, Framer Motion |
| **Desktop** | Tauri |

---

## 🔍 Troubleshooting

### GUI won't open / freezes
```bash
# Check Ollama
ollama ls
ollama serve

# Install dependencies
pip install -e .
```

### No sound from TTS
```bash
pip install edge-tts pygame
```

### Microphone not detected
```bash
python -m ultron.cli --list-mics
python -m ultron.cli --test-mic
```

### "No LLM providers available" error
```bash
# Is Ollama running?
ollama serve

# Is the model downloaded?
ollama pull qwen2.5:14b
```

---

## 📜 License

[MIT License](../LICENSE) — Copyright (c) 2025–2026 WexyS

Free to use, modify, and distribute. No warranty.

---

<div align="center">

**Built with ❤️ and local compute. 13 AI providers, 8 agents, infinite possibilities.**

</div>
