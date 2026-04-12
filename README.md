# J.A.R.V.I.S v2.0 — Personal AI Assistant

> Multi-agent, self-healing, locally-hosted AI system with Tauri/React GUI.

## Quick Start

```bash
# Terminal 1: Backend
cd C:\Users\nemes\Desktop\Jarvis
python -m uvicorn jarvis.api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: React GUI
cd jarvis-desktop && npm run dev

# Open http://localhost:5173
```

## Project Structure

```
Jarvis/
├── config/           # YAML configs
├── docs/             # Documentation
├── scripts/          # Helper scripts
├── data/             # Runtime data (memory, cache)
├── workspace/        # Coder agent sandbox
├── jarvis/           # Python backend
│   ├── api/          # FastAPI + WebSocket
│   ├── v2/           # Multi-agent system
│   └── actions/      # Local tools
├── jarvis-desktop/   # React + Tauri GUI
├── .env              # API keys
├── pyproject.toml    # Python deps
└── start-jarvis.bat  # Launcher
```

## Documentation

See [`docs/README.md`](docs/README.md) for full usage guide.
