"""LLM sağlayıcıları — SADECE Ollama (yerel). Cloud API gerektirmez."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional

from jarvis.config import JarvisConfig, ModelConfig

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """LLM sağlayıcıları için temel sınıf."""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        ...

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        ...

    @abstractmethod
    def is_available(self) -> bool:
        ...


class OllamaProvider(LLMProvider):
    """Ollama yerel çıkarım sağlayıcısı. Tamamen yerel, internet gerektirmez."""

    def __init__(self, config: ModelConfig):
        self.config = config
        self._available = None

    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            import httpx
            base = self.config.ollama_base_url.rstrip("/")
            resp = httpx.get(f"{base}/api/tags", timeout=5)
            self._available = resp.status_code == 200
            return self._available
        except Exception as e:
            logger.debug("Ollama kullanılamıyor: %s", e)
            self._available = False
            return False

    async def chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        import ollama
        response = ollama.chat(
            model=self.config.ollama_model,
            messages=messages,
            options={
                "temperature": temperature or self.config.temperature,
                "num_predict": max_tokens or self.config.max_tokens,
            },
        )
        return response["message"]["content"]

    async def stream_chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        import ollama
        response = ollama.chat(
            model=self.config.ollama_model,
            messages=messages,
            stream=True,
            options={
                "temperature": temperature or self.config.temperature,
                "num_predict": max_tokens or self.config.max_tokens,
            },
        )
        for chunk in response:
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]


class LLMRouter:
    """Ollama merkezli LLM yönlendirici. Tek sağlayıcı, basit arayüz."""

    def __init__(self, config: JarvisConfig):
        self.config = config
        self.ollama = OllamaProvider(config.model)

        if not self.ollama.is_available():
            raise RuntimeError(
                "Ollama bulunamadı. Lütfen Ollama'yı kurun ve bir model indirin:\n"
                "  1. https://ollama.ai adresinden Ollama'yı indirin\n"
                "  2. ollama pull qwen2.5:7b komutunu çalıştırın\n"
                "  3. Jarvis'i tekrar başlatın"
            )

        logger.info("Ollama sağlayıcısı başlatıldı (%s)", config.model.ollama_model)

    @property
    def active_provider(self) -> LLMProvider:
        return self.ollama

    async def chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[list[dict]] = None,
    ) -> str:
        return await self.ollama.chat(
            messages, temperature=temperature, max_tokens=max_tokens,
        )

    async def stream_chat(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        async for chunk in self.ollama.stream_chat(
            messages, temperature=temperature, max_tokens=max_tokens,
        ):
            yield chunk

    def get_status(self) -> dict:
        return {
            "active": "ollama",
            "ollama_available": self.ollama.is_available(),
            "model": self.config.model.ollama_model,
        }
