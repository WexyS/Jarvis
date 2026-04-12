"""Skill & Agent Manager — Discovery, validation, and registration."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def discover_all_skills() -> list[dict]:
    """Discover all skills from all known directories."""
    skills = []
    search_dirs = [
        Path.home() / ".qwen" / "skills",
        Path(__file__).parent.parent.parent / "skills",
        Path(__file__).parent.parent / "skills",
    ]

    for search_dir in search_dirs:
        if not search_dir.is_dir():
            continue
        for item in sorted(search_dir.iterdir()):
            # Check for SKILL.md in directories
            if item.is_dir() and not item.name.startswith("."):
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    try:
                        content = skill_md.read_text(encoding="utf-8", errors="replace")
                        desc = content[:200].strip()
                        skills.append({
                            "name": item.name,
                            "description": f"Skill: {item.name}. {desc}",
                            "path": str(item),
                            "source": str(search_dir),
                        })
                    except Exception as e:
                        logger.debug("Failed to read skill %s: %s", item.name, e)
            # Check for .md files directly
            elif item.is_file() and item.suffix == ".md" and not item.name.startswith("."):
                try:
                    content = item.read_text(encoding="utf-8", errors="replace")
                    desc = content[:200].strip()
                    skills.append({
                        "name": item.stem,
                        "description": f"Skill: {item.stem}. {desc}",
                        "path": str(item),
                        "source": str(search_dir),
                    })
                except Exception as e:
                    logger.debug("Failed to read skill file %s: %s", item.name, e)

    return skills


def discover_all_agents() -> list[dict]:
    """Discover all agents from all known directories."""
    agents = []
    search_dirs = [
        Path.home() / ".qwen" / "agents",
        Path(__file__).parent.parent.parent / "agents",
        Path(__file__).parent.parent / "agents",
    ]

    for search_dir in search_dirs:
        if not search_dir.is_dir():
            continue
        for item in sorted(search_dir.iterdir()):
            # Check for AGENT.md, agent.json, config.json, README.md in directories
            if item.is_dir() and not item.name.startswith("."):
                for config_name in ["AGENT.md", "agent.json", "config.json", "README.md"]:
                    config_file = item / config_name
                    if config_file.exists():
                        try:
                            content = config_file.read_text(encoding="utf-8", errors="replace")
                            desc = content[:200].strip()
                            agents.append({
                                "name": item.name,
                                "description": f"Agent: {item.name}. {desc}",
                                "path": str(item),
                                "source": str(search_dir),
                            })
                        except Exception as e:
                            logger.debug("Failed to read agent %s: %s", item.name, e)
                        break
            # Check for .md files directly (e.g., accessibility-tester.md)
            elif item.is_file() and item.suffix == ".md" and not item.name.startswith("."):
                try:
                    content = item.read_text(encoding="utf-8", errors="replace")
                    desc = content[:200].strip()
                    agents.append({
                        "name": item.stem,
                        "description": f"Agent: {item.stem}. {desc}",
                        "path": str(item),
                        "source": str(search_dir),
                    })
                except Exception as e:
                    logger.debug("Failed to read agent file %s: %s", item.name, e)

    return agents


def get_skill_summary(skills: list[dict]) -> str:
    """Generate a readable summary of all discovered skills."""
    if not skills:
        return "No skills discovered."

    lines = [f"📚 Discovered {len(skills)} skills:"]
    for i, skill in enumerate(skills[:20], 1):
        name = skill["name"]
        source = Path(skill["source"]).name
        lines.append(f"  {i}. {name} (from {source})")

    if len(skills) > 20:
        lines.append(f"  ... and {len(skills) - 20} more")

    return "\n".join(lines)


def get_agent_summary(agents: list[dict]) -> str:
    """Generate a readable summary of all discovered agents."""
    if not agents:
        return "No agents discovered."

    lines = [f"🤖 Discovered {len(agents)} agents:"]
    for i, agent in enumerate(agents[:20], 1):
        name = agent["name"]
        source = Path(agent["source"]).name
        lines.append(f"  {i}. {name} (from {source})")

    if len(agents) > 20:
        lines.append(f"  ... and {len(agents) - 20} more")

    return "\n".join(lines)
