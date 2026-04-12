"""Workspace Manager — manages website cloning, app generation, and RAG synthesis."""

from __future__ import annotations

import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import aiosqlite
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class WorkspaceItem(BaseModel):
    """Represents a workspace item (cloned site or generated app)."""
    id: str
    type: str  # "clone" or "generated" or "synthesized"
    name: str
    url: Optional[str] = None
    description: str = ""
    components: list[str] = []
    tech_stack: str = "html-css-js"
    path: str
    metadata: dict = {}
    created_at: str = ""
    embeddings_stored: bool = False


class CloneRequest(BaseModel):
    url: str
    extract_components: bool = True
    name: Optional[str] = None


class GenerateRequest(BaseModel):
    idea: str
    tech_stack: str = "html-css-js"
    name: Optional[str] = None


class SynthesizeRequest(BaseModel):
    user_command: str
    target_project: str
    source_projects: list[str] = []


class WorkspaceManager:
    """Manages workspace operations: cloning, generating, and synthesizing apps."""

    def __init__(self) -> None:
        self.workspace_dir = Path(__file__).parent.parent.parent / "workspace"
        self.cloned_dir = self.workspace_dir / "cloned_templates"
        self.generated_dir = self.workspace_dir / "generated_apps"
        self.synthesized_dir = self.workspace_dir / "synthesized_apps"
        self.db_path = self.workspace_dir / "workspace_index.db"

        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.cloned_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self.synthesized_dir.mkdir(parents=True, exist_ok=True)

        self._db: Optional[aiosqlite.Connection] = None

    async def init_db(self) -> None:
        """Initialize SQLite manifest database."""
        self._db = await aiosqlite.connect(str(self.db_path))
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS workspace_items (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                url TEXT,
                description TEXT,
                components TEXT,
                tech_stack TEXT,
                path TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT,
                embeddings_stored BOOLEAN DEFAULT 0
            )
        """)
        await self._db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS workspace_fts 
            USING fts5(name, description, components, content=workspace_items)
        """)
        await self._db.commit()
        logger.info("Workspace DB initialized")

    async def clone_site(self, req: CloneRequest) -> WorkspaceItem:
        """Clone a website using Playwright."""
        from jarvis.v2.workspace.clone_agent import WebsiteCloneAgent

        agent = WebsiteCloneAgent()
        item = await agent.clone(req.url, req.extract_components, req.name)

        # Store in DB
        await self._db.execute(
            "INSERT INTO workspace_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                item.id, item.type, item.name, item.url, item.description,
                str(item.components), item.tech_stack, item.path,
                str(item.metadata), item.created_at, item.embeddings_stored
            )
        )
        await self._db.commit()

        logger.info("Cloned: %s -> %s", req.url, item.path)
        return item

    async def generate_app(self, req: GenerateRequest) -> WorkspaceItem:
        """Generate an app from an idea using LLM."""
        from jarvis.v2.workspace.code_generator import CodeGeneratorAgent

        agent = CodeGeneratorAgent()
        item = await agent.generate(req.idea, req.tech_stack, req.name)

        await self._db.execute(
            "INSERT INTO workspace_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                item.id, item.type, item.name, None, item.description,
                str(item.components), item.tech_stack, item.path,
                str(item.metadata), item.created_at, item.embeddings_stored
            )
        )
        await self._db.commit()

        logger.info("Generated: %s", item.name)
        return item

    async def synthesize(self, req: SynthesizeRequest) -> WorkspaceItem:
        """Synthesize a new app from existing templates using RAG."""
        from jarvis.v2.workspace.rag_synthesizer import RAGSynthesizerAgent

        agent = RAGSynthesizerAgent()
        item = await agent.synthesize(req.user_command, req.target_project, req.source_projects)

        await self._db.execute(
            "INSERT INTO workspace_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                item.id, item.type, item.name, None, item.description,
                str(item.components), item.tech_stack, item.path,
                str(item.metadata), item.created_at, item.embeddings_stored
            )
        )
        await self._db.commit()

        logger.info("Synthesized: %s", item.name)
        return item

    async def list_workspace(self) -> list[WorkspaceItem]:
        """List all workspace items."""
        cursor = await self._db.execute("SELECT * FROM workspace_items ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [self._row_to_item(row) for row in rows]

    async def search_templates(self, query: str, top_k: int = 5) -> list[dict]:
        """Search workspace items using FTS."""
        cursor = await self._db.execute("""
            SELECT workspace_items.*, rank 
            FROM workspace_fts 
            JOIN workspace_items ON workspace_fts.rowid = workspace_items.rowid 
            WHERE workspace_fts MATCH ? 
            LIMIT ?
        """, (query, top_k))
        rows = await cursor.fetchall()
        return [{"id": r[0], "name": r[2], "type": r[1], "description": r[4]} for r in rows]

    async def store_embeddings(self, item_id: str) -> None:
        """Store ChromaDB embeddings for an item."""
        # TODO: Integrate with ChromaDB for semantic search
        await self._db.execute(
            "UPDATE workspace_items SET embeddings_stored = 1 WHERE id = ?",
            (item_id,)
        )
        await self._db.commit()

    def _row_to_item(self, row: tuple) -> WorkspaceItem:
        """Convert DB row to WorkspaceItem."""
        import ast
        return WorkspaceItem(
            id=row[0], type=row[1], name=row[2], url=row[3],
            description=row[4],
            components=ast.literal_eval(row[5]) if row[5] else [],
            tech_stack=row[6], path=row[7],
            metadata=ast.literal_eval(row[8]) if row[8] else {},
            created_at=row[9], embeddings_stored=bool(row[10])
        )

    async def close(self) -> None:
        """Close DB connection."""
        if self._db:
            await self._db.close()
