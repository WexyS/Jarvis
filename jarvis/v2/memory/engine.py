"""Memory Engine — Vector DB + Graph DB + Self-Learning Loop.

Aggressive continuous learning, failure analysis, and automatic prompt/skill updates.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    type: str  # "episodic", "semantic", "lesson", "skill_update"
    content: str
    embedding: Optional[list[float]] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0


class MemoryEngine:
    """Unified memory engine combining Vector DB, Graph DB, and self-learning.

    Three layers:
    1. Vector DB (ChromaDB): Semantic similarity search for tasks/outcomes
    2. Graph DB (NetworkX): Knowledge graph of concepts and relationships
    3. Lesson Store: Failure → lesson → prompt/skill updates
    """

    def __init__(
        self,
        persist_dir: str = "./data/memory_v2",
        embedding_model: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self._chroma_client = None
        self._chroma_collection = None
        self._embedding_model = embedding_model
        self._sentence_transformer = None

        self._graph = None  # NetworkX graph
        self._lessons_file = self.persist_dir / "lessons.json"
        self._lessons: list[dict] = []

        self._init_chroma()
        self._init_graph()
        self._load_lessons()

    # ── ChromaDB (Vector Memory) ─────────────────────────────────────────

    def _init_chroma(self) -> None:
        import chromadb

        client = chromadb.PersistentClient(path=str(self.persist_dir / "chroma"))
        try:
            self._chroma_collection = client.get_collection("jarvis_memory")
        except Exception:
            self._chroma_collection = client.create_collection("jarvis_memory")
        self._chroma_client = client
        logger.info("ChromaDB initialized")

    def _get_embedding(self, text: str) -> list[float]:
        """Get embedding for text using local model."""
        if self._sentence_transformer is None:
            from sentence_transformers import SentenceTransformer
            self._sentence_transformer = SentenceTransformer(self._embedding_model)
            logger.info("Embedding model loaded: %s", self._embedding_model)

        embedding = self._sentence_transformer.encode(text)
        return embedding.tolist()

    def store(
        self,
        entry_id: str,
        content: str,
        entry_type: str = "episodic",
        metadata: Optional[dict] = None,
    ) -> None:
        """Store a memory entry in the vector DB."""
        try:
            embedding = self._get_embedding(content)
            self._chroma_collection.upsert(
                ids=[entry_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[{"type": entry_type, **(metadata or {})}],
            )
            logger.debug("Memory stored: %s (%s)", entry_id, entry_type)
        except Exception as e:
            logger.error("Failed to store memory: %s", e)

    def search(self, query: str, limit: int = 5, entry_type: Optional[str] = None) -> list[dict]:
        """Search memories by semantic similarity."""
        try:
            kwargs: dict[str, Any] = {
                "query_texts": [query],
                "n_results": limit,
            }
            if entry_type:
                kwargs["where"] = {"type": entry_type}

            results = self._chroma_collection.query(**kwargs)
            entries = []
            for i, doc_id in enumerate(results.get("ids", [[]])[0]):
                entries.append({
                    "id": doc_id,
                    "content": results.get("documents", [[]])[0][i],
                    "metadata": results.get("metadatas", [[]])[0][i],
                    "distance": results.get("distances", [[]])[0][i] if results.get("distances") else None,
                })
            return entries
        except Exception as e:
            logger.error("Memory search failed: %s", e)
            return []

    # ── NetworkX (Knowledge Graph) ──────────────────────────────────────

    def _init_graph(self) -> None:
        import networkx as nx

        self._graph = nx.DiGraph()
        # Load existing graph if persisted
        graph_file = self.persist_dir / "knowledge_graph.json"
        if graph_file.exists():
            try:
                data = json.loads(graph_file.read_text(encoding="utf-8"))
                self._graph = nx.node_link_graph(data)
                logger.info("Knowledge graph loaded: %d nodes, %d edges",
                           self._graph.number_of_nodes(), self._graph.number_of_edges())
            except Exception as e:
                logger.warning("Failed to load knowledge graph: %s", e)

    def add_concept(
        self,
        concept: str,
        description: str = "",
        category: str = "general",
        properties: Optional[dict] = None,
    ) -> None:
        """Add a concept to the knowledge graph."""
        self._graph.add_node(
            concept,
            description=description,
            category=category,
            properties=properties or {},
            created_at=datetime.now().isoformat(),
            access_count=0,
        )
        self._persist_graph()

    def add_relationship(
        self,
        source: str,
        target: str,
        relation: str,
        evidence: str = "",
    ) -> None:
        """Add a relationship between two concepts."""
        # Ensure nodes exist
        if not self._graph.has_node(source):
            self.add_concept(source)
        if not self._graph.has_node(target):
            self.add_concept(target)

        self._graph.add_edge(
            source, target,
            relation=relation,
            evidence=evidence,
            created_at=datetime.now().isoformat(),
        )
        self._persist_graph()

    def query_graph(self, concept: str, max_depth: int = 2) -> dict[str, Any]:
        """Get all related concepts within a certain depth."""
        if not self._graph.has_node(concept):
            return {"error": f"Concept not found: {concept}"}

        # Get neighbors
        subgraph_nodes = {concept}
        for depth in range(1, max_depth + 1):
            current = set(subgraph_nodes)
            for node in current:
                successors = set(self._graph.successors(node))
                predecessors = set(self._graph.predecessors(node))
                subgraph_nodes.update(successors)
                subgraph_nodes.update(predecessors)

        subgraph = self._graph.subgraph(subgraph_nodes)

        # Build result
        result = {
            "concept": concept,
            "nodes": {},
            "edges": [],
        }

        for node in subgraph.nodes():
            result["nodes"][node] = dict(subgraph.nodes[node])

        for u, v, data in subgraph.edges(data=True):
            result["edges"].append({
                "source": u,
                "target": v,
                "relation": data.get("relation", ""),
                "evidence": data.get("evidence", ""),
            })

        # Increment access count
        if self._graph.has_node(concept):
            node = self._graph.nodes[concept]
            node["access_count"] = node.get("access_count", 0) + 1
            self._persist_graph()

        return result

    def find_path(self, source: str, target: str) -> list[dict]:
        """Find paths between two concepts."""
        try:
            import networkx as nx
            paths = list(nx.all_simple_paths(self._graph, source, target, cutoff=4))
            result = []
            for path in paths[:5]:  # Limit
                path_info = []
                for i in range(len(path) - 1):
                    edge_data = self._graph.get_edge_data(path[i], path[i+1])
                    path_info.append({
                        "from": path[i],
                        "to": path[i+1],
                        "relation": edge_data.get("relation", "") if edge_data else "",
                    })
                result.append(path_info)
            return result
        except Exception:
            return []

    def _persist_graph(self) -> None:
        """Save graph to disk."""
        import networkx as nx
        graph_file = self.persist_dir / "knowledge_graph.json"
        try:
            data = nx.node_link_data(self._graph)
            graph_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning("Failed to persist graph: %s", e)

    # ── Self-Learning Loop ──────────────────────────────────────────────

    def _load_lessons(self) -> None:
        if self._lessons_file.exists():
            try:
                self._lessons = json.loads(self._lessons_file.read_text(encoding="utf-8"))
                logger.info("Loaded %d lessons", len(self._lessons))
            except Exception as e:
                logger.warning("Failed to load lessons: %s", e)

    def store_lesson(
        self,
        failure_description: str,
        error_details: str,
        root_cause: str,
        fix_applied: str,
        domain: str = "general",
    ) -> None:
        """Store a lesson from a failure.

        This is the key self-learning mechanism:
        1. Detect failure
        2. Analyze root cause
        3. Generate lesson
        4. Update relevant skill/prompt
        5. Store in memory
        """
        lesson = {
            "id": hashlib.md5(f"{failure_description}{datetime.now().isoformat()}".encode()).hexdigest()[:12],
            "failure": failure_description,
            "error": error_details,
            "root_cause": root_cause,
            "fix": fix_applied,
            "domain": domain,
            "created_at": datetime.now().isoformat(),
            "applied": False,
        }

        self._lessons.append(lesson)
        self._lessons_file.write_text(json.dumps(self._lessons, indent=2), encoding="utf-8")

        # Also store in vector memory for semantic retrieval
        self.store(
            entry_id=f"lesson_{lesson['id']}",
            content=f"Failure: {failure_description}\nRoot cause: {root_cause}\nFix: {fix_applied}",
            entry_type="lesson",
            metadata={"domain": domain},
        )

        # Add to knowledge graph
        self.add_concept(
            concept=domain,
            description=f"Domain with {len([l for l in self._lessons if l['domain'] == domain])} lessons",
            category="domain",
        )
        self.add_relationship(
            source=failure_description[:50],
            target=domain,
            relation="occurs_in",
            evidence=fix_applied[:100],
        )

        logger.info("Lesson stored: %s → %s", lesson["id"][:8], domain)

    def get_relevant_lessons(self, query: str, limit: int = 3) -> list[dict]:
        """Get lessons relevant to the current task."""
        # Vector search
        vector_results = self.search(query, limit=limit, entry_type="lesson")

        lessons = []
        for result in vector_results:
            # Find matching lesson
            for lesson in self._lessons:
                if lesson["id"] in result.get("id", ""):
                    lessons.append(lesson)
                    break

        return lessons

    def get_lesson_context(self, query: str) -> str:
        """Format relevant lessons as context for LLM prompts."""
        lessons = self.get_relevant_lessons(query)
        if not lessons:
            return ""

        lines = ["Lessons learned from past failures:"]
        for lesson in lessons:
            lines.append(
                f"- Problem: {lesson['failure'][:100]}\n"
                f"  Root cause: {lesson['root_cause'][:100]}\n"
                f"  Fix: {lesson['fix'][:100]}"
            )
        return "\n".join(lines)

    async def generate_lesson_from_failure(
        self,
        task_description: str,
        error_message: str,
        llm_router,
    ) -> Optional[dict]:
        """Use LLM to analyze a failure and generate a structured lesson."""
        messages = [
            {"role": "system", "content": (
                "You are a failure analysis system. Analyze the following task failure "
                "and provide a structured analysis with root cause and recommended fix. "
                "Be specific and actionable. Return JSON only."
            )},
            {"role": "user", "content": (
                f"Task: {task_description}\n"
                f"Error: {error_message}\n\n"
                f"Analyze and return JSON:\n"
                f'{{"root_cause": "...", "fix": "...", "prevention": "...", "domain": "..."}}'
            )},
        ]

        try:
            response = await llm_router.chat(messages, max_tokens=500)
            # Parse JSON
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
        except Exception as e:
            logger.warning("Lesson generation failed: %s", e)

        return None

    # ── Statistics ──────────────────────────────────────────────────────

    def stats(self) -> dict:
        return {
            "vector_entries": self._chroma_collection.count() if self._chroma_collection else 0,
            "graph_nodes": self._graph.number_of_nodes() if self._graph else 0,
            "graph_edges": self._graph.number_of_edges() if self._graph else 0,
            "lessons": len(self._lessons),
            "persist_dir": str(self.persist_dir),
        }

    def clear_all(self) -> None:
        """Nuclear option: wipe everything."""
        import networkx as nx
        import chromadb

        # Clear Chroma
        client = chromadb.PersistentClient(path=str(self.persist_dir / "chroma"))
        try:
            client.delete_collection("jarvis_memory")
        except Exception:
            pass
        self._chroma_collection = client.create_collection("jarvis_memory")

        # Clear graph
        self._graph = nx.DiGraph()

        # Clear lessons
        self._lessons = []
        self._lessons_file.write_text("[]", encoding="utf-8")

        logger.warning("All memory cleared")
