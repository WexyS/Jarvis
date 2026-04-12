"""Jarvis v2.0 — FastAPI Backend Bridge."""
from __future__ import annotations
import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

START_TIME = time.time()
_orchestrator: Optional["Orchestrator"] = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("jarvis.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _orchestrator
    logger.info("=" * 60)
    logger.info("JARVIS v2.0 API — Starting...")
    logger.info("=" * 60)
    load_dotenv()
    try:
        from jarvis.v2.core.llm_router import LLMRouter
        from jarvis.v2.memory.engine import MemoryEngine
        from jarvis.v2.core.orchestrator import Orchestrator

        llm = LLMRouter(ollama_model="qwen2.5:14b")
        llm.enable_all_providers(dict(os.environ))
        memory = MemoryEngine(persist_dir="./data/memory_v2")
        _orchestrator = Orchestrator(llm_router=llm, memory=memory, work_dir="./workspace")
        await _orchestrator.start()  # Sets _running=True, starts all agents

        logger.info("LLM Providers: %s", llm.get_healthy_providers())
        logger.info("Agents started: %s", list(_orchestrator.agents.keys()))
    except Exception as e:
        logger.error("Failed to initialize: %s", e, exc_info=True)
        _orchestrator = None
    yield
    logger.info("Shutting down...")
    if _orchestrator:
        await _orchestrator.stop()

app = FastAPI(title="Jarvis v2.0 API", version="2.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

from jarvis.api.routes.chat import router as chat_router
from jarvis.api.routes.agents import router as agents_router
from jarvis.api.routes.status import router as status_router

app.include_router(chat_router)
app.include_router(agents_router)
app.include_router(status_router)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return JSONResponse(status_code=500, content={"error": str(exc)})

@app.get("/")
async def root():
    return {"name": "Jarvis v2.0 API", "version": "2.1.0", "status": "running" if _orchestrator else "initializing", "docs": "/docs"}

async def get_orchestrator():
    return _orchestrator

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("jarvis.api.main:app", host="0.0.0.0", port=8000, reload=True,
                reload_excludes=["workspace/*", "data/*", ".venv/*"])
