"""Memory Manager — Tüm bellek katmanlarını birleştiren tek arayüz.

Her konuşma turunda çağrılır: working memory'ye ekler, önem skoru hesaplar,
önemli bilgileri long_term'e kaydeder, entity extraction yapar.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from .long_term_memory import Entity, LongTermMemory, MemoryItem
from .procedural_memory import Procedure, ProceduralMemory
from .working_memory import WorkingMemory

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_IMPORTANCE_KEYWORDS = frozenset(
    {
        "important",
        "remember",
        "save",
        "learn",
        "critical",
        "must",
        "should",
        "önemli",
        "hatırla",
        "kaydet",
        "öğren",
        "kritik",
        "mutlaka",
    }
)

_LENGTH_THRESHOLD = 100
_IMPORTANCE_THRESHOLD = 0.3

_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_URL_RE = re.compile(r"https?://[^\s<>\"')\]}]+")
_FILEPATH_RE = re.compile(r"(?:[A-Za-z]:\\|/)[^\s<>\"']+[\w.-]+")


# ---------------------------------------------------------------------------
# MemoryContext
# ---------------------------------------------------------------------------


@dataclass
class MemoryContext:
    """Bir konuşma turu için birleştirilmiş bellek bağlamı."""

    working_messages: list[dict[str, str]] = field(default_factory=list)
    relevant_memories: list[MemoryItem] = field(default_factory=list)
    relevant_procedures: list[Procedure] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)

    def format_for_llm(self) -> str:
        """Tüm bağlamı LLM tarafından okunabilir tek bir metne dönüştür."""
        sections: list[str] = []

        # --- Working memory ---
        if self.working_messages:
            lines = ["## Recent Conversation"]
            for msg in self.working_messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                lines.append(f"**{role}**: {content}")
            sections.append("\n".join(lines))

        # --- Relevant long-term memories ---
        if self.relevant_memories:
            lines = ["## Relevant Memories"]
            for mem in self.relevant_memories:
                lines.append(
                    f"- [{mem.kind}] (score={mem.score:.3f}, "
                    f"importance={mem.importance:.2f}) {mem.content}"
                )
            sections.append("\n".join(lines))

        # --- Relevant procedures ---
        if self.relevant_procedures:
            lines = ["## Relevant Procedures"]
            for proc in self.relevant_procedures:
                lines.append(
                    f"- **{proc.trigger}** "
                    f"(success_rate={proc.success_rate:.2f}, uses={proc.uses})"
                )
                if proc.steps:
                    for idx, step in enumerate(proc.steps, 1):
                        lines.append(f"  {idx}. {step}")
            sections.append("\n".join(lines))

        # --- Entities ---
        if self.entities:
            lines = ["## Known Entities"]
            for ent in self.entities:
                attrs = ", ".join(
                    f"{k}={v}" for k, v in ent.attributes.items()
                )
                lines.append(
                    f"- **{ent.name}** ({ent.entity_type})"
                    + (f" — {attrs}" if attrs else "")
                )
            sections.append("\n".join(lines))

        if not sections:
            return "(no additional context available)"

        return "\n\n".join(sections)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation for serialization."""
        return {
            "working_messages": self.working_messages,
            "relevant_memories": [
                {
                    "id": m.id,
                    "kind": m.kind,
                    "content": m.content,
                    "score": m.score,
                    "importance": m.importance,
                    "tags": m.tags,
                    "created_at": m.created_at,
                }
                for m in self.relevant_memories
            ],
            "relevant_procedures": [p.to_dict() for p in self.relevant_procedures],
            "entities": [
                {
                    "id": e.id,
                    "name": e.name,
                    "entity_type": e.entity_type,
                    "attributes": e.attributes,
                    "last_seen": e.last_seen,
                }
                for e in self.entities
            ],
        }


# ---------------------------------------------------------------------------
# MemoryManager
# ---------------------------------------------------------------------------


class MemoryManager:
    """Unified interface that ties WorkingMemory, LongTermMemory,
    and ProceduralMemory into a single high-level API.

    Typical lifecycle::

        manager = MemoryManager(config)
        await manager.initialize()

        await manager.process_turn(user_msg="Hello", assistant_msg="Hi!")
        ctx = await manager.get_context("What do I need to do?")
        print(ctx.format_for_llm())

        await manager.nightly_consolidation()
        await manager.close()
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        cfg = config or {}

        # Working memory config
        wm_cfg = cfg.get("working_memory", {})
        self.working = WorkingMemory(
            max_messages=wm_cfg.get("max_messages", 20),
            max_tokens=wm_cfg.get("max_tokens", 4000),
        )

        # Long-term memory config
        lt_cfg = cfg.get("long_term_memory", {})
        self.long_term = LongTermMemory(
            db_path=lt_cfg.get("db_path"),
            embedding_model=lt_cfg.get("embedding_model", "all-MiniLM-L6-v2"),
            chroma_persist_dir=lt_cfg.get("chroma_persist_dir"),
        )

        # Procedural memory config
        self.procedural = ProceduralMemory()
        self._procedural_db_path = cfg.get("procedural_memory", {}).get(
            "db_path", "data/procedures.db"
        )

        # Thresholds
        self._importance_threshold = cfg.get("importance_threshold", _IMPORTANCE_THRESHOLD)

    # ── lifecycle ─────────────────────────────────────────────────────

    async def initialize(self) -> None:
        """Initialize long-term and procedural memory backends."""
        try:
            await self.long_term.initialize()
        except Exception:
            logger.exception("Failed to initialize LongTermMemory")
            raise

        try:
            await self.procedural.initialize(db_path=self._procedural_db_path)
        except Exception:
            logger.exception("Failed to initialize ProceduralMemory")
            raise

        logger.info("MemoryManager fully initialized")

    async def close(self) -> None:
        """Release long-term and procedural memory resources."""
        try:
            # LongTermMemory uses aiosqlite context managers per call — no
            # persistent connection to close.  ChromaDB is process-scoped.
            logger.debug("LongTermMemory has no persistent connection to close")
        except Exception:
            logger.exception("Error during LongTermMemory close")

        try:
            await self.procedural.close()
        except Exception:
            logger.exception("Error during ProceduralMemory close")

        logger.info("MemoryManager closed")

    # ── importance scoring ────────────────────────────────────────────

    @staticmethod
    def _calculate_importance(
        user_msg: str,
        assistant_msg: str,
        metadata: dict[str, Any] | None = None,
    ) -> float:
        """Heuristic importance scorer (0.0 – 1.0)."""
        combined = f"{user_msg} {assistant_msg}".lower()
        score = 0.0

        # Length signal
        if len(combined) > _LENGTH_THRESHOLD:
            score += 0.2

        # Numbers / dates signal
        if re.search(r"\b\d{1,4}[-/]\d{1,2}[-/]\d{1,4}\b", combined):
            score += 0.1

        # Question signal
        if "?" in combined:
            score += 0.15

        # Keyword signal
        words = set(combined.split())
        if words & _IMPORTANCE_KEYWORDS:
            score += 0.25

        # Metadata override
        if metadata and "importance" in metadata:
            try:
                meta_score = float(metadata["importance"])
                score = max(score, meta_score)
            except (TypeError, ValueError):
                logger.warning("Invalid metadata importance value: %r", metadata["importance"])

        return min(score, 1.0)

    # ── entity extraction ─────────────────────────────────────────────

    @staticmethod
    def _extract_entities(text: str) -> list[dict[str, str]]:
        """Simple regex-based entity extraction."""
        entities: list[dict[str, str]] = []

        for match in _DATE_RE.finditer(text):
            entities.append({"type": "date", "value": match.group()})

        for match in _EMAIL_RE.finditer(text):
            entities.append({"type": "email", "value": match.group()})

        for match in _URL_RE.finditer(text):
            entities.append({"type": "url", "value": match.group()})

        for match in _FILEPATH_RE.finditer(text):
            entities.append({"type": "file_path", "value": match.group()})

        return entities

    # ── core: process a single turn ───────────────────────────────────

    async def process_turn(
        self,
        user_msg: str,
        assistant_msg: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Process one conversation turn.

        1. Add both messages to working memory.
        2. Calculate importance score.
        3. If above threshold → store as episode in long-term memory.
        4. Extract entities and persist them.
        5. Check procedural memory for relevant procedures.

        Parameters
        ----------
        user_msg:
            The user's message text.
        assistant_msg:
            The assistant's response text.
        metadata:
            Optional dict with extra signals (e.g. ``importance``).

        Returns
        -------
        dict
            Summary of what happened during this turn.
        """
        # 1. Working memory
        self.working.add("user", user_msg, metadata)
        self.working.add("assistant", assistant_msg)

        # 2. Importance
        importance = self._calculate_importance(user_msg, assistant_msg, metadata)

        result: dict[str, Any] = {
            "importance": importance,
            "stored_episode": False,
            "entities_extracted": 0,
            "procedures_found": 0,
        }

        # 3. Long-term storage
        if importance > self._importance_threshold:
            try:
                # Build a compact summary from both messages
                user_preview = (
                    user_msg[:200] + "…" if len(user_msg) > 200 else user_msg
                )
                assistant_preview = (
                    assistant_msg[:200] + "…"
                    if len(assistant_msg) > 200
                    else assistant_msg
                )
                summary = f"User: {user_preview}\nAssistant: {assistant_preview}"

                await self.long_term.store_episode(
                    summary=summary,
                    tags=self._extract_tags(user_msg),
                    importance=importance,
                )
                result["stored_episode"] = True
                logger.debug(
                    "Episode stored (importance=%.3f)", importance
                )
            except Exception:
                logger.exception(
                    "Failed to store episode (importance=%.3f)", importance
                )

        # 4. Entity extraction
        combined_text = f"{user_msg} {assistant_msg}"
        entities = self._extract_entities(combined_text)
        for ent in entities:
            try:
                await self.long_term.store_entity(
                    name=ent["value"],
                    entity_type=ent["type"],
                    attributes={"source": "process_turn"},
                )
            except Exception:
                logger.exception("Failed to store entity %s", ent["value"])

        result["entities_extracted"] = len(entities)

        # 5. Procedural memory lookup
        try:
            procedures = await self.procedural.get_best_procedure(user_msg)
            result["procedures_found"] = len(procedures)
            if procedures:
                logger.debug(
                    "Found %d relevant procedures for turn", len(procedures)
                )
        except Exception:
            logger.exception("Failed to query procedural memory")

        return result

    # ── context retrieval ─────────────────────────────────────────────

    async def get_context(
        self,
        query: str,
        top_k_memories: int = 5,
        top_k_procedures: int = 3,
    ) -> MemoryContext:
        """Build a unified context for the LLM based on *query*.

        Parameters
        ----------
        query:
            The current user prompt used to retrieve relevant memories
            and procedures.
        top_k_memories:
            How many long-term memories to fetch.
        top_k_procedures:
            How many procedures to fetch.

        Returns
        -------
        MemoryContext
            Populated context dataclass ready for ``format_for_llm()``.
        """
        # Working memory (recent messages)
        working_msgs = self.working.to_messages()

        # Long-term recall
        relevant_mems: list[MemoryItem] = []
        try:
            relevant_mems = await self.long_term.recall(
                query=query,
                top_k=top_k_memories,
            )
        except Exception:
            logger.exception("Long-term recall failed for query=%r", query)

        # Procedural lookup
        relevant_procs: list[Procedure] = []
        try:
            relevant_procs = await self.procedural.get_best_procedure(
                query=query,
                top_k=top_k_procedures,
            )
        except Exception:
            logger.exception("Procedural lookup failed for query=%r", query)

        # Entities
        ents: list[Entity] = []
        try:
            ents = await self._get_entities()
        except Exception:
            logger.exception("Failed to retrieve entities")

        return MemoryContext(
            working_messages=working_msgs,
            relevant_memories=relevant_mems,
            relevant_procedures=relevant_procs,
            entities=ents,
        )

    # ── nightly consolidation ─────────────────────────────────────────

    async def nightly_consolidation(self) -> dict[str, Any]:
        """Run periodic maintenance: forget old items, consolidate.

        Intended to be scheduled nightly (or at any low-traffic window).

        Returns
        -------
        dict
            Consolidation statistics.
        """
        logger.info("Nightly consolidation started")
        stats: dict[str, Any] = {}

        # 1. Forgetting
        try:
            forget_stats = await self.long_term.forget_old(
                days=90,
                importance_threshold=0.2,
            )
            stats["forget"] = forget_stats
            logger.info("Forget phase: %s", forget_stats)
        except Exception:
            logger.exception("Forget phase failed")
            stats["forget"] = {"error": "forget phase failed"}

        # 2. Consolidation
        try:
            consolidate_stats = await self.long_term.consolidate()
            stats["consolidate"] = consolidate_stats
            logger.info("Consolidate phase: %s", consolidate_stats)
        except Exception:
            logger.exception("Consolidate phase failed")
            stats["consolidate"] = {"error": "consolidate phase failed"}

        stats["status"] = "completed"
        logger.info("Nightly consolidation completed: %s", stats)
        return stats

    # ── aggregate stats ───────────────────────────────────────────────

    async def stats(self) -> dict[str, Any]:
        """Aggregate statistics from all three memory layers.

        Returns
        -------
        dict
            Keys: ``working``, ``long_term``, ``procedural``.
        """
        working_stats = self.working.stats()

        try:
            lt_stats = await self._long_term_stats()
        except Exception:
            logger.exception("Failed to get long-term stats")
            lt_stats = {"error": "unavailable"}

        try:
            proc_stats = await self.procedural.live_stats()
        except Exception:
            logger.exception("Failed to get procedural stats")
            proc_stats = self.procedural.stats()

        return {
            "working": working_stats,
            "long_term": lt_stats,
            "procedural": proc_stats,
        }

    # ── helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _extract_tags(text: str) -> list[str]:
        """Derive simple tags from message content."""
        tags: list[str] = []
        lower = text.lower()

        if any(kw in lower for kw in ("task", "görev", "todo", "yapılacak")):
            tags.append("task")
        if any(kw in lower for kw in ("meeting", "toplantı", "calendar", "takvim")):
            tags.append("meeting")
        if any(kw in lower for kw in ("code", "kod", "bug", "fix", "debug")):
            tags.append("code")
        if any(kw in lower for kw in ("email", "mail", "message", "mesaj")):
            tags.append("communication")
        if any(kw in lower for kw in ("file", "dosya", "document", "belge")):
            tags.append("file")
        if any(kw in lower for kw in ("question", "soru", "how", "what", "why")):
            tags.append("question")

        return tags

    async def _get_entities(self) -> list[Entity]:
        """Retrieve known entities from long-term memory.

        LongTermMemory does not expose a ``get_entities`` method directly,
        so we query the SQLite ``entities`` table.
        """
        entities: list[Entity] = []

        try:
            import aiosqlite  # noqa: PLC0415

            # Use the same DB path as long_term
            db_path = str(self.long_term._db_path)
            async with aiosqlite.connect(db_path) as db:
                cursor = await db.execute(
                    "SELECT id, name, type, attributes, last_seen FROM entities "
                    "ORDER BY last_seen DESC LIMIT 100"
                )
                rows = await cursor.fetchall()
                for row in rows:
                    import json  # noqa: PLC0415

                    entities.append(
                        Entity(
                            id=row[0],
                            name=row[1],
                            entity_type=row[2],
                            attributes=json.loads(row[3]) if row[3] else {},
                            last_seen=row[4] or "",
                        )
                    )
        except Exception:
            logger.exception("Failed to retrieve entities from long-term DB")

        return entities

    async def _long_term_stats(self) -> dict[str, Any]:
        """Query long-term memory table sizes."""
        import aiosqlite  # noqa: PLC0415

        db_path = str(self.long_term._db_path)
        async with aiosqlite.connect(db_path) as db:
            ep_row = await (await db.execute("SELECT COUNT(*) FROM episodes")).fetchone()
            fa_row = await (await db.execute("SELECT COUNT(*) FROM facts")).fetchone()
            en_row = await (await db.execute("SELECT COUNT(*) FROM entities")).fetchone()

        return {
            "episodes": ep_row[0] if ep_row else 0,
            "facts": fa_row[0] if fa_row else 0,
            "entities": en_row[0] if en_row else 0,
        }
