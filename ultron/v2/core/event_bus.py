"""Async event bus for inter-agent communication."""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Coroutine, Optional

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """An event on the bus."""
    name: str
    source: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


Handler = Callable[[Event], Coroutine[None, None, None]]


class EventBus:
    """Pub/sub event bus for agent communication.

    Agents publish events (task results, status changes, requests).
    Other agents subscribe to events they care about.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._global_handlers: list[Handler] = []
        self._event_log: list[Event] = []
        self._max_log = 1000  # Keep last N events

    def subscribe(self, event_name: str, handler: Handler) -> None:
        """Subscribe to a specific event type."""
        self._handlers[event_name].append(handler)
        logger.debug("Subscribed to '%s': %s", event_name, handler.__name__)

    def subscribe_all(self, handler: Handler) -> None:
        """Subscribe to ALL events."""
        self._global_handlers.append(handler)

    async def publish(self, event: Event) -> None:
        """Publish an event to all subscribers."""
        # Append to log
        self._event_log.append(event)
        if len(self._event_log) > self._max_log:
            self._event_log = self._event_log[-self._max_log:]

        # Fire specific handlers
        handlers = self._handlers.get(event.name, [])
        tasks = []
        for handler in handlers:
            tasks.append(self._safe_call(handler, event))

        # Fire global handlers
        for handler in self._global_handlers:
            tasks.append(self._safe_call(handler, event))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(
                        "Event handler error [%s]: %s",
                        event.name,
                        result,
                    )

        logger.debug("Published event '%s' from '%s'", event.name, event.source)

    async def publish_simple(self, name: str, source: str, data: Optional[dict] = None) -> None:
        """Convenience: publish without creating Event object."""
        await self.publish(Event(name=name, source=source, data=data or {}))

    @staticmethod
    async def _safe_call(handler: Handler, event: Event) -> None:
        try:
            await handler(event)
        except Exception as e:
            logger.error("Handler %s failed on event %s: %s", handler.__name__, event.name, e)
            raise

    def get_recent_events(self, count: int = 10, filter_name: Optional[str] = None) -> list[Event]:
        """Get recent events, optionally filtered by name."""
        events = self._event_log[-count:]
        if filter_name:
            events = [e for e in events if e.name == filter_name]
        return events

    def clear(self) -> None:
        """Clear all handlers and event log."""
        self._handlers.clear()
        self._global_handlers.clear()
        self._event_log.clear()
