"""FastAPI endpoint tests.

These tests verify endpoint structure WITHOUT the heavy orchestrator.
A minimal FastAPI app is constructed manually for each test.
"""

from __future__ import annotations

import time
from typing import Optional

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import ASGITransport, AsyncClient

# ---------------------------------------------------------------------------
# Minimal test app (mimics ultron.api.main without the orchestrator)
# ---------------------------------------------------------------------------

_START_TIME = time.time()
_test_orchestrator: Optional[object] = None  # Simulates "no orchestrator"


class _FakeLLMRouter:
    def get_status(self) -> dict:
        return {
            "ollama": {
                "available": True,
                "model": "qwen2.5:14b",
                "stats": {
                    "avg_latency_ms": "12ms",
                    "health_score": "1.00",
                },
            }
        }


class _FakeOrchestrator:
    def __init__(self) -> None:
        self._running = True
        self.llm_router = _FakeLLMRouter()

    def get_status(self) -> dict:
        return {
            "running": True,
            "agents": {
                "coder": {
                    "status": "idle",
                    "tasks_completed": 2,
                    "tasks_failed": 0,
                }
            },
            "llm_providers": self.llm_router.get_status(),
            "memory": {"vector_entries": 5},
            "event_bus_events": 0,
        }


def _build_test_app() -> FastAPI:
    """Build a minimal FastAPI app that mirrors the real endpoint shapes."""

    app = FastAPI(title="Ultron v2.0 API (test)", version="2.1.0")

    @app.get("/")
    async def root():
        return {
            "name": "Ultron v2.0 API",
            "version": "2.1.0",
            "status": "running" if _test_orchestrator else "initializing",
            "docs": "/docs",
        }

    @app.get("/health")
    async def health(request: Request):
        uptime = time.time() - _START_TIME
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok" if _test_orchestrator else "degraded",
                "version": "2.1.0",
                "uptime_seconds": round(uptime, 1),
            },
        )

    @app.get("/docs", include_in_schema=False)
    async def docs():
        from fastapi.openapi.docs import get_swagger_ui_html
        return get_swagger_ui_html(openapi_url="/openapi.json", title="Docs")

    @app.get("/openapi.json", include_in_schema=False)
    async def openapi():
        return app.openapi()

    return app


def _build_status_router_app() -> FastAPI:
    """Build a lightweight app that mounts the real status router."""
    from ultron.api.routes.status import router as status_router

    app = FastAPI(title="Ultron Status Router (test)", version="2.1.0")
    app.include_router(status_router)
    return app


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    @pytest.mark.asyncio
    async def test_health_endpoint_structure(self) -> None:
        """Verify /health returns dict with status, version, uptime_seconds."""
        app = _build_test_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ("ok", "degraded")
        assert "version" in data
        assert data["version"] == "2.1.0"
        assert "uptime_seconds" in data
        assert isinstance(data["uptime_seconds"], (int, float))
        assert data["uptime_seconds"] >= 0


class TestRootEndpoint:
    """Tests for the / root endpoint."""

    @pytest.mark.asyncio
    async def test_root_endpoint(self) -> None:
        """Verify / returns dict with name, version."""
        app = _build_test_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Ultron v2.0 API"
        assert "version" in data
        assert data["version"] == "2.1.0"
        assert "status" in data
        assert "docs" in data
        assert data["docs"] == "/docs"


class TestDocsEndpoint:
    """Tests for the /docs endpoint."""

    @pytest.mark.asyncio
    async def test_docs_endpoint(self) -> None:
        """Verify /docs returns 200 and HTML content."""
        app = _build_test_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/docs")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_openapi_json_endpoint(self) -> None:
        """Verify /openapi.json returns valid OpenAPI spec."""
        app = _build_test_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/openapi.json")

        assert response.status_code == 200
        spec = response.json()
        assert "openapi" in spec
        assert "info" in spec
        assert "paths" in spec
        assert "/" in spec["paths"]
        assert "/health" in spec["paths"]


class TestAppCreation:
    """Tests that confirm basic app creation works."""

    @pytest.mark.asyncio
    async def test_app_has_expected_routes(self) -> None:
        """Verify the test app registers the expected routes."""
        app = _build_test_app()
        routes = [r.path for r in app.routes]
        assert "/" in routes
        assert "/health" in routes
        assert "/docs" in routes

    @pytest.mark.asyncio
    async def test_multiple_requests(self) -> None:
        """Send multiple requests and verify consistency."""
        app = _build_test_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp1 = await client.get("/")
            resp2 = await client.get("/health")

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        data1 = resp1.json()
        data2 = resp2.json()
        assert data1["version"] == data2["version"]


class TestV2StatusAndProvidersAliases:
    """Regression tests for /api/v2/status and /api/v2/providers aliases."""

    @pytest.mark.asyncio
    async def test_v2_status_alias_returns_consistent_shape_when_degraded(self, monkeypatch) -> None:
        """Both /status and /api/v2/status should exist and include uptime_seconds."""
        import ultron.api.main as api_main

        async def _fake_get_orchestrator_none():
            return None

        monkeypatch.setattr(api_main, "get_orchestrator", _fake_get_orchestrator_none)
        monkeypatch.setattr(api_main, "START_TIME", time.time() - 5)

        app = _build_status_router_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            v1 = await client.get("/status")
            v2 = await client.get("/api/v2/status")

        assert v1.status_code == 200
        assert v2.status_code == 200

        for payload in (v1.json(), v2.json()):
            assert payload["running"] is False
            assert "agents" in payload
            assert "llm_providers" in payload
            assert "memory" in payload
            assert "uptime_seconds" in payload
            assert isinstance(payload["uptime_seconds"], (int, float))

    @pytest.mark.asyncio
    async def test_v2_providers_alias_returns_provider_map_when_running(self, monkeypatch) -> None:
        """Both /providers and /api/v2/providers should return provider maps."""
        import ultron.api.main as api_main

        fake_orchestrator = _FakeOrchestrator()

        async def _fake_get_orchestrator():
            return fake_orchestrator

        monkeypatch.setattr(api_main, "get_orchestrator", _fake_get_orchestrator)

        app = _build_status_router_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            v1 = await client.get("/providers")
            v2 = await client.get("/api/v2/providers")

        assert v1.status_code == 200
        assert v2.status_code == 200

        for payload in (v1.json(), v2.json()):
            assert isinstance(payload, dict)
            assert "ollama" in payload
            assert payload["ollama"]["available"] is True

    @pytest.mark.asyncio
    async def test_v2_providers_alias_returns_empty_map_when_degraded(self, monkeypatch) -> None:
        """/api/v2/providers should return a stable dict type even when orchestrator is absent."""
        import ultron.api.main as api_main

        async def _fake_get_orchestrator_none():
            return None

        monkeypatch.setattr(api_main, "get_orchestrator", _fake_get_orchestrator_none)

        app = _build_status_router_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v2/providers")

        assert response.status_code == 200
        assert response.json() == {}
