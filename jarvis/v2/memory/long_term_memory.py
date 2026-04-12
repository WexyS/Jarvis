"""Long-Term Memory — Episodic + Semantic kalıcı bellek.

SQLite + FTS5 tabanlı kalıcı bellek. ChromaDB ile vektör arama.
Her fact/episode otomatik embed edilir, hibrit arama (FTS5 + vector) yapar.
Sonuçlar RRF (Reciprocal Rank Fusion) ile birleştirilir.
Decay mekanizması ile eski/önemsiz bilgiler zamanla unutulur.
"""

from __future__ import annotations

import json
import logging
import math
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import aiosqlite

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class MemoryItem:
    """Tek bir geri çağrılan bellek öğesi."""

    id: int
    kind: str  # "episode" | "fact"
    content: str
    score: float
    importance: float = 0.5
    confidence: float = 1.0
    tags: list[str] = field(default_factory=list)
    source: str = ""
    created_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Entity:
    """Bilinen bir varlık (kişi, yer, kavram …)."""

    id: int
    name: str
    entity_type: str
    attributes: dict[str, Any] = field(default_factory=dict)
    last_seen: str = ""


# ---------------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------------

class _EmbeddingModel:
    """Lazy-loaded sentence-transformers wrapper."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._model_name = model_name
        self._model: Any = None

    # -- public -----------------------------------------------------------

    def encode(self, texts: str | list[str]) -> list[float] | list[list[float]]:
        """Encode one or more texts into dense vectors."""
        model = self._load()
        if isinstance(texts, str):
            vec = model.encode(texts)
            return vec.tolist()
        vectors = model.encode(texts)
        return [v.tolist() for v in vectors]

    # -- private ----------------------------------------------------------

    def _load(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # noqa: PLC0415

            self._model = SentenceTransformer(self._model_name)
            logger.info("Embedding model loaded: %s", self._model_name)
        return self._model


# ---------------------------------------------------------------------------
# LongTermMemory
# ---------------------------------------------------------------------------

_RRF_K = 60
_DEFAULT_DECAY_DAYS = 90.0
_DEFAULT_IMPORTANCE_THRESHOLD = 0.2
_DEFAULT_MIN_IMPORTANCE = 0.3
_DEFAULT_TOP_K = 5


class LongTermMemory:
    """Long-term episodic + semantic memory backed by SQLite + ChromaDB.

    * Episodes  → olay bazlı kayıtlar (summary, tags, importance)
    * Facts     → doğrulanabilir bilgiler (content, source, confidence)
    * Entities  → isimlendirilmiş varlıklar (name, type, attributes)

    Hibrit arama: FTS5 (lexical) + ChromaDB (semantic) → RRF ile fusion.
    """

    def __init__(
        self,
        db_path: str | Path | None = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        chroma_persist_dir: str | Path | None = None,
    ) -> None:
        self._db_path = Path(
            db_path
            or os.environ.get(
                "JARVIS_MEMORY_DB",
                "./data/memory/long_term.db",
            )
        )
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        self._embedder = _EmbeddingModel(embedding_model)

        # ChromaDB — lazy init
        self._chroma_client: Any = None
        self._chroma_collection: Any = None
        self._chroma_persist_dir = chroma_persist_dir

        self._initialized = False

    # ── lazy bootstrap ───────────────────────────────────────────────────

    async def initialize(self) -> None:
        """Create tables / FTS5 indexes if they don't exist."""
        if self._initialized:
            return

        async with aiosqlite.connect(str(self._db_path)) as db:
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute("PRAGMA foreign_keys=ON")

            # episodes
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS episodes (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                    summary     TEXT    NOT NULL,
                    tags        TEXT    NOT NULL DEFAULT '[]',
                    importance  REAL    NOT NULL DEFAULT 0.5,
                    decay       REAL    NOT NULL DEFAULT 90.0
                )
                """
            )

            # facts
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS facts (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    content     TEXT    NOT NULL,
                    source      TEXT    NOT NULL DEFAULT '',
                    confidence  REAL    NOT NULL DEFAULT 1.0,
                    created_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                    updated_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                )
                """
            )

            # entities
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS entities (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT    NOT NULL UNIQUE,
                    type        TEXT    NOT NULL DEFAULT 'general',
                    attributes  TEXT    NOT NULL DEFAULT '{}',
                    last_seen   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
                )
                """
            )

            # FTS5 virtual tables
            await db.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(
                    summary, tags,
                    content='episodes',
                    content_rowid='id'
                )
                """
            )
            await db.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
                    content, source,
                    content='facts',
                    content_rowid='id'
                )
                """
            )

            # Triggers to keep FTS5 in sync
            await db.executescript(
                """
                -- episodes triggers
                CREATE TRIGGER IF NOT EXISTS episodes_ai AFTER INSERT ON episodes BEGIN
                    INSERT INTO episodes_fts(rowid, summary, tags)
                    VALUES (new.id, new.summary, new.tags);
                END;

                CREATE TRIGGER IF NOT EXISTS episodes_ad AFTER DELETE ON episodes BEGIN
                    INSERT INTO episodes_fts(episodes_fts, rowid, summary, tags)
                    VALUES ('delete', old.id, old.summary, old.tags);
                END;

                CREATE TRIGGER IF NOT EXISTS episodes_au AFTER UPDATE ON episodes BEGIN
                    INSERT INTO episodes_fts(episodes_fts, rowid, summary, tags)
                    VALUES ('delete', old.id, old.summary, old.tags);
                    INSERT INTO episodes_fts(rowid, summary, tags)
                    VALUES (new.id, new.summary, new.tags);
                END;

                -- facts triggers
                CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON facts BEGIN
                    INSERT INTO facts_fts(rowid, content, source)
                    VALUES (new.id, new.content, new.source);
                END;

                CREATE TRIGGER IF NOT EXISTS facts_ad AFTER DELETE ON facts BEGIN
                    INSERT INTO facts_fts(facts_fts, rowid, content, source)
                    VALUES ('delete', old.id, old.content, old.source);
                END;

                CREATE TRIGGER IF NOT EXISTS facts_au AFTER UPDATE ON facts BEGIN
                    INSERT INTO facts_fts(facts_fts, rowid, content, source)
                    VALUES ('delete', old.id, old.content, old.source);
                    INSERT INTO facts_fts(rowid, content, source)
                    VALUES (new.id, new.content, new.source);
                END;
                """
            )

            await db.commit()

        self._initialized = True
        logger.info(
            "LongTermMemory initialized — db=%s", self._db_path
        )

    # ── ChromaDB lazy init ───────────────────────────────────────────────

    def _ensure_chroma(self) -> Any:
        """Return the ChromaDB collection, initializing on first call."""
        if self._chroma_collection is not None:
            return self._chroma_collection

        import chromadb  # noqa: PLC0415

        persist = self._chroma_persist_dir or str(self._db_path.parent / "chroma_ltm")
        client = chromadb.PersistentClient(path=persist)
        try:
            collection = client.get_collection("long_term_memory")
        except Exception:
            collection = client.create_collection(
                name="long_term_memory",
                metadata={"hnsw:space": "cosine"},
            )
        self._chroma_client = client
        self._chroma_collection = collection
        logger.info("ChromaDB collection ready: %s", persist)
        return collection

    # ── public store methods ─────────────────────────────────────────────

    async def store_episode(
        self,
        summary: str,
        tags: list[str] | None = None,
        importance: float = 0.5,
        decay: float = _DEFAULT_DECAY_DAYS,
    ) -> int:
        """Store an episodic memory."""
        await self.initialize()

        tags_json = json.dumps(tags or [], ensure_ascii=False)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        async with aiosqlite.connect(str(self._db_path)) as db:
            cursor = await db.execute(
                """
                INSERT INTO episodes (timestamp, summary, tags, importance, decay)
                VALUES (?, ?, ?, ?, ?)
                """,
                (now, summary, tags_json, importance, decay),
            )
            await db.commit()
            episode_id = cursor.lastrowid

        # ChromaDB
        try:
            chroma_text = f"{' '.join(tags or [])} {summary}"
            embedding = self._embedder.encode(chroma_text)
            collection = self._ensure_chroma()
            collection.upsert(
                ids=[f"episode_{episode_id}"],
                embeddings=[embedding],
                documents=[summary],
                metadatas=[{
                    "kind": "episode",
                    "tags": tags_json,
                    "importance": importance,
                    "created_at": now,
                }],
            )
        except Exception:
            logger.exception("ChromaDB upsert failed for episode %d", episode_id)

        logger.debug(
            "Episode stored id=%d importance=%.2f tags=%s",
            episode_id, importance, tags,
        )
        return episode_id  # type: ignore[return-value]

    async def store_fact(
        self,
        content: str,
        source: str = "",
        confidence: float = 1.0,
    ) -> int:
        """Store a semantic fact."""
        await self.initialize()

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        async with aiosqlite.connect(str(self._db_path)) as db:
            cursor = await db.execute(
                """
                INSERT INTO facts (content, source, confidence, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (content, source, confidence, now, now),
            )
            await db.commit()
            fact_id = cursor.lastrowid

        # ChromaDB
        try:
            embedding = self._embedder.encode(content)
            collection = self._ensure_chroma()
            collection.upsert(
                ids=[f"fact_{fact_id}"],
                embeddings=[embedding],
                documents=[content],
                metadatas=[{
                    "kind": "fact",
                    "source": source,
                    "confidence": confidence,
                    "created_at": now,
                }],
            )
        except Exception:
            logger.exception("ChromaDB upsert failed for fact %d", fact_id)

        logger.debug(
            "Fact stored id=%d confidence=%.2f source=%s",
            fact_id, confidence, source,
        )
        return fact_id  # type: ignore[return-value]

    async def store_entity(
        self,
        name: str,
        entity_type: str,
        attributes: dict[str, Any] | None = None,
        last_seen: str | None = None,
    ) -> int:
        """Store or update a named entity."""
        await self.initialize()

        attr_json = json.dumps(attributes or {}, ensure_ascii=False)
        seen = last_seen or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        async with aiosqlite.connect(str(self._db_path)) as db:
            cursor = await db.execute(
                """
                INSERT INTO entities (name, type, attributes, last_seen)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    type=excluded.type,
                    attributes=excluded.attributes,
                    last_seen=excluded.last_seen
                RETURNING id
                """,
                (name, entity_type, attr_json, seen),
            )
            await db.commit()
            row = await cursor.fetchone()
            entity_id = row[0] if row else 0

        logger.debug(
            "Entity stored id=%d name=%s type=%s",
            entity_id, name, entity_type,
        )
        return entity_id  # type: ignore[return-value]

    # ── hybrid recall ────────────────────────────────────────────────────

    async def recall(
        self,
        query: str,
        top_k: int = _DEFAULT_TOP_K,
        min_importance: float = _DEFAULT_MIN_IMPORTANCE,
    ) -> list[MemoryItem]:
        """Hybrid FTS5 + vector search with RRF fusion."""
        await self.initialize()

        fts_scores: dict[tuple[str, int], float] = {}
        vec_scores: dict[tuple[str, int], float] = {}

        # 1 ─ FTS5 lexical search ─────────────────────────────────────
        async with aiosqlite.connect(str(self._db_path)) as db:
            # episodes
            rows = await db.execute(
                """
                SELECT e.id, e.summary, e.tags, e.importance,
                       rank
                FROM episodes_fts f
                JOIN episodes e ON e.id = f.rowid
                WHERE episodes_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (self._fts_escape(query), top_k * 3),
            )
            for rank, row in enumerate(await rows.fetchall(), 1):
                eid, summary, tags_json, importance, _ = row
                if importance < min_importance:
                    continue
                tags = json.loads(tags_json)
                fts_scores[("episode", eid)] = rank  # lower rank = better

            # facts
            rows = await db.execute(
                """
                SELECT f.id, f.content, f.source, f.confidence,
                       rank
                FROM facts_fts f
                JOIN facts f ON f.id = f.rowid
                WHERE facts_fts MATCH ?
                ORDER BY rank
                LIMIT ?
                """,
                (self._fts_escape(query), top_k * 3),
            )
            for rank, row in enumerate(await rows.fetchall(), 1):
                fid, content, source, confidence, _ = row
                fts_scores[("fact", fid)] = rank

        # 2 ─ ChromaDB vector search ──────────────────────────────────
        try:
            embedding = self._embedder.encode(query)
            collection = self._ensure_chroma()
            results = collection.query(
                query_embeddings=[embedding],
                n_results=top_k * 3,
                include=["metadatas", "documents", "distances"],
            )

            for idx, doc_id in enumerate(results.get("ids", [[]])[0]):
                meta = (results.get("metadatas", [[]])[0])[idx] if results.get("metadatas") else {}
                kind = meta.get("kind", "fact")
                raw_id = int(doc_id.split("_", 1)[1])
                vec_scores[(kind, raw_id)] = idx + 1  # 1-based rank
        except Exception:
            logger.exception("ChromaDB vector search failed")

        # 3 ─ RRF fusion ──────────────────────────────────────────────
        combined_scores: dict[tuple[str, int], float] = {}
        for key, rank in fts_scores.items():
            combined_scores[key] = combined_scores.get(key, 0.0) + 1.0 / (_RRF_K + rank)
        for key, rank in vec_scores.items():
            combined_scores[key] = combined_scores.get(key, 0.0) + 1.0 / (_RRF_K + rank)

        # 4 ─ Build result items ──────────────────────────────────────
        items: list[MemoryItem] = []

        # Fetch episode details
        episode_ids = [eid for (kind, eid) in combined_scores if kind == "episode"]
        if episode_ids:
            placeholders = ",".join("?" * len(episode_ids))
            async with aiosqlite.connect(str(self._db_path)) as db:
                cursor = await db.execute(
                    f"SELECT id, summary, tags, importance, timestamp FROM episodes WHERE id IN ({placeholders})",
                    episode_ids,
                )
                for row in await cursor.fetchall():
                    eid, summary, tags_json, importance, ts = row
                    tags = json.loads(tags_json)
                    items.append(MemoryItem(
                        id=eid,
                        kind="episode",
                        content=summary,
                        score=combined_scores.get(("episode", eid), 0.0),
                        importance=importance,
                        tags=tags,
                        created_at=ts,
                    ))

        # Fetch fact details
        fact_ids = [fid for (kind, fid) in combined_scores if kind == "fact"]
        if fact_ids:
            placeholders = ",".join("?" * len(fact_ids))
            async with aiosqlite.connect(str(self._db_path)) as db:
                cursor = await db.execute(
                    f"SELECT id, content, source, confidence, created_at FROM facts WHERE id IN ({placeholders})",
                    fact_ids,
                )
                for row in await cursor.fetchall():
                    fid, content, source, confidence, ts = row
                    items.append(MemoryItem(
                        id=fid,
                        kind="fact",
                        content=content,
                        score=combined_scores.get(("fact", fid), 0.0),
                        confidence=confidence,
                        source=source,
                        created_at=ts,
                    ))

        # Sort by RRF score descending, return top_k
        items.sort(key=lambda x: x.score, reverse=True)
        return items[:top_k]

    # ── forget / decay ───────────────────────────────────────────────────

    async def forget_old(
        self,
        days: int = _DEFAULT_DECAY_DAYS,
        importance_threshold: float = _DEFAULT_IMPORTANCE_THRESHOLD,
    ) -> dict[str, int]:
        """Apply exponential decay and delete items below threshold."""
        await self.initialize()

        now_ts = time.time()
        decay_days = float(days)
        deleted_episodes = 0
        deleted_facts = 0
        decayed_episodes = 0
        decayed_facts = 0

        async with aiosqlite.connect(str(self._db_path)) as db:
            # ── Episodes decay + delete ──
            rows = await db.execute(
                "SELECT id, importance, timestamp, decay FROM episodes"
            )
            for row in await rows.fetchall():
                eid, importance, ts, decay = row
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0
                effective_decay = decay if decay else decay_days
                new_importance = importance * math.exp(-age_days / effective_decay)

                if new_importance < importance_threshold:
                    await db.execute("DELETE FROM episodes WHERE id=?", (eid,))
                    deleted_episodes += 1
                else:
                    await db.execute(
                        "UPDATE episodes SET importance=? WHERE id=?",
                        (round(new_importance, 6), eid),
                    )
                    decayed_episodes += 1

            # ── Facts decay (via confidence proxy) ──
            rows = await db.execute(
                "SELECT id, confidence, created_at FROM facts"
            )
            for row in await rows.fetchall():
                fid, confidence, ts = row
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0
                new_confidence = confidence * math.exp(-age_days / decay_days)

                if new_confidence < importance_threshold:
                    await db.execute("DELETE FROM facts WHERE id=?", (fid,))
                    deleted_facts += 1
                else:
                    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                    await db.execute(
                        "UPDATE facts SET confidence=?, updated_at=? WHERE id=?",
                        (round(new_confidence, 6), now_str, fid),
                    )
                    decayed_facts += 1

            await db.commit()

        result = {
            "episodes_decayed": decayed_episodes,
            "episodes_deleted": deleted_episodes,
            "facts_decayed": decayed_facts,
            "facts_deleted": deleted_facts,
        }
        logger.info("forget_old completed: %s", result)
        return result

    # ── consolidate ──────────────────────────────────────────────────────

    async def consolidate(self) -> dict[str, int]:
        """Group semantically similar episodes and merge them.

        1. Fetch all episodes.
        2. Embed summaries.
        3. Pairwise cosine similarity → cluster via single-linkage (threshold 0.75).
        4. For each cluster with >1 episode, create a merged episode and delete originals.
        """
        await self.initialize()

        async with aiosqlite.connect(str(self._db_path)) as db:
            rows = await db.execute(
                "SELECT id, summary, tags, importance FROM episodes ORDER BY timestamp DESC"
            )
            episodes = await rows.fetchall()

        if len(episodes) < 2:
            return {"clusters_formed": 0, "episodes_merged": 0}

        summaries = [ep[1] for ep in episodes]
        ids = [ep[0] for ep in episodes]
        tag_lists = [json.loads(ep[2]) for ep in episodes]
        importances = [ep[3] for ep in episodes]

        # Embed all summaries
        vectors = self._embedder.encode(summaries)

        # Build similarity matrix (cosine)
        import numpy as np  # noqa: PLC0415

        vec_arr = np.array(vectors)
        norms = np.linalg.norm(vec_arr, axis=1, keepdims=True)
        norms[norms == 0] = 1e-8
        normalized = vec_arr / norms
        sim_matrix = normalized @ normalized.T  # cosine similarity

        # Single-linkage clustering
        threshold = 0.75
        n = len(episodes)
        parent = list(range(n))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        for i in range(n):
            for j in range(i + 1, n):
                if sim_matrix[i][j] >= threshold:
                    union(i, j)

        # Group by cluster root
        clusters: dict[int, list[int]] = {}
        for i in range(n):
            root = find(i)
            clusters.setdefault(root, []).append(i)

        merged_count = 0
        new_episode_ids: list[int] = []

        for root, members in clusters.items():
            if len(members) < 2:
                continue

            # Merge: concatenate summaries, union tags, average importance
            merged_summary = " | ".join(summaries[members[i]] for i in members)
            merged_tags: set[str] = set()
            total_importance = 0.0
            for idx in members:
                merged_tags.update(tag_lists[idx])
                total_importance += importances[idx]
            avg_importance = total_importance / len(members)

            # Store merged episode
            new_id = await self.store_episode(
                summary=f"[CONSOLIDATED] {merged_summary}",
                tags=list(merged_tags),
                importance=avg_importance,
            )
            new_episode_ids.append(new_id)

            # Delete originals from SQLite
            async with aiosqlite.connect(str(self._db_path)) as db:
                placeholders = ",".join("?" * len(members))
                orig_ids = [ids[mem] for mem in members]
                await db.execute(
                    f"DELETE FROM episodes WHERE id IN ({placeholders})",
                    orig_ids,
                )
                await db.commit()

            # Delete originals from ChromaDB
            try:
                collection = self._ensure_chroma()
                del_ids = [f"episode_{oid}" for oid in orig_ids]
                collection.delete(ids=del_ids)
            except Exception:
                logger.exception("ChromaDB delete failed during consolidation")

            merged_count += len(members)

        result = {
            "clusters_formed": len(clusters) - len([m for m in clusters.values() if len(m) < 2]),
            "episodes_merged": merged_count,
        }
        logger.info("consolidate completed: %s", result)
        return result

    # ── entity retrieval ─────────────────────────────────────────────────

    async def get_entities(
        self,
        query: str | None = None,
        top_k: int = _DEFAULT_TOP_K,
    ) -> list[Entity]:
        """Retrieve entities, optionally filtered by FTS5 match on name."""
        await self.initialize()

        async with aiosqlite.connect(str(self._db_path)) as db:
            if query:
                rows = await db.execute(
                    """
                    SELECT e.id, e.name, e.type, e.attributes, e.last_seen
                    FROM entities e
                    WHERE e.name LIKE ?
                    ORDER BY e.last_seen DESC
                    LIMIT ?
                    """,
                    (f"%{query}%", top_k),
                )
            else:
                rows = await db.execute(
                    "SELECT id, name, type, attributes, last_seen FROM entities ORDER BY last_seen DESC LIMIT ?",
                    (top_k,),
                )

            results: list[Entity] = []
            for row in await rows.fetchall():
                eid, name, etype, attr_json, last_seen = row
                results.append(Entity(
                    id=eid,
                    name=name,
                    entity_type=etype,
                    attributes=json.loads(attr_json),
                    last_seen=last_seen,
                ))
            return results

    # ── stats ────────────────────────────────────────────────────────────

    def stats(self) -> dict[str, Any]:
        """Return memory statistics (synchronous, opens its own connection)."""
        if not self._initialized:
            return {
                "episodes": 0,
                "facts": 0,
                "entities": 0,
                "chroma_entries": 0,
                "db_path": str(self._db_path),
            }

        import sqlite3  # noqa: PLC0415 — sync read for stats

        conn = sqlite3.connect(str(self._db_path))
        try:
            episodes = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
            facts = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
            entities = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        finally:
            conn.close()

        chroma_entries = 0
        try:
            collection = self._ensure_chroma()
            chroma_entries = collection.count()
        except Exception:
            pass

        return {
            "episodes": episodes,
            "facts": facts,
            "entities": entities,
            "chroma_entries": chroma_entries,
            "db_path": str(self._db_path),
        }

    # ── helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _fts_escape(query: str) -> str:
        """Escape special FTS5 characters in user query."""
        for ch in ('"', '*', '-', '(', ')', ':', 'AND', 'OR', 'NOT'):
            query = query.replace(ch, f'"{ch}"')
        return query
