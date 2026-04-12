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
        for skill_dir in sorted(search_dir.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue
            # Look for SKILL.md or skill.json
            skill_md = skill_dir / "SKILL.md"
            skill_json = skill_dir / "skill.json"

            if skill_md.exists():
                try:
                    content = skill_md.read_text(encoding="utf-8", errors="replace")
                    desc = content[:200].strip()
                    skills.append({
                        "name": skill_dir.name,
                        "description": f"Skill: {skill_dir.name}. {desc}",
                        "path": str(skill_dir),
                        "source": str(search_dir),
                    })
                except Exception as e:
                    logger.debug("Failed to read skill %s: %s", skill_dir.name, e)
            elif skill_json.exists():
                try:
                    data = json.loads(skill_json.read_text(encoding="utf-8"))
                    skills.append({
                        "name": skill_dir.name,
                        "description": data.get("description", f"Skill: {skill_dir.name}"),
                        "path": str(skill_dir),
                        "source": str(search_dir),
                    })
                except Exception as e:
                    logger.debug("Failed to read skill.json %s: %s", skill_dir.name, e)

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
        for agent_dir in sorted(search_dir.iterdir()):
            if not agent_dir.is_dir() or agent_dir.name.startswith("."):
                continue
            # Look for AGENT.md, agent.json, config.json, or README.md
            for config_name in ["AGENT.md", "agent.json", "config.json", "README.md"]:
                config_file = agent_dir / config_name
                if config_file.exists():
                    try:
                        content = config_file.read_text(encoding="utf-8", errors="replace")
                        desc = content[:200].strip()
                        agents.append({
                            "name": agent_dir.name,
                            "description": f"Agent: {agent_dir.name}. {desc}",
                            "path": str(agent_dir),
                            "source": str(search_dir),
                        })
                    except Exception as e:
                        logger.debug("Failed to read agent %s: %s", agent_dir.name, e)
                    break

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
