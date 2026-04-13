"""Base provider interface and common types."""
import time
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional

from pydantic import BaseModel


class Message(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ProviderConfig(BaseModel):
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: str
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: int = 60
    priority: int = 99


class ProviderResult(BaseModel):
    content: str
    provider: str
    model: str
    tokens_used: int = 0
    latency_ms: int = 0


class BaseProvider(ABC):
    def __init__(self, config: ProviderConfig):
        self.config = config

    def is_configured(self) -> bool:
        """API key var mı? Yoksa bu provider atlanır."""
        return bool(self.config.api_key) or self.config.name == "ollama"

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> ProviderResult: ...

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[Message],
        model: Optional[str] = None,
    ) -> AsyncIterator[str]: ...

    @abstractmethod
    async def is_available(self) -> bool: ...

    @abstractmethod
    async def list_models(self) -> list[str]: ...
