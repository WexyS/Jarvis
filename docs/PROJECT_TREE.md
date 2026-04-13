# ULTRON v2.0 — Project Structure

```
Ultron/
│
├── start.bat                    # Tek tıkla başlatıcı (Ollama + model kontrolü)
├── start-ultron-desktop.bat     # GUI + Desktop launcher
├── pyproject.toml               # Python dependencies
├── .env                         # API keys (OpenRouter, Groq, Gemini, etc.)
├── .env.example                 # API key template
├── .gitignore
├── README.md                    # Root README (kısa)
│
├── config/
│   ├── config.yaml              # Ana yapılandırma
│   └── config.template.yaml     # Template
│
├── docs/
│   ├── README.md                # Ana dokümantasyon
│   ├── USAGE.md                 # Kullanım kılavuzu
│   ├── ARCHITECTURE.md          # Mimari diyagram
│   ├── COMPARISON.md            # Proje karşılaştırma raporu
│   ├── AUDIT_REPORT.md          # Debug raporu
│   ├── PROMPT.txt               # Sistem promptu
│   └── TECH_STACK.md            # Teknoloji yığını
│
├── scripts/                     # Yardımcı scriptler
│   ├── audit_v2.py
│   ├── ultron_auto_patcher.py
│   └── test_audio.py
│
├── data/                        # Runtime veriler
│   ├── memory_v2/               # Vector + Graph DB
│   └── memory/                  # Legacy cache
│
├── workspace/                   # Coder Agent çalışma alanı
│
├── ultron/                      # Python Backend
│   ├── cli.py                   # CLI entry point (GUI başlatır)
│   ├── config.py                # Pydantic config
│   ├── gui_app.py               # Tkinter Mark-XXXV GUI
│   ├── voice_pipeline.py        # STT → LLM → TTS pipeline
│   ├── tts_voice.py             # edge-tts engine
│   ├── memory.py                # ResponseCache + UserMemory
│   ├── llm.py                   # Legacy LLM router
│   ├── coding.py                # Legacy coding assistant
│   ├── research.py              # Legacy research assistant
│   │
│   ├── api/                     # FastAPI Backend (YENİ)
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app + lifespan
│   │   ├── ws_manager.py        # WebSocket manager
│   │   ├── models.py            # Pydantic models
│   │   └── routes/
│   │       ├── chat.py          # /ws/chat WebSocket
│   │       ├── agents.py        # /agents/* REST
│   │       └── status.py        # /status, /health
│   │
│   ├── v2/                      # Multi-Agent System (YENİ)
│   │   ├── __init__.py
│   │   ├── bootstrap.py         # v2 terminal entry point
│   │   │
│   │   ├── core/
│   │   │   ├── orchestrator.py  # Central brain + agent routing
│   │   │   ├── llm_router.py    # Hybrid LLM routing (8 providers)
│   │   │   ├── providers.py     # Groq, Gemini, Cloudflare, etc.
│   │   │   ├── event_bus.py     # Pub/sub event system
│   │   │   ├── blackboard.py    # Shared context
│   │   │   ├── hermes.py        # Hermes TAO loop
│   │   │   ├── hermes_*.py      # Hermes components
│   │   │   ├── types.py         # Data structures
│   │   │   └── prompt.txt       # Sistem promptu
│   │   │
│   │   ├── agents/
│   │   │   ├── base.py          # Base Agent class
│   │   │   ├── coder.py         # Self-healing code agent
│   │   │   ├── researcher.py    # Deep research agent
│   │   │   └── rpa_operator.py  # Computer use agent
│   │   │
│   │   └── memory/
│   │       └── engine.py        # Vector+Graph+Lessons
│   │
│   └── actions/                 # Local tools
│       ├── code_helper.py
│       ├── computer_settings.py
│       ├── open_app.py
│       ├── weather_report.py
│       └── web_search.py
│
└── ultron-desktop/              # React + Tauri GUI (YENİ)
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── tsconfig.json
    ├── index.html
    │
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── index.css
    │   ├── vite-env.d.ts
    │   │
    │   ├── hooks/
    │   │   └── useUltron.ts     # WebSocket hook (streaming)
    │   │
    │   └── components/
    │       ├── ChatArea.tsx     # Message display
    │       ├── InputBox.tsx     # Text input + mode selector
    │       ├── Sidebar.tsx      # Agent status panel
    │       ├── StatusBadge.tsx  # Connection health
    │       └── StreamingMessage.tsx  # Markdown + code highlight
    │
    └── src-tauri/
        ├── tauri.conf.json
        ├── Cargo.toml
        ├── build.rs
        └── src/main.rs
```

## Key Systems

### 1. LLM Routing (8 Providers)
```
openrouter/free → ollama → groq → gemini → cloudflare → together → hf → openai
```

### 2. Agent System
```
Orchestrator
├── Coder Agent (qwen2.5-coder:7b) — write → execute → self-heal
├── Researcher Agent (qwen2.5:14b) — web search + synthesis
└── RPA Operator (qwen2.5:14b) — screen/keyboard/mouse control
```

### 3. Memory Engine
```
ChromaDB (Vector) + NetworkX (Graph) + Lessons Store
```

### 4. GUI Layers
```
Tkinter GUI (legacy) ←→ orchestrator (text input)
FastAPI + WebSocket ←→ React GUI (modern)
Tauri (Rust shell) ←→ native OS integration
```

### 5. Voice Pipeline
```
Microphone → Silero VAD → Google STT → Whisper (fallback) → LLM → edge-tts → Speaker
```
