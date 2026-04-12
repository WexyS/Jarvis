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
# Minimal test app (mimics jarvis.api.main without the orchestrator)
# ---------------------------------------------------------------------------

_START_TIME = time.time()
_test_orchestrator: Optional[object] = None  # Simulates "no orchestrator"


def _build_test_app() -> FastAPI:
    """Build a minimal FastAPI app that mirrors the real endpoint shapes."""

    app = FastAPI(title="Jarvis v2.0 API (test)", version="2.1.0")

    @app.get("/")
    async def root():
        return {
            "name": "Jarvis v2.0 API",
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
        assert data["name"] == "Jarvis v2.0 API"
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
