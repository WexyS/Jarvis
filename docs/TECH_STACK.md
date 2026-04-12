# Tech Stack & Agent Matrix

## Tech Stack Recommendation

### Core Runtime
| Component | Library | Why |
|-----------|---------|-----|
| **Async Runtime** | `asyncio` (stdlib) | Native async/await, no extra deps |
| **HTTP Client** | `httpx` | Async, HTTP/2, connection pooling |
| **Config** | `pydantic-settings` | Type-safe, env override, validation |
| **Logging** | `structlog` + `logging` | Structured logs, JSON output |

### LLM Layer (RTX 4080 Optimized)
| Component | Library | Why |
|-----------|---------|-----|
| **Local Inference** | `vLLM` (via API) | 24GB VRAM → 70B models, PagedAttention |
| **Fallback** | `ollama` (Python SDK) | Easy model management |
| **Router** | Custom `LLMRouter` | Multi-provider, cost/latency aware |
| **Streaming** | `httpx` SSE | Real-time token streaming |

### Memory Engine
| Component | Library | Why |
|-----------|---------|-----|
| **Vector DB** | `chromadb` | Local, persistent, fast similarity |
| **Graph DB** | `networkx` | In-memory, knowledge graph, pathfinding |
| **Embeddings** | `sentence-transformers` | Local, `all-MiniLM-L6-v2` (fast) |
| **Cache** | `diskcache` | LRU + TTL, disk-backed, zero-config |

### RPA / Computer Use
| Component | Library | Why |
|-----------|---------|-----|
| **Screen Capture** | `mss` | Cross-platform, ~60fps, zero-copy |
| **Mouse/Keyboard** | `pyautogui` | Mature, safe defaults, cross-platform |
| **UI Automation** | `pywinauto` (Win) | Native Windows controls, reliable |
| **OCR** | `easyocr` / `paddleocr` | Local, multi-language, accurate |
| **Screen Analysis** | `opencv-python` | Template matching, object detection |

### Self-Healing Code Engine
| Component | Library | Why |
|-----------|---------|-----|
| **Code Execution** | `subprocess` + `asyncio` | Native, controllable, sandboxable |
| **Sandboxing** | `docker` SDK (optional) | Isolated execution, resource limits |
| **AST Parsing** | `ast` (stdlib) | Code analysis, safety checks |
| **Test Runner** | `pytest` | Standard, fixtures, parametrization |

### Multi-Agent System
| Component | Library | Why |
|-----------|---------|-----|
| **Orchestration** | Custom `Orchestrator` | Lightweight, no overhead, full control |
| **Task Queue** | `asyncio.Queue` | In-process, zero deps, fast |
| **Event Bus** | `aiosignal` or custom | Pub/sub, decoupled agents |
| **State Machine** | `transitions` | Agent lifecycle management |

### Voice Pipeline (keep existing)
| Component | Library | Why |
|-----------|---------|-----|
| **STT Primary** | Google Web Speech API | Free, Turkish, accurate |
| **STT Fallback** | `openai-whisper` | Local, offline, reliable |
| **VAD** | `silero-vad` | Neural, accurate, low false-positive |
| **TTS** | `edge-tts` | Free, natural voices, Turkish |

### Utilities
| Component | Library | Why |
|-----------|---------|-----|
| **Rich Output** | `rich` | Terminal formatting, progress bars |
| **Scheduling** | `apscheduler` | Cron-like, async, persistent |
| **File Watcher** | `watchdog` | Auto-index new documents |

---

## Agent & Skill Matrix

### Core Agents

#### 1. ORCHESTRATOR (Central Brain)
- **Role**: Task decomposition, agent assignment, result aggregation
- **Capabilities**: Intent classification, dependency graph building, parallel execution
- **Skills**: Planning, routing, merging, error recovery

#### 2. CODER (Software Engineer)
- **Role**: Write, debug, test, deploy code in any language
- **Capabilities**:
  - Self-healing loop: write → execute → read stack trace → fix → repeat
  - Multi-language: Python, JS/TS, C++, C#, Go, Rust, Java, etc.
  - File I/O, git operations, package management
  - Test generation and execution
- **Skills**:
  - `code_write` - Generate code from description
  - `code_execute` - Run in sandbox
  - `code_debug` - Analyze errors and fix
  - `code_review` - Quality and security check
  - `git_commit` - Version control
  - `project_setup` - Scaffold new projects

#### 3. RESEARCHER (Deep Research)
- **Role**: Multi-hop research with citations, web + local docs
- **Capabilities**:
  - Web search (DuckDuckGo, Google via RPA)
  - Page scraping and content extraction
  - PDF/academic paper analysis
  - Local document RAG
  - Citation tracking and source verification
- **Skills**:
  - `web_search` - Multi-engine search
  - `scrape_url` - Extract content
  - `read_pdf` - Parse academic papers
  - `rag_query` - Local document search
  - `citation_check` - Verify sources
  - `summarize` - Multi-document synthesis

#### 4. RPA-OPERATOR (Computer Use)
- **Role**: Control mouse, keyboard, screen when APIs unavailable
- **Capabilities**:
  - Screen capture + OCR + UI element detection
  - Mouse movement, clicks, drag-drop
  - Keyboard input, shortcuts, text entry
  - Window management (open, close, resize)
  - Application launching and control
- **Skills**:
  - `screenshot` - Capture screen region
  - `ocr_read` - Extract text from screen
  - `mouse_click` - Click at coordinates
  - `type_text` - Keyboard input
  - `launch_app` - Open application
  - `find_ui_element` - Locate button/field by OCR/template
  - `drag_drop` - Mouse drag operations

#### 5. HOME-CONTROLLER (Smart Home / IoT)
- **Role**: Manage smart home devices, MQTT, automation rules
- **Capabilities**:
  - MQTT broker communication
  - Device discovery and control
  - Automation rule creation
  - Energy monitoring
- **Skills**:
  - `mqtt_publish` - Send command to device
  - `mqtt_subscribe` - Listen for events
  - `device_discover` - Find devices on network
  - `rule_create` - Create automation
  - `energy_query` - Check consumption

#### 6. MEMORY-KEEPER (Continuous Learning)
- **Role**: Store lessons, update skills, prevent repeat failures
- **Capabilities**:
  - Failure analysis → lesson generation
  - System prompt auto-update
  - Skill library management
  - Knowledge graph construction
- **Skills**:
  - `store_lesson` - Save failure + fix
  - `update_prompt` - Modify system prompt
  - `build_knowledge` - Add to graph
  - `retrieve_context` - Get relevant past lessons

#### 7. VOICE-ASSISTANT (Conversational Interface)
- **Role**: Voice I/O, always-listening, barge-in (existing pipeline)
- **Capabilities**: Everything from current voice_pipeline.py
- **Skills**: Inherited from current implementation

### Skill Library (Baseline)

| Category | Skills |
|----------|--------|
| **System** | `get_system_info`, `file_read`, `file_write`, `list_dir`, `execute_command` |
| **Web** | `web_search`, `scrape_page`, `download_file`, `monitor_website` |
| **Code** | `code_generate`, `code_execute`, `code_debug`, `code_review`, `git_ops` |
| **RPA** | `screenshot`, `ocr`, `mouse_click`, `type_text`, `launch_app`, `find_element` |
| **Research** | `arxiv_search`, `wikipedia`, `scholar`, `citation_tracker` |
| **Home** | `mqtt_control`, `camera_view`, `thermostat`, `lighting`, `security` |
| **Productivity** | `email_check`, `calendar_query`, `task_create`, `note_take` |
| **Media** | `play_music`, `edit_image`, `generate_image`, `edit_video` |

---

## Self-Healing Loop (Clerk Agent)

```
User Request → Coder writes script → Sandbox executes
                                      │
                              ┌───────▼───────┐
                              │   Success?     │
                              └───┬───────┬───┘
                              YES │       │ NO
                                  │       │
                          Return  │  Read stack trace
                          Result  │  Analyze error
                                  │  Generate fix
                                  │  Retry (max 5)
                                  │
                                  │  After 5 fails → escalate to Orchestrator
                                  │  Store lesson in Memory
```

## Memory Architecture

```
┌──────────────────────────────────────────────────┐
│                  MEMORY ENGINE                    │
│                                                   │
│  SHORT-TERM (Working Memory)                     │
│  ┌─────────────────────────────────────────┐     │
│  │ Current conversation context            │     │
│  │ Active task state                       │     │
│  │ Recent tool call results                │     │
│  │ TTL: 24 hours                           │     │
│  └─────────────────────────────────────────┘     │
│                                                   │
│  MID-TERM (Episodic Memory)                      │
│  ┌─────────────────────────────────────────┐     │
│  │ Vector DB (ChromaDB)                    │     │
│  │ - Task outcomes                         │     │
│  │ - Code snippets + results               │     │
│  │ - Research findings                     │     │
│  │ TTL: 30 days                            │     │
│  └─────────────────────────────────────────┘     │
│                                                   │
│  LONG-TERM (Semantic Memory)                     │
│  ┌─────────────────────────────────────────┐     │
│  │ Graph DB (NetworkX)                     │     │
│  │ - User preferences                      │     │
│  │ - Learned patterns                      │     │
│  │ - Domain knowledge                      │     │
│  │ - Skill definitions                     │     │
│  │ TTL: Permanent                          │     │
│  └─────────────────────────────────────────┘     │
│                                                   │
│  SELF-LEARNING LOOP                              │
│  ┌─────────────────────────────────────────┐     │
│  │ 1. Detect failure                       │     │
│  │ 2. Analyze root cause                   │     │
│  │ 3. Generate "lesson learned"            │     │
│  │ 4. Update relevant skill/prompt         │     │
│  │ 5. Store in episodic + semantic memory  │     │
│  │ 6. Re-attempt task with new knowledge   │     │
│  └─────────────────────────────────────────┘     │
└──────────────────────────────────────────────────┘
```
