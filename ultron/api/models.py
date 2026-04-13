"""Pydantic models for API requests/responses."""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    mode: str = Field(default="chat")
    stream: bool = True

class AgentRequest(BaseModel):
    agent: str
    task: str = Field(..., min_length=1, max_length=10000)
    context: dict[str, Any] = Field(default_factory=dict)
