"""System health and provider status."""
from __future__ import annotations
import time
from fastapi import APIRouter

router = APIRouter(tags=["status"])

@router.get("/status")
async def system_status():
    from ultron.api.main import get_orchestrator, START_TIME
    orch = await get_orchestrator()
    if not orch:
        return {"running": False, "agents": {}, "llm_providers": {}, "memory": {}}
    status = orch.get_status()
    status["uptime_seconds"] = time.time() - START_TIME
    return status

@router.get("/providers")
async def provider_status():
    from ultron.api.main import get_orchestrator
    orch = await get_orchestrator()
    if not orch:
        return {"providers": []}
    return orch.llm_router.get_status()

@router.get("/health")
async def health_check():
    from ultron.api.main import get_orchestrator
    orch = await get_orchestrator()
    return {"status": "healthy" if orch and orch._running else "degraded", "orchestrator": bool(orch and orch._running)}
