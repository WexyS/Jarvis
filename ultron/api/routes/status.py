"""System health and provider status."""
from __future__ import annotations
import time
from fastapi import APIRouter

router = APIRouter(tags=["status"])

@router.get("/status")
@router.get("/api/v2/status")
async def system_status():
    from ultron.api.main import get_orchestrator, START_TIME
    uptime_seconds = time.time() - START_TIME
    orch = await get_orchestrator()
    if not orch:
        return {
            "running": False,
            "agents": {},
            "llm_providers": {},
            "memory": {},
            "uptime_seconds": uptime_seconds,
        }
    status = orch.get_status()
    status["uptime_seconds"] = uptime_seconds
    return status

@router.get("/providers")
@router.get("/api/v2/providers")
async def provider_status():
    from ultron.api.main import get_orchestrator
    orch = await get_orchestrator()
    if not orch:
        return {}
    return orch.llm_router.get_status()

@router.get("/health")
@router.get("/api/v2/health")
async def health_check():
    from ultron.api.main import get_orchestrator
    orch = await get_orchestrator()
    is_running = bool(orch and getattr(orch, "_running", False))
    return {"status": "healthy" if is_running else "degraded", "orchestrator": is_running}
