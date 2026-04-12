"""Base provider abstract classes."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterator, Optional
from pydantic import BaseModel


class ProviderStats:
    """Provider statistics and health metrics."""
    def __init__(self):
        self.total_calls: int = 0
        self.successful_calls: int = 0
        self.failed_calls: int = 0
        self.total_latency_ms: float = 0
        self.total_cost_usd: float = 0
        self.last_active: Optional[datetime] = None
        self.last_error: str = ""
        self.consecutive_failures: int = 0

    @property
    def success_rate(self) -> float:
        total = self.successful_calls + self.failed_calls
        return self.successful_calls / total if total > 0 else 0.0

    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / self.successful_calls if self.successful_calls > 0 else 0.0

    @property
    def health_score(self) -> float:
        if self.consecutive_failures >= 5:
            return 0.0
        return max(0.0, self.success_rate * 0.7 + (0.3 if self.avg_latency_ms < 2000 else 0.0))


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
        self.stats = ProviderStats()

    @abstractmethod
    def is_configured(self) -> bool:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        pass

    def is_available_sync(self) -> bool:
        """Sync version for status checks."""
        return self.is_configured()

    def get_model_name(self) -> str:
        """Return the default model name."""
        return self.config.default_model

    @abstractmethod
    async def chat(
        self, messages: list[Message],
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False
    ) -> ProviderResult:
        pass

    @abstractmethod
    async def stream_chat(
        self, messages: list[Message],
        model: Optional[str] = None
    ) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def list_models(self) -> list[str]:
        pass
