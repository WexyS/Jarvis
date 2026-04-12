# Jarvis v2.0 — Complete Architecture Documentation

> **Jarvis** is an independent, locally-hosted, fully autonomous AI assistant. Built from scratch for privacy, speed, and complete autonomy on a high-end workstation (RTX 4080, 32GB RAM).

---

## 🏗️ System Architecture

### Core Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        JARVIS CORE ORCHESTRATOR                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Task Router  │  │ Agent Pool   │  │ Memory Bus   │  │ Safety Gate │ │
│  │ & Planner    │  │ Manager      │  │ (Event Bus)  │  │ & Guardrails│ │
│  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
│         │                │                 │                 │         │
│  ┌──────▼────────────────▼─────────────────▼─────────────────▼──────┐ │
│  │                    SHARED CONTEXT LAYER                          │ │
│  │  Working Memory  │  Task State  │  Resource Locks  │  Blackboard │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
         │                │                 │                 │
    ┌────▼────┐    ┌─────▼─────┐   ┌──────▼──────┐   ┌─────▼─────┐
    │ CODER   │    │RESEARCHER │   │ RPA-OPERATOR│   │HOME-CTRL  │
    │  Agent  │    │  Agent    │   │   Agent     │   │  Agent    │
    └────┬────┘    └─────┬─────┘   └──────┬──────┘   └─────┬─────┘
         │               │                │                │
    ┌────▼────┐    ┌─────▼─────┐   ┌──────▼──────┐   ┌─────▼─────┐
    │ Sandbox │    │ Web/Doc   │   │Mouse/Keyboard│   │IoT/MQTT  │
    │Executor │    │Scraper    │   │Screen Capture│   │API Hub   │
    └─────────┘    └───────────┘   └─────────────┘   └───────────┘
                              │
                    ┌─────────▼─────────┐
                    │   MEMORY ENGINE   │
                    │  ┌─────────────┐  │
                    │  │ Vector DB   │  │  ← Semantic similarity
                    │  │ (ChromaDB)  │  │
                    │  ├─────────────┤  │
                    │  │ Graph DB    │  │  ← Relational knowledge
                    │  │ (NetworkX)  │  │
                    │  ├─────────────┤  │
                    │  │ Episodic    │  │  ← Conversation history
                    │  │ Store       │  │
                    │  ├─────────────┤  │
                    │  │ Skill       │  │  ← Learned patterns
                    │  │ Library     │  │
                    │  └─────────────┘  │
                    │                   │
                    │ ┌───────────────┐ │
                    │ │ Self-Learning │ │  ← Failure analysis → lesson
                    │ │ Loop          │ │  ← Prompt auto-update
                    │ └───────────────┘ │
                    └───────────────────┘
```

---

## 📦 Project Structure

```
Jarvis/
├── jarvis/                        # Python Backend
│   ├── v2/                        # v2 Multi-Agent System
│   │   ├── core/                  # Core Engine
│   │   │   ├── orchestrator.py    # Central brain - intent routing, agent dispatch
│   │   │   ├── llm_router.py      # Multi-provider LLM routing (9 providers)
│   │   │   ├── providers.py       # Individual LLM providers (Groq, Gemini, etc.)
│   │   │   ├── hermes.py          # Hermes TAO loop integration
│   │   │   ├── hermes_tool.py     # Hermes tool definitions
│   │   │   ├── hermes_translator.py # Hermes schema translation
│   │   │   ├── hermes_prompt.py   # Hermes system prompts
│   │   │   ├── hermes_loop.py     # Hermes execution loop
│   │   │   ├── hermes_trajectory.py # Hermes trajectory tracking
│   │   │   ├── event_bus.py       # Pub/sub event system
│   │   │   ├── blackboard.py      # Shared context memory
│   │   │   ├── types.py           # Data structures
│   │   │   ├── skill_manager.py   # Skill/agent discovery
│   │   │   └── prompt.txt         # System prompt for LLM
│   │   ├── agents/                # Specialized Agents
│   │   │   ├── base.py            # Base Agent class
│   │   │   ├── coder.py           # Coder Agent - code generation & execution
│   │   │   ├── researcher.py      # Research Agent - web research
│   │   │   └── rpa_operator.py    # RPA Operator - screen/keyboard/mouse control
│   │   ├── memory/                # Memory Engine
│   │   │   ├── engine.py          # Vector + Graph DB + Self-learning
│   │   │   └── __init__.py
│   │   └── bootstrap.py           # v2 initialization entry point
│   ├── api/                       # FastAPI REST + WebSocket API
│   │   ├── main.py                # FastAPI app entry point
│   │   ├── models.py              # Pydantic request/response models
│   │   ├── routes/                # API routes
│   │   │   ├── chat.py            # WebSocket chat endpoint
│   │   │   ├── agents.py          # Agent invocation endpoints
│   │   │   └── status.py          # System health endpoint
│   │   └── ws_manager.py          # WebSocket connection manager
│   ├── actions/                   # Local Tools
│   │   ├── code_helper.py         # Code assistance
│   │   ├── computer_settings.py   # System settings control
│   │   ├── open_app.py            # Application launching
│   │   ├── weather_report.py      # Weather reporting
│   │   └── web_search.py          # Web search
│   ├── cli.py                     # CLI entry point
│   ├── gui_app.py                 # Tkinter GUI (legacy)
│   ├── config.py                  # Configuration management
│   └── voice_pipeline.py          # Voice pipeline (STT → LLM → TTS)
├── jarvis-desktop/                # React + Tailwind + Tauri GUI
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatArea.tsx       # Chat area with streaming
│   │   │   ├── InputBox.tsx       # Text input + mode selector
│   │   │   ├── Sidebar.tsx        # Agent status panel
│   │   │   ├── StatusBadge.tsx    # Connection health badge
│   │   │   └── StreamingMessage.tsx # Markdown + syntax highlighting
│   │   └── hooks/
│   │       └── useJarvis.ts       # WebSocket hook for Jarvis communication
│   ├── tailwind.config.js         # Tailwind CSS configuration
│   ├── tsconfig.json              # TypeScript configuration
│   └── vite.config.ts             # Vite build configuration
├── docs/                          # Documentation
│   ├── README.md                  # Main documentation
│   ├── USAGE.md                   # Usage guide
│   ├── ARCHITECTURE.md            # This file
│   ├── COMPARISON.md              # Project comparison
│   ├── AUDIT_REPORT.md            # Debug report
│   ├── PROMPT.txt                 # System prompt
│   └── TECH_STACK.md              # Technology stack
├── config/                        # Configuration
│   ├── config.yaml                # Main configuration
│   └── config.template.yaml       # Configuration template
├── scripts/                       # Helper scripts
├── data/                          # Runtime data (memory, cache)
├── workspace/                     # Coder Agent workspace
├── .env                           # API keys
├── .env.example                   # API key template
├── pyproject.toml                 # Python project definition
└── README.md                      # Root README
```

---

## 🤖 Agents

### Coder Agent (`coder.py`)
- **Role:** Code generation, execution, testing, and iteration
- **LLM:** `qwen2.5-coder:7b` (local) + cloud fallback
- **Capabilities:**
  - Self-healing loop: write → execute → read stack trace → fix → retry (max 5 iterations)
  - Multi-language support: Python, JavaScript, TypeScript, C++, C#, Go, Rust, Java, etc.
  - Sandboxed execution environment
  - Test generation and execution
  - File I/O operations within workspace

### Researcher Agent (`researcher.py`)
- **Role:** Web research with citations and synthesis
- **LLM:** `qwen2.5:14b` (local) + cloud fallback
- **Capabilities:**
  - Web search via DuckDuckGo
  - URL fetching and content extraction
  - Multi-hop research with citations
  - Local document RAG (Retrieval Augmented Generation)
  - Citation tracking and source verification
  - Content synthesis and summarization

### RPA Operator Agent (`rpa_operator.py`)
- **Role:** Screen control, mouse/keyboard automation
- **LLM:** `qwen2.5:14b` (local) + cloud fallback
- **Capabilities:**
  - Screen capture via `mss`
  - OCR reading via `easyocr`
  - Mouse movement, clicking, drag-drop via `pyautogui`
  - Keyboard input and shortcuts
  - Application launching
  - Window management
  - Autonomous action planning with LLM
  - Visual verification after actions

---

## 🧠 Memory Engine

### Three-Layer Memory
1. **Vector DB (ChromaDB):** Semantic similarity search for tasks/outcomes
   - Stores task contexts, LLM responses, and interaction histories
   - Enables semantic search for similar past interactions
   - Used for context retrieval during conversations

2. **Graph DB (NetworkX):** Knowledge graph of concepts and relationships
   - Stores relationships between concepts, tools, and tasks
   - Enables relationship discovery between different concepts
   - Used for discovering connections between different tools and tasks

3. **Episodic Store:** Conversation history and interaction logs
   - Stores complete conversation histories with timestamps
   - Enables tracking of past interactions and their outcomes
   - Used for context retrieval and pattern discovery

### Self-Learning Loop
- **Failure Analysis:** When a tool fails, the error is analyzed and stored
- **Prompt Updates:** System prompts are updated based on learned patterns
- **Skill Updates:** Tool capabilities are updated based on usage patterns
- **Pattern Discovery:** Patterns are discovered from interaction histories

---

## 🔌 LLM Providers

### Provider Priority Order
1. **Groq** (`llama-3.1-8b-instant`) — Fastest, 300-500 tok/s
2. **OpenRouter Free** — Free tier, no credits needed
3. **OpenRouter** — OpenRouter paid models
4. **Gemini** (`gemini-2.0-flash`) — Google's Gemini model
5. **OpenAI** (`gpt-4o`) — OpenAI's GPT-4 model

### Provider Fallback
- When a provider fails, the next provider in the priority order is tried
- If all providers fail, an error is returned to the user
- The fallback chain is: Groq → OpenRouter Free → OpenRouter → Gemini → OpenAI

---

## 📡 API Endpoints

### FastAPI REST Endpoints
- `GET /` — Service information
- `GET /status` — System health check
- `GET /agents` — List available agents
- `POST /agents/{name}/invoke` — Invoke a specific agent

### WebSocket Endpoints
- `WS /ws/chat` — Real-time chat with streaming
- `WS /ws/agents` — Agent status updates

---

## 🛠️ Local Tools

### Code Helper (`code_helper.py`)
- **Description:** Code assistance and generation
- **Parameters:** `code` (optional) — Code to analyze or generate
- **Is Async:** False

### Computer Settings (`computer_settings.py`)
- **Description:** System settings control
- **Parameters:** `setting` (required) — Setting to control
- **Is Async:** False

### Open App (`open_app.py`)
- **Description:** Application launching
- **Parameters:** `app_name` (required) — Application name to launch
- **Is Async:** False

### Weather Report (`weather_report.py`)
- **Description:** Weather reporting
- **Parameters:** `location` (required) — Location for weather report
- **Is Async:** False

### Web Search (`web_search.py`)
- **Description:** Web search via DuckDuckGo
- **Parameters:** `query` (required) — Search query
- **Is Async:** False

---

## 🎯 Usage Instructions

### Backend
```bash
cd C:\Users\nemes\Desktop\Jarvis
python -m jarvis.api.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd C:\Users\nemes\Desktop\Jarvis\jarvis-desktop
npm run dev
```

### Voice Pipeline
```bash
cd C:\Users\nemes\Desktop\Jarvis
python -m jarvis.voice_pipeline
```

### CLI
```bash
cd C:\Users\nemes\Desktop\Jarvis
python -m jarvis.cli
```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama (for local LLM inference)
- RTX 4080 (recommended)

### Setup Steps
1. Clone the repository
2. Install dependencies: `pip install -e .`
3. Start Ollama: `ollama serve`
4. Pull models: `ollama pull qwen2.5:14b`
5. Start backend: `python -m jarvis.api.main:app --host 0.0.0.0 --port 8000`
6. Start frontend: `cd jarvis-desktop && npm run dev`

---

## 📈 Roadmap

### ✅ Completed
- System Architecture
- Multi-Agent System
- Hermes Tool Calling
- Voice Pipeline
- GUI (React + Tailwind + Tauri)
- GitHub Repository

### 🚧 In Progress
- Model Fine-Tuning
- RPA Testing
- Voice Command Integration
- Error Handling Improvements

### 📋 Future
- Custom Model Training
- Advanced RPA Features
- Voice Command Recognition
- Real-Time Error Recovery
- Advanced Pattern Discovery
- Multi-Modal Support

---

## 📝 Notes

This is an independent, locally-hosted, fully autonomous AI assistant. It is not affiliated with any other project or organization. Built from scratch for privacy, speed, and complete autonomy.
