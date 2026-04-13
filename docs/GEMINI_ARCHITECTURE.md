# Ultron v2.0 — Complete Architecture Document (For Gemini)

## 1. PROJECT OVERVIEW

**Name:** Ultron v2.0 (Advanced Unified Learning & Tactical Response Operations Network)
**Type:** Personal AI Assistant with Multi-Agent, Self-Healing, RPA, and Web GUI
**Language:** Python 3.11 (Primary), TypeScript/React (Frontend)
**Runtime:** Local (RTX 4080 Mobile 12GB VRAM, 32GB RAM, Windows 11)
**LLM Models:** qwen2.5:14b (local via Ollama), Google Gemini 2.0 Flash (cloud via OpenRouter), Claude Sonnet 4 (cloud via OpenRouter)
**Status:** Production-Ready

## 2. PROJECT STRUCTURE

```
Ultron/
│
├── start.bat                              # Tkinter GUI Launcher
├── start-ultron-desktop.bat               # Web GUI Launcher (React + FastAPI)
├── .env                                   # API Keys (OpenRouter, OpenAI)
├── pyproject.toml                         # Python dependencies
├── README.md                              # Root README
│
├── config/
│   └── config.yaml                        # Main configuration (model, TTS, email, calendar, documents, coding)
│
├── data/
│   └── memory_v2/                         # Vector DB (ChromaDB), Graph DB, Lessons Store (runtime)
│
├── workspace/                             # Coder Agent sandbox (code execution output)
│
├── ultron/
│   ├── cli.py                             # CLI Entry Point — launches Tkinter GUI, initializes v2 orchestrator
│   ├── gui_app.py                         # Tkinter GUI (Mark-XXXV animated interface, 550+ lines)
│   ├── config.py                          # Pydantic config management
│   ├── voice_pipeline.py                  # Legacy voice pipeline: STT (Google) → LLM → TTS (edge-tts)
│   ├── tts_voice.py                       # edge-tts + pyttsx3 engine
│   ├── memory.py                          # Legacy memory: ResponseCache + UserMemory
│   ├── llm.py                             # Legacy LLM router
│   ├── coding.py                          # Legacy coding assistant
│   ├── research.py                        # Legacy research assistant
│   │
│   ├── api/                               # FastAPI Backend (Web GUI)
│   │   ├── main.py                        # FastAPI app + lifespan (startup/shutdown)
│   │   ├── ws_manager.py                  # WebSocket connection manager
│   │   ├── models.py                      # Pydantic request/response models
│   │   └── routes/
│   │       ├── chat.py                    # /ws/chat WebSocket endpoint
│   │       ├── agents.py                  # /agents/* REST endpoints
│   │       └── status.py                  # /status, /health endpoints
│   │
│   ├── actions/                           # Local Tools
│   │   ├── code_helper.py                 # Code generation/execution helper
│   │   ├── computer_settings.py           # System settings (volume, WiFi, power)
│   │   ├── open_app.py                    # App launcher (Windows/Mac/Linux with os.startfile fallback)
│   │   ├── weather_report.py              # Weather browser opener
│   │   └── web_search.py                  # DuckDuckGo web search
│   │
│   └── v2/                                # Multi-Agent System (Core Engine)
│       ├── bootstrap.py                   # Terminal entry point for v2
│       │
│       ├── core/
│       │   ├── orchestrator.py            # CENTRAL BRAIN — intent routing, agent dispatch, memory, HITL
│       │   ├── llm_router.py              # Hybrid LLM routing (9 providers with auto-fallback)
│       │   ├── providers.py               # Individual LLM providers (Groq, Gemini, Cloudflare, Together, HF, OpenRouter)
│       │   ├── event_bus.py               # Pub/sub event system for inter-agent communication
│       │   ├── blackboard.py              # Shared context memory between agents
│       │   ├── types.py                   # Data structures (Task, AgentRole, AgentStatus, ToolCall)
│       │   ├── hermes.py                  # Hermes TAO (Thought-Action-Observation) loop
│       │   └── prompt.txt                 # SYSTEM PROMPT — Ultron identity, rules, Turkish language enforcement
│       │
│       ├── agents/
│       │   ├── base.py                    # Base Agent class (LLM routing, event subscription, blackboard access)
│       │   ├── coder.py                   # Coder Agent — writes, executes, self-heals code (max 5 iterations)
│       │   ├── researcher.py              # Researcher Agent — web search (DDGS), URL scraping, synthesis
│       │   └── rpa_operator.py            # RPA Operator — screen capture (mss), OCR (easyocr), mouse/keyboard (pyautogui), app launching
│       │
│       └── memory/
│           └── engine.py                  # Memory Engine — ChromaDB (vector), NetworkX (graph), Lessons Store
│
└── ultron-desktop/                        # Web GUI (React 18 + TypeScript + Tailwind + Vite)
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── tsconfig.json
    ├── index.html
    ├── src/
    │   ├── main.tsx                       # React entry point
    │   ├── App.tsx                        # Main app layout
    │   ├── index.css                      # Tailwind + custom styles (dark theme, scrollbars)
    │   ├── vite-env.d.ts                  # TypeScript declarations
    │   ├── hooks/
    │   │   └── useUltron.ts               # WebSocket hook (auto-reconnect, streaming tokens, status polling)
    │   └── components/
    │       ├── ChatArea.tsx               # Message display with markdown rendering
    │       ├── InputBox.tsx               # Text input + mode selector (Chat/Code/Research/RPA)
    │       ├── Sidebar.tsx                # Agent status panel, LLM providers, memory stats
    │       ├── StatusBadge.tsx            # Connection health indicator
    │       └── StreamingMessage.tsx       # Markdown + syntax highlighting (react-syntax-highlighter)
    │
    └── src-tauri/                         # Tauri (Rust) native shell
        ├── tauri.conf.json
        ├── Cargo.toml
        ├── build.rs
        └── src/main.rs
```

## 3. CORE ARCHITECTURE FLOW

### User Input Processing Pipeline
```
User Input (GUI/Web/Terminal)
    │
    ▼
┌─────────────────────────────────┐
│  Orchestrator (core/orchestrator.py) │
│                                   │
│  1. Intent Classification (keyword-based, <1ms)  │
│     - code / research / weather / app / system / file / chat │
│     - 6 categories with Turkish + English keywords │
│                                   │
│  2. Routing:                      │
│     - code → Coder Agent         │
│     - research → Researcher Agent │
│     - weather → Weather Handler  │
│     - system → System Info Handler │
│     - file → File Read/List Handler │
│     - app/RPA → HITL Confirmation │
│     - chat → General Chat (LLM)  │
│                                   │
│  3. Memory Storage:               │
│     - Every interaction saved to memory_v2 │
│     - Lesson context loaded for future responses │
└─────────────────────────────────┘
```

### Intent Keywords (INTENT_KEYWORDS dict)
- **code:** "kod yaz", "kod", "yazılım", "program", "python", "javascript", "calculate", "hesapla", "debug", "çalıştır", "execute"
- **research:** "araştır", "research", "bul", "search", "nedir", "explain", "öğren", "learn", "hakkında"
- **weather:** "hava durumu", "weather", "sıcaklık", "temperature", "yağmur", "rain", "kar", "snow", "güneşli", "rüzgar"
- **app:** "aç", "open", "başlat", "start", "launch", "çalıştır", "run", "uygulama", "app", "steam", "chrome", "spotify", "youtube", "twitter", "reddit", "github", "gmail", "google"
- **system:** "sistem", "system", "cpu", "ram", "disk", "batarya", "battery", "saat", "time", "durum", "status"
- **file:** "dosya", "file", "oku", "read", "yaz", "write", "kaydet", "save", "listele", "list", "klasör", "folder"

### Human-in-the-Loop (HITL) Protection
- **RPA tasks require approval.** When user asks to open an app/website, system returns a confirmation prompt instead of executing autonomously.
- **Message shown:** "🔒 RPA Aksiyon Onayı Gerekli. Planlanan işlem: [action]. Devam etmek istiyor musunuz? Onaylamak için 'evet' veya 'onay' yazın."

## 4. LLM PROVIDER ECOSYSTEM (9 Providers)

### Provider Priority Order (Auto-Fallback)
1. **Groq** — `meta-llama/llama-3.1-8b-instruct` (fastest, ~300 tok/s) — needs `GROQ_API_KEY`
2. **OpenRouter Free** — `google/gemini-2.0-flash-exp:free` (Turkish excellent, free) — needs `OPENROUTER_API_KEY` ✅ ACTIVE
3. **Ollama** — `qwen2.5:14b` (local, unlimited, 12GB VRAM) ✅ ACTIVE
4. **Gemini** — `gemini-2.0-flash` (1M context, free tier) — needs `GEMINI_API_KEY`
5. **Cloudflare** — `@cf/qwen/qwen2.5-7b-instruct` (10K/day free) — needs `CLOUDFLARE_API_KEY` + `CLOUDFLARE_ACCOUNT_ID`
6. **Together** — `Qwen/Qwen2.5-72B-Instruct-Turbo` ($25 free credit) — needs `TOGETHER_API_KEY`
7. **HuggingFace** — `Qwen/Qwen2.5-72B-Instruct` (free inference API) — needs `HF_API_KEY`
8. **OpenRouter Paid** — `anthropic/claude-sonnet-4` — needs `OPENROUTER_API_KEY` ✅ ACTIVE
9. **OpenAI** — `gpt-4o` (last resort fallback) — needs `OPENAI_API_KEY` ✅ ACTIVE

### Current Active Providers (no additional keys needed)
- ✅ OpenRouter Free (Gemini 2.0 Flash)
- ✅ Ollama (qwen2.5:14b)
- ✅ OpenRouter Paid (Claude Sonnet 4)
- ✅ OpenAI (gpt-4o)

### Resource Leak Fix Applied
- All `AsyncOpenAI` clients now call `await client.close()` after each request.
- `httpx.AsyncClient` uses context manager (`async with`).
- Orchestrator `stop()` cleans up event bus handlers.

## 5. AGENTS (3 Active + HITL Protection)

### Coder Agent (`ultron/v2/agents/coder.py`)
- **LLM:** Dedicated `qwen2.5-coder:7b` via Ollama (local)
- **Capability:** Writes code → executes in sandbox → reads stack trace → auto-fixes → retries (max 5 iterations)
- **Languages:** Python, JavaScript, TypeScript, and more
- **Self-Healing Loop:**
  1. Generate code from task description
  2. Execute in `./workspace/` directory
  3. If error: read stderr → send to LLM → generate fix → retry
  4. Max 5 iterations before failure

### Researcher Agent (`ultron/v2/agents/researcher.py`)
- **LLM:** `qwen2.5:14b` via main router
- **Capability:** Web search (DDGS) → URL fetching → content extraction → synthesis with citations
- **Package:** `ddgs` (replacement for deprecated `duckduckgo_search`)
- **Process:** Search → Read top 5 URLs → Synthesize findings

### RPA Operator Agent (`ultron/v2/agents/rpa_operator.py`)
- **LLM:** `qwen2.5:14b` via main router
- **Capabilities:**
  - Screen capture via `mss` (context manager for Windows TLS fix)
  - OCR via `easyocr` (English + Turkish, GPU enabled)
  - Mouse/keyboard via `pyautogui`
  - App launching via `subprocess` + `os.startfile` fallback
  - Website opening via `webbrowser.open()`
  - Window switching via `alt+tab`
- **Two-Path Execution:**
  - **FAST PATH:** Direct app/website launch (no screenshot, instant) — detects keywords like "steam", "youtube", "sozluk"
  - **FULL PATH:** Screenshot → OCR → LLM planning → step-by-step execution with verification loop
- **Focus Verification:** Before any keystroke, checks if screen shows `localhost`/`ultron`/`517` → auto `alt+tab` if wrong window
- **Markdown Stripping:** Strips ``` blocks from LLM responses before JSON parsing

### Human-in-the-Loop (HITL)
- **App/Website tasks:** Returns confirmation prompt instead of executing
- **RPA tasks with known targets:** Shows plan and asks for approval
- **Unknown RPA tasks:** Falls through to full autonomous RPA loop (still requires HITL)

## 6. MEMORY ENGINE (`ultron/v2/memory/engine.py`)

### Three-Layer Memory
1. **Vector DB (ChromaDB):** Semantic similarity search for tasks/outcomes
   - Stores: `{entry_id, content, embedding, metadata, created_at}`
   - Used for: finding relevant past interactions, lesson context
2. **Graph DB (NetworkX):** Knowledge graph of concepts and relationships
   - Stores: concepts with descriptions, relationships with evidence
   - Used for: concept mapping, relationship discovery
3. **Lessons Store:** Failure → lesson → prompt auto-update
   - Stores: `{failure, error, root_cause, fix, domain, created_at}`
   - Used for: preventing repeat mistakes

### Anti-Loop Protection
- Response cache: if same query hits >5 times, cache is cleared
- GUI: same message sent within 3 seconds is ignored
- Memory: each interaction stored with timestamp, prevents duplicate processing

## 7. WEB GUI (React + TypeScript + FastAPI + WebSocket)

### Architecture
```
Browser (http://localhost:5173)
    │ WebSocket: ws://localhost:8000/ws/chat
    ▼
FastAPI Backend (http://localhost:8000)
    │
    ▼
Orchestrator → Agent → Response
    │
    ▼
WebSocket Streaming → Browser
```

### Frontend Components
- **Sidebar.tsx:** Shows 3 agents (Coder, Researcher, RPA), LLM providers status, memory stats
- **ChatArea.tsx:** Message display with markdown rendering, auto-scroll
- **InputBox.tsx:** Text input with mode selector (Chat/Code/Research/RPA), anti-loop (3s debounce)
- **StatusBadge.tsx:** Connection health indicator
- **StreamingMessage.tsx:** Markdown + syntax highlighting for code blocks

### WebSocket Hook (`useUltron.ts`)
- Auto-connect on mount
- Auto-reconnect (max 10 attempts, 3s interval)
- Token streaming via response buffer (avoids stale closure bug)
- Status polling every 5 seconds

### Backend Endpoints
- `GET /` — Service info
- `GET /health` — Health check (`{"status":"healthy","orchestrator":true}`)
- `GET /status` — Full system status (agents, providers, memory)
- `GET /providers` — All LLM providers with status
- `WS /ws/chat` — Real-time chat with streaming
- `POST /agents/invoke` — Direct agent invocation

## 8. KEY DEPENDENCIES

### Python (venv)
```
ollama, ddgs, easyocr, mss, pyautogui, pyscreeze, mouseinfo
openai, httpx, fastapi, uvicorn[standard], websockets, sse-starlette, python-multipart
chromadb, networkx, sentence-transformers, psutil, pydantic, python-dotenv
torch, torchaudio, edge-tts, pygame, sounddevice, soundfile, numpy
```

### TypeScript/React (ultron-desktop)
```
react, react-dom, typescript, vite, @vitejs/plugin-react
tailwindcss, postcss, autoprefixer
lucide-react, react-markdown, react-syntax-highlighter
@tauri-apps/api, @tauri-apps/cli
```

## 9. CRITICAL FIXES APPLIED (Chronological)

1. **Infinite Loop** — Removed Hermes loop from orchestrator, added GUI anti-loop (3s debounce)
2. **Chinese Hallucination** — Changed OpenRouter default model to `google/gemini-2.0-flash-exp:free`, added language enforcement regex validation
3. **duckduckgo_search → ddgs** — Package renamed, updated import in `researcher.py`
4. **mss Windows Threading Bug** — Replaced instance-level `mss.mss()` with `with mss.mss() as sct:` context manager
5. **webbrowser UnboundLocalError** — Added `import webbrowser` at top of `rpa_operator.py`
6. **LLM JSON Hallucination** — Prompt now says "CRITICAL: Return ONLY a raw JSON array", code strips ``` blocks
7. **Resource Leaks (Unclosed Sockets)** — All `AsyncOpenAI` clients now call `await client.close()`
8. **Intent Routing** — Added 15+ app/website keywords to `INTENT_KEYWORDS["app"]`
9. **FastAPI Chat.py Corruption** — Rewrote corrupted file cleanly
10. **HITL Protection** — RPA tasks now require user confirmation before autonomous execution

## 10. CONFIGURATION

### .env (API Keys)
```
OPENROUTER_API_KEY=sk-or-v1-... (Active — Free tier + Paid tier)
OPENAI_API_KEY=sk-proj-... (Active — Fallback)
# GROQ_API_KEY= (Not set)
# GEMINI_API_KEY= (Not set)
# TOGETHER_API_KEY= (Not set)
# CLOUDFLARE_API_KEY= (Not set)
# HF_API_KEY= (Not set)
```

### config/config.yaml
```yaml
model:
  ollama_model: "qwen2.5:14b"
  ollama_base_url: "http://localhost:11434"
  max_tokens: 4096
  temperature: 0.7
  language: "tr"
```

### System Prompt (`ultron/v2/core/prompt.txt`)
- Identity: ULTRON v2.0 Multi-Agent
- Owner: Eren
- Location: Windows 11, RTX 4080 Mobile (12GB VRAM), 32GB RAM
- Language: MUTLAKA Türkçe cevap ver. İngilizce, Çince, başka dil KULLANMA.
- Personality: Helpful, concise, accurate

## 11. HOW TO RUN

### Option A: Tkinter GUI (Console)
```bash
start.bat
```

### Option B: Web GUI (React + FastAPI)
```bash
start-ultron-desktop.bat
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

### Option C: Terminal (v2 Multi-Agent)
```bash
python -m ultron.v2.bootstrap
```

### Option D: Terminal (Legacy Voice Pipeline)
```bash
python -m ultron.cli --cli
```

## 12. TESTING COMMANDS

| Input | Expected Result |
|-------|----------------|
| `selam ultron` | 🇹🇷 Turkish response, no Chinese characters |
| `İstanbul hava durumu` | 🌤 Browser opens weather |
| `cpu durumu` | 🖥 CPU/RAM/Disk info |
| `kod yaz fibonacci` | 💻 [0, 1, 1, 2, 3, 5, 8, 13, 21, 34] |
| `steam'i aç` | ✅ Steam opens instantly |
| `chrome aç` | ✅ Chrome opens instantly |
| `youtube git` | ✅ YouTube opens in browser |
| `readme dosyasını oku` | 📄 README.md content |
| `sozluk.gov.tr git` | 🔒 RPA confirmation prompt (HITL) |

---

**END OF ARCHITECTURE DOCUMENT**
This document contains every component, file, dependency, fix, and workflow in the Ultron v2.0 project. Give it to Gemini for full context awareness.
  
  
  
### Discovery  
- **Skills**: 1458 discovered from `~/.qwen/skills/` (directories + .md files)  
- **Agents**: 186 discovered from `~/.qwen/agents/` (directories + .md files)  
  
### How to Add More Skills/Agents  
1. Place `.md` file in `~/.qwen/skills/` or `~/.qwen/agents/`  
2. Or create directory with SKILL.md / AGENT.md inside  
3. Auto-discovered on next orchestrator start  
  
### Top Agent Categories (186 total)  
- Development: python-expert, react-specialist, typescript-expert, etc.  
- Infrastructure: cloud-architect, devops-engineer, kubernetes-specialist  
- Security: penetration-tester, security-auditor, vulnerability-scanner  
- AI/ML: ai-engineer, ml-engineer, mlops-engineer, rag-engineer  
- Design: ui-designer, ux-researcher, ui-component-generator  
- Data: data-engineer, data-scientist, database-expert, sql-pro  
  
### Integration Points  
- Orchestrator discovers skills/agents at startup via `skill_manager.py`  
- Intent classification matches user input to skill/agent names  
- Future: Skills can be invoked as tools via LLM function calling 
