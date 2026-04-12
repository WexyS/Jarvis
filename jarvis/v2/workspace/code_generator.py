"""Code Generator Agent — generates complete apps from ideas using LLM."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from jarvis.v2.core.llm_router import LLMRouter

logger = logging.getLogger(__name__)


class CodeGeneratorAgent:
    """Generates complete applications from natural language ideas."""

    def __init__(self) -> None:
        self.workspace_dir = Path(__file__).parent.parent.parent.parent / "workspace" / "generated_apps"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.llm_router = None  # Will use HTTP directly

    async def generate(
        self,
        idea: str,
        tech_stack: str = "html-css-js",
        name: Optional[str] = None,
    ) -> dict:
        """Generate a complete app from an idea."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        app_name = name or self._sanitize_name(idea)
        project_dir = self.workspace_dir / f"{app_name}_{timestamp}"
        project_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Generating app: %s", app_name)

        # Generate app structure
        structure = await self._generate_structure(idea, tech_stack)

        # Generate files
        files_generated = []
        for file_path in structure["files"]:
            content = await self._generate_file(idea, file_path, tech_stack)
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            files_generated.append(file_path)

        # Create metadata
        metadata = {
            "id": f"gen_{timestamp}",
            "type": "generated",
            "name": app_name,
            "description": idea,
            "components": structure.get("components", []),
            "tech_stack": tech_stack,
            "path": str(project_dir),
            "files": files_generated,
            "metadata": {
                "original_idea": idea,
                "generation_timestamp": datetime.now().isoformat(),
            },
            "created_at": datetime.now().isoformat(),
            "embeddings_stored": False,
        }

        # Save metadata
        metadata_path = project_dir / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

        # Save generation log
        log_path = project_dir / "generation_log.json"
        log_path.write_text(
            json.dumps({
                "idea": idea,
                "tech_stack": tech_stack,
                "structure": structure,
                "files_generated": len(files_generated),
            }, indent=2),
            encoding="utf-8",
        )

        logger.info("✅ Generated %d files for: %s", len(files_generated), app_name)
        return metadata

    async def _generate_structure(self, idea: str, tech_stack: str) -> dict:
        """Generate app structure using LLM."""
        prompt = f"""You are an expert full-stack developer. Given this app idea, create a complete file structure.

IDEA: {idea}
TECH STACK: {tech_stack}

Return JSON with:
- files: list of file paths (e.g., ["index.html", "css/style.css", "js/app.js"])
- components: list of UI components (e.g., ["navbar", "hero", "features", "footer"])
- description: brief architecture description

Make it production-ready with proper organization."""

        import httpx
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:14b",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                }
            )
            resp.raise_for_status()
            result = resp.json()

        try:
            return json.loads(result["response"])
        except:
            # Fallback structure
            return {
                "files": ["index.html", "css/style.css", "js/app.js"],
                "components": ["navbar", "hero", "footer"],
                "description": "Simple web app",
            }

    async def _generate_file(
        self,
        idea: str,
        file_path: str,
        tech_stack: str,
    ) -> str:
        """Generate content for a single file."""
        ext = Path(file_path).suffix.lower()

        prompts = {
            ".html": f"""Create a complete, production-ready HTML file for: {idea}

Requirements:
- Modern, professional design
- Responsive (mobile-first)
- Clean, semantic HTML5
- Include meta tags for SEO
- Use inline CSS for simplicity
- Professional color scheme

Return ONLY the complete HTML code, no explanations.""",

            ".css": f"""Create professional CSS for: {idea}

Requirements:
- Modern design with CSS variables
- Responsive grid/flexbox layouts
- Smooth animations and transitions
- Professional color palette
- Clean typography

Return ONLY the CSS code.""",

            ".js": f"""Create JavaScript for: {idea}

Requirements:
- Clean, modular code
- Event listeners for interactivity
- Smooth animations
- Form validation if needed
- Local storage for persistence

Return ONLY the JS code.""",

            ".py": f"""Create Python code for: {idea}

Requirements:
- FastAPI backend
- Proper error handling
- RESTful API design
- Database models if needed
- Type hints

Return ONLY the Python code.""",
        }

        prompt = prompts.get(ext, f"Create code for {file_path} for app idea: {idea}")

        import httpx
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5-coder:14b",
                    "prompt": prompt,
                    "stream": False,
                }
            )
            resp.raise_for_status()
            result = resp.json()

        return result.get("response", f"// TODO: Implement {file_path}")

    @staticmethod
    def _sanitize_name(text: str) -> str:
        """Sanitize text to valid filename."""
        import re
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', text[:30])
        return name or "app"
