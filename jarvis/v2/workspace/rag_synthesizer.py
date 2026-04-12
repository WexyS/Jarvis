"""RAG Synthesizer Agent — combines existing templates to create new apps."""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class RAGSynthesizerAgent:
    """Synthesizes new applications by combining existing cloned templates."""

    def __init__(self) -> None:
        self.workspace_dir = Path(__file__).parent.parent.parent.parent / "workspace"
        self.cloned_dir = self.workspace_dir / "cloned_templates"
        self.synthesized_dir = self.workspace_dir / "synthesized_apps"
        self.synthesized_dir.mkdir(parents=True, exist_ok=True)

    async def synthesize(
        self,
        user_command: str,
        target_project: str,
        source_projects: list[str] = [],
    ) -> dict:
        """Synthesize a new app from existing templates."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_dir = self.synthesized_dir / f"{target_project}_{timestamp}"
        project_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Synthesizing: %s from %d sources", target_project, len(source_projects))

        # Find relevant templates
        relevant_templates = await self._find_relevant_templates(user_command, source_projects)

        # Analyze and extract components
        components_map = {}
        for template in relevant_templates:
            components = await self._analyze_template(template)
            components_map[template["name"]] = components

        # Generate synthesis plan
        synthesis_plan = await self._generate_synthesis_plan(
            user_command, target_project, components_map
        )

        # Execute synthesis
        files_created = await self._execute_synthesis(synthesis_plan, project_dir)

        # Create metadata
        metadata = {
            "id": f"synth_{timestamp}",
            "type": "synthesized",
            "name": target_project,
            "description": user_command,
            "components": synthesis_plan.get("components", []),
            "tech_stack": synthesis_plan.get("tech_stack", "html-css-js"),
            "path": str(project_dir),
            "source_templates": [t["name"] for t in relevant_templates],
            "synthesis_plan": synthesis_plan,
            "files_created": files_created,
            "metadata": {
                "user_command": user_command,
                "templates_used": len(relevant_templates),
            },
            "created_at": datetime.now().isoformat(),
            "embeddings_stored": False,
        }

        # Save metadata
        metadata_path = project_dir / "metadata.json"
        metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        logger.info("✅ Synthesized %d files for: %s", len(files_created), target_project)
        return metadata

    async def _find_relevant_templates(
        self,
        query: str,
        source_projects: list[str],
    ) -> list[dict]:
        """Find relevant templates from workspace."""
        templates = []

        # Search cloned templates
        if self.cloned_dir.exists():
            for template_dir in self.cloned_dir.iterdir():
                if not template_dir.is_dir():
                    continue

                metadata_file = template_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
                        # Simple keyword matching
                        score = self._calculate_relevance(query, metadata)
                        metadata["relevance_score"] = score
                        templates.append(metadata)
                    except Exception as e:
                        logger.warning("Failed to load metadata: %s", e)

        # Sort by relevance
        templates.sort(key=lambda t: t.get("relevance_score", 0), reverse=True)

        # Return top 5
        return templates[:5]

    async def _analyze_template(self, template_metadata: dict) -> dict:
        """Analyze a template and extract reusable components."""
        template_path = Path(template_metadata["path"])
        components = {}

        # Analyze HTML files
        for html_file in template_path.glob("*.html"):
            html_content = html_file.read_text(encoding="utf-8")
            components["html"] = self._extract_html_components(html_content)

        # Analyze CSS files
        for css_file in template_path.glob("**/*.css"):
            css_content = css_file.read_text(encoding="utf-8")
            components["css"] = self._extract_css_components(css_content)

        # Analyze JS files
        for js_file in template_path.glob("**/*.js"):
            js_content = js_file.read_text(encoding="utf-8")
            components["js"] = self._extract_js_modules(js_content)

        return components

    async def _generate_synthesis_plan(
        self,
        user_command: str,
        target_project: str,
        components_map: dict,
    ) -> dict:
        """Generate a plan for synthesizing the new app."""
        import httpx

        prompt = f"""You are an expert software architect. Create a synthesis plan for combining existing templates into a new app.

USER COMMAND: {user_command}
TARGET PROJECT: {target_project}

AVAILABLE COMPONENTS:
{json.dumps(components_map, indent=2)}

Create a JSON plan with:
- architecture: brief description
- components: list of UI components to include
- tech_stack: technologies to use
- file_structure: dict of file_path -> source_template
- styling_notes: how to unify styles
- integration_notes: how to integrate components"""

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
            return {
                "architecture": "Simple web app",
                "components": ["navbar", "hero", "footer"],
                "tech_stack": "html-css-js",
                "file_structure": {},
            }

    async def _execute_synthesis(
        self,
        plan: dict,
        output_dir: Path,
    ) -> list[str]:
        """Execute the synthesis plan and create files."""
        files_created = []

        # Copy and merge files from source templates
        for file_path, source_template in plan.get("file_structure", {}).items():
            # Find source file
            source_file = self._find_source_file(source_template, file_path)
            if source_file and source_file.exists():
                dest_file = output_dir / file_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest_file)
                files_created.append(file_path)

        # Create main index.html if not exists
        if not (output_dir / "index.html").exists():
            index_content = await self._generate_index_html(plan)
            (output_dir / "index.html").write_text(index_content, encoding="utf-8")
            files_created.append("index.html")

        return files_created

    def _calculate_relevance(self, query: str, metadata: dict) -> float:
        """Calculate relevance score for a template."""
        score = 0.0
        query_lower = query.lower()

        # Match against name
        if metadata.get("name", "").lower() in query_lower:
            score += 3.0

        # Match against description
        if metadata.get("description", "").lower() in query_lower:
            score += 2.0

        # Match against components
        for component in metadata.get("components", []):
            if component.lower() in query_lower:
                score += 1.5

        return score

    def _extract_html_components(self, html: str) -> dict:
        """Extract components from HTML."""
        import re
        components = {}

        # Extract sections with IDs or classes
        sections = re.findall(r'<(section|div|header|footer|nav)[^>]*class="([^"]*)"[^>]*>', html)
        for tag, classes in sections:
            components[f"{tag}.{classes}"] = "found"

        return components

    def _extract_css_components(self, css: str) -> dict:
        """Extract CSS components."""
        import re
        components = {}

        # Extract class selectors
        classes = re.findall(r'\.([a-zA-Z0-9_-]+)\s*{', css)
        for cls in classes:
            components[cls] = "found"

        return components

    def _extract_js_modules(self, js: str) -> dict:
        """Extract JS modules."""
        import re
        components = {}

        # Extract function names
        funcs = re.findall(r'function\s+(\w+)', js)
        for func in funcs:
            components[func] = "function"

        return components

    def _find_source_file(self, template_name: str, file_path: str) -> Optional[Path]:
        """Find a source file from a template."""
        # Search in cloned templates
        if self.cloned_dir.exists():
            for template_dir in self.cloned_dir.iterdir():
                if template_name in template_dir.name:
                    return template_dir / file_path
        return None

    async def _generate_index_html(self, plan: dict) -> str:
        """Generate a main index.html file."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{plan.get('architecture', 'Synthesized App')}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <!-- Synthesized from multiple templates -->
    <main id="app"></main>
    <script src="js/app.js"></script>
</body>
</html>
"""
