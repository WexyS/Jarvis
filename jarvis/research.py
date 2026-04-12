"""Research assistant with web search and document RAG."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from jarvis.config import JarvisConfig
from jarvis.llm import LLMRouter

logger = logging.getLogger(__name__)


class WebSearcher:
    """Web search with citation support."""

    def __init__(self):
        self._session = None

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """Search the web and return results with URLs."""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            return [
                {
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", ""),
                }
                for r in results
            ]
        except ImportError:
            logger.warning("duckduckgo-search not installed. Install with: pip install duckduckgo-search")
            return []
        except Exception as e:
            logger.error("Web search failed: %s", e)
            return []

    def fetch_page_content(self, url: str, max_chars: int = 5000) -> Optional[str]:
        """Fetch and extract readable text from a webpage."""
        try:
            import httpx
            from bs4 import BeautifulSoup

            headers = {
                "User-Agent": "Mozilla/5.0 (Jarvis AI Assistant; +https://github.com/jarvis)"
            }
            response = httpx.get(url, follow_redirects=True, timeout=15, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            text = soup.get_text(separator="\n", strip=True)
            # Collapse multiple blank lines
            import re
            text = re.sub(r"\n{3,}", "\n\n", text)
            return text[:max_chars]
        except Exception as e:
            logger.warning("Failed to fetch %s: %s", url, e)
            return None


class DocumentIndexer:
    """RAG document indexing and retrieval with ChromaDB."""

    def __init__(self, config: JarvisConfig):
        self.config = config.documents
        self._db = None
        self._embeddings = None
        self._initialized = False

    def _init_db(self):
        if self._initialized:
            return

        try:
            import chromadb
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            persist_dir = self.config.persist_directory
            self._db = chromadb.PersistentClient(path=persist_dir)

            self._splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap,
                length_function=len,
            )
            self._initialized = True
            logger.info("ChromaDB initialized at %s", persist_dir)
        except ImportError:
            logger.warning("chromadb not installed. Install with: pip install chromadb")
        except Exception as e:
            logger.error("Failed to initialize ChromaDB: %s", e)

    def index_documents(self, paths: Optional[list[str]] = None) -> int:
        """Index documents from configured paths."""
        if not self.config.enabled:
            logger.info("Document indexing is disabled")
            return 0

        self._init_db()
        if not self._db:
            return 0

        doc_paths = paths or self.config.paths
        extensions = set(self.config.extensions)
        total = 0

        collection = self._db.get_or_create_collection("jarvis_documents")

        for path_str in doc_paths:
            path = Path(path_str)
            if not path.exists():
                logger.warning("Document path does not exist: %s", path)
                continue

            files = self._find_files(path, extensions)
            for file_path in files:
                try:
                    content = self._read_file(file_path)
                    if not content:
                        continue

                    chunks = self._splitter.split_text(content)
                    for i, chunk in enumerate(chunks):
                        doc_id = f"{file_path}:{i}"
                        collection.upsert(
                            documents=[chunk],
                            metadatas=[{
                                "source": str(file_path),
                                "chunk": i,
                                "total_chunks": len(chunks),
                            }],
                            ids=[doc_id],
                        )
                    total += len(chunks)
                    logger.info("Indexed %d chunks from %s", len(chunks), file_path)
                except Exception as e:
                    logger.warning("Failed to index %s: %s", file_path, e)

        logger.info("Total documents indexed: %d chunks", total)
        return total

    def query(self, question: str, n_results: int = 5) -> list[dict]:
        """Search indexed documents for relevant context."""
        self._init_db()
        if not self._db:
            return []

        collection = self._db.get_or_create_collection("jarvis_documents")
        results = collection.query(
            query_texts=[question],
            n_results=n_results,
        )

        documents = []
        for i, doc in enumerate(results.get("documents", [[]])[0]):
            metadata = results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {}
            documents.append({
                "content": doc,
                "source": metadata.get("source", "unknown"),
                "chunk": metadata.get("chunk", 0),
            })

        return documents

    @staticmethod
    def _find_files(path: Path, extensions: set[str]) -> list[Path]:
        """Find all matching files recursively."""
        if path.is_file() and path.suffix in extensions:
            return [path]
        if path.is_dir():
            return [f for f in path.rglob("*") if f.suffix in extensions and not f.name.startswith(".")]
        return []

    @staticmethod
    def _read_file(path: Path) -> Optional[str]:
        """Read document content from file."""
        try:
            if path.suffix == ".pdf":
                return DocumentIndexer._read_pdf(path)
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.warning("Failed to read %s: %s", path, e)
            return None

    @staticmethod
    def _read_pdf(path: Path) -> Optional[str]:
        """Extract text from PDF."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except ImportError:
            logger.warning("pypdf not installed for PDF reading. Install with: pip install pypdf")
            return None
        except Exception as e:
            logger.warning("PDF read failed: %s", e)
            return None


class ResearchAssistant:
    """Research assistant combining web search and document RAG."""

    def __init__(self, config: JarvisConfig, llm: LLMRouter):
        self.config = config
        self.llm = llm
        self.web_searcher = WebSearcher()
        self.doc_indexer = DocumentIndexer(config)

    async def research(self, question: str, use_documents: bool = True) -> str:
        """Research a question using web search and/or local documents."""
        context_parts = []
        citations = []

        # Search local documents if enabled
        if use_documents and self.config.documents.enabled:
            doc_results = self.doc_indexer.query(question, n_results=3)
            for doc in doc_results:
                context_parts.append(
                    f"From document: {doc['source']}\n{doc['content']}"
                )
                citations.append(doc["source"])

        # Web search
        web_results = self.web_searcher.search(question, max_results=5)
        if web_results:
            for r in web_results:
                context_parts.append(f"From web: {r['title']}\n{r['snippet']}")
                citations.append(r["url"])

            # Fetch top 2 pages for more context
            for result in web_results[:2]:
                content = self.web_searcher.fetch_page_content(result["url"], max_chars=3000)
                if content:
                    context_parts.append(f"From {result['title']} (full page):\n{content[:2000]}")

        if not context_parts:
            # Fall back to LLM knowledge
            return await self.llm.chat([
                {"role": "system", "content": "You are a research assistant. Answer questions thoroughly with citations if possible."},
                {"role": "user", "content": question},
            ])

        # Compose research prompt
        context = "\n\n---\n\n".join(context_parts)
        prompt = f"""You are a research assistant. Answer the following question based on the provided research material.

IMPORTANT:
- Cite your sources using [1], [2], etc. format
- If the information comes from web search, cite the URL
- If the information comes from local documents, cite the file path
- If you cannot find enough information, say so clearly

Question: {question}

Research material:
{context}

Provide a comprehensive, well-structured answer with citations."""

        messages = [
            {"role": "system", "content": "You are a thorough research assistant. Always cite sources."},
            {"role": "user", "content": prompt},
        ]

        return await self.llm.chat(messages)

    def index_documents(self, paths: Optional[list[str]] = None) -> int:
        """Trigger document indexing."""
        return self.doc_indexer.index_documents(paths)
