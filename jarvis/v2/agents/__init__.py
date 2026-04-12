"""Agent package — tüm specialized agentlar."""

from .base import Agent
from .coder import CoderAgent
from .researcher import ResearcherAgent
from .rpa_operator import RPAOperatorAgent
# ── Yeni Agentlar ─────────────────────────────────────
from .email_agent import EmailAgent
from .sysmon_agent import SystemMonitorAgent
from .clipboard_agent import ClipboardAgent
from .meeting_agent import MeetingAgent
from .files_agent import FilesAgent

__all__ = [
    "Agent",
    "CoderAgent",
    "ResearcherAgent",
    "RPAOperatorAgent",
    "EmailAgent",
    "SystemMonitorAgent",
    "ClipboardAgent",
    "MeetingAgent",
    "FileOrganizerAgent",
]
