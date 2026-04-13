"""Pytest fixtures for Ultron v2.0 tests."""

from __future__ import annotations

from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Mock LLMRouter
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_llm_router() -> MagicMock:
    """Mock LLMRouter that returns canned responses without hitting any API."""
    router = MagicMock()
    router.chat = AsyncMock(return_value=MagicMock(
        content="Canned LLM response",
        provider="mock",
        model="mock-model",
        tokens_used=10,
        cost_usd=0.0,
        latency_ms=1.0,
        finish_reason="stop",
    ))
    router.stream_chat = AsyncMock()
    router.providers = {"ollama": MagicMock()}
    router.priority_order = ["ollama"]
    router._active_provider = "ollama"
    router.get_healthy_providers = MagicMock(return_value=["ollama"])
    router.get_status = MagicMock(return_value={})
    router.enable_all_providers = MagicMock()
    return router


# ---------------------------------------------------------------------------
# Mock EventBus
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_event_bus() -> MagicMock:
    """Mock EventBus with async publish."""
    bus = MagicMock()
    bus.publish = AsyncMock()
    bus.publish_simple = AsyncMock()
    bus.subscribe = MagicMock()
    bus.subscribe_all = MagicMock()
    bus.get_recent_events = MagicMock(return_value=[])
    bus.clear = MagicMock()
    bus._handlers: dict[str, list] = {}
    return bus


# ---------------------------------------------------------------------------
# Mock Blackboard
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_blackboard() -> MagicMock:
    """Mock Blackboard with async read/write."""
    board = MagicMock()
    board.write = AsyncMock()
    board.read = AsyncMock(return_value=None)
    board.delete = AsyncMock(return_value=False)
    board.keys = AsyncMock(return_value=[])
    board.clear = AsyncMock(return_value=0)
    board.get_all = AsyncMock(return_value={})
    return board


# ---------------------------------------------------------------------------
# Temporary path for test databases
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_path_for_db(tmp_path: Path) -> Path:
    """Provide a temporary directory for test database files."""
    db_dir = tmp_path / "ultron_test_db"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir
