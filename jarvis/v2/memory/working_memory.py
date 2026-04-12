"""Working Memory — Kısa süreli aktif konuşma bağlamı.

Maksimum son N mesajı deque ile tutar.
Token sınırı aşılırsa özetleme yapar.
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Tek bir mesaj."""
    role: str  # "user", "assistant", "system"
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class WorkingMemory:
    """Aktif konuşma bağlamı. Maksimum son N mesajı tutar."""

    def __init__(self, max_messages: int = 20, max_tokens: int = 4000):
        self.max_messages = max_messages
        self.max_tokens = max_tokens
        self._messages: deque[Message] = deque(maxlen=max_messages * 2)  # buffer
        self._tokenizer = None

    def add(self, role: str, content: str, metadata: dict | None = None) -> None:
        """Mesaj ekle."""
        self._messages.append(Message(role=role, content=content, metadata=metadata or {}))

    def get_messages(self) -> list[Message]:
        """Son N mesajı döndür (token limitine göre kırp)."""
        messages = list(self._messages)
        # Token limitine göre geriye doğru kırp
        while messages and self._count_tokens(messages) > self.max_tokens:
            messages.pop(0)
        return messages

    def to_messages(self) -> list[dict[str, str]]:
        """LLM'e gönderilecek formatta döndür."""
        return [{"role": m.role, "content": m.content} for m in self.get_messages()]

    def clear(self) -> None:
        self._messages.clear()

    def _count_tokens(self, messages: list[Message]) -> int:
        """Mesajların yaklaşık token sayısını hesapla."""
        if self._tokenizer is None:
            try:
                import tiktoken
                self._tokenizer = tiktoken.get_encoding("cl100k_base")
            except ImportError:
                # Fallback: 4 karakter ≈ 1 token
                self._tokenizer = None

        if self._tokenizer is None:
            total = sum(len(m.content) for m in messages)
            return total // 4

        total = 0
        for m in messages:
            total += len(self._tokenizer.encode(m.content))
        return total

    def token_count(self) -> int:
        """Mevcut token sayısı."""
        return self._count_tokens(list(self._messages))

    def summarize_if_needed(self, summarize_fn=None) -> list[dict[str, str]] | None:
        """Token sınırı aşıldığında eski mesajları özetle.

        summarize_fn: LLM ile özetleme yapan async fonksiyon.
        None ise sadece kırpma yapar.
        """
        if self.token_count() <= self.max_tokens:
            return None

        messages = list(self._messages)
        # İlk yarısını özetlenecek olarak ayır
        split = len(messages) // 2
        to_summarize = messages[:split]
        to_keep = messages[split:]

        if summarize_fn is None:
            # Sadece kırp
            self._messages = deque(to_keep, maxlen=self.max_messages * 2)
            logger.info("WorkingMemory trimmed (no summarization)")
            return self.to_messages()

        # Özetleme yapılabilir — caller'a bilgi ver
        return {
            "to_summarize": [m.content for m in to_summarize],
            "to_keep": [{"role": m.role, "content": m.content} for m in to_keep],
        }

    def apply_summary(self, summary: str) -> None:
        """Özetleme sonucunu uygula: eski mesajları sil, özet ekle."""
        messages = list(self._messages)
        split = len(messages) // 2
        self._messages = deque(messages[split:], maxlen=self.max_messages * 2)
        # Özeti system mesajı olarak ekle
        self._messages.appendleft(Message(
            role="system",
            content=f"[Previous conversation summary: {summary}]",
        ))
        logger.info("WorkingMemory summarized: %d messages → summary + %d messages",
                     len(messages), len(self._messages) - 1)

    def stats(self) -> dict:
        return {
            "message_count": len(self._messages),
            "token_count": self.token_count(),
            "max_messages": self.max_messages,
            "max_tokens": self.max_tokens,
        }
