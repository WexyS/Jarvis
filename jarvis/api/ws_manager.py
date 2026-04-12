"""WebSocket connection manager."""
from __future__ import annotations
import asyncio
import logging
from typing import Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WSManager:
    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()

    async def connect(self, connection_id: str, ws: WebSocket):
        async with self._lock:
            self._connections[connection_id] = ws

    async def disconnect(self, connection_id: str):
        async with self._lock:
            self._connections.pop(connection_id, None)

    async def send_json(self, connection_id: str, data: dict):
        ws = self._connections.get(connection_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.warning("WS send failed for %s: %s", connection_id, e)
                await self.disconnect(connection_id)

    @property
    def active_connections(self) -> int:
        return len(self._connections)

ws_manager = WSManager()
