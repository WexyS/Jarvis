"""Configuration management for Ultron."""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    ollama_model: str = "qwen2.5:14b"
    ollama_base_url: str = "http://localhost:11434"
    max_tokens: int = 4096
    temperature: float = 0.7
    language: str = "tr"
    openai_api_key: str = ""


class TTSConfig(BaseModel):
    enabled: bool = True
    engine: str = "auto"  # auto = openai > edge-tts > pyttsx3
    voice: str = "tr-TR-AhmetNeural"  # edge-tts için
    openai_voice: str = "onyx"  # OpenAI TTS için


class BriefingConfig(BaseModel):
    enabled: bool = True
    time: str = "08:00"
    include_news: bool = True
    news_sources: list[str] = Field(default_factory=lambda: [
        "https://news.ycombinator.com/rss",
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
    ])
    news_count: int = 5


class EmailConfig(BaseModel):
    provider: str = "imap"
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993
    imap_username: str = ""
    imap_password: str = ""
    gmail_credentials_file: str = ""
    max_emails: int = 10


class CalendarConfig(BaseModel):
    enabled: bool = False
    provider: str = "google"
    google_credentials_file: str = ""
    hours_ahead: int = 24


class DocumentsConfig(BaseModel):
    enabled: bool = True
    paths: list[str] = Field(default_factory=lambda: ["./documents", "./notes"])
    extensions: list[str] = Field(default_factory=lambda: [".txt", ".md", ".pdf", ".docx"])
    persist_directory: str = "./data/chroma_db"
    chunk_size: int = 1000
    chunk_overlap: int = 200


class CodingConfig(BaseModel):
    enabled: bool = True
    allow_execution: bool = False
    work_dir: str = "./workspace"
    allowed_read_extensions: list[str] = Field(default_factory=lambda: [
        ".py", ".js", ".ts", ".jsx", ".tsx", ".md", ".txt",
        ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini",
        ".html", ".css", ".sql", ".sh", ".bat",
    ])


class LoggingConfig(BaseModel):
    level: str = "INFO"
    file: str = "./data/ultron.log"


class MemoryConfig(BaseModel):
    enabled: bool = True
    # Response cache settings
    cache_size: int = 500
    cache_ttl_hours: int = 48
    cache_similarity: float = 0.80
    # Persistence directory
    persist_dir: str = "./data/memory"
    # Self-learning
    auto_learn: bool = True
    learn_batch_size: int = 5
    # Voice STT model
    whisper_model: str = "base"  # tiny, base, small, medium, large


class UltronConfig(BaseModel):
    model: ModelConfig = Field(default_factory=ModelConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    briefing: BriefingConfig = Field(default_factory=BriefingConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    calendar: CalendarConfig = Field(default_factory=CalendarConfig)
    documents: DocumentsConfig = Field(default_factory=DocumentsConfig)
    coding: CodingConfig = Field(default_factory=CodingConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)


def load_config(config_path: Optional[str] = None) -> UltronConfig:
    """Load configuration from YAML file, with env var overrides."""
    if config_path is None:
        # Look for config.yaml in common locations
        candidates = [
            Path("config") / "config.yaml",
            Path("config.yaml"),
            Path.home() / ".ultron" / "config.yaml",
            Path(__file__).parent.parent / "config" / "config.yaml",
            Path(__file__).parent.parent / "config.yaml",
        ]
        for candidate in candidates:
            if candidate.exists():
                config_path = str(candidate)
                break

    data = {}
    if config_path and Path(config_path).exists():
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

    # Override sensitive fields with environment variables
    model_cfg = data.get("model", {})
    if os.environ.get("OPENAI_API_KEY"):
        model_cfg["openai_api_key"] = os.environ["OPENAI_API_KEY"]

    email_cfg = data.get("email", {})
    if os.environ.get("ULTRON_EMAIL_USER"):
        email_cfg["imap_username"] = os.environ["ULTRON_EMAIL_USER"]
    if os.environ.get("ULTRON_EMAIL_PASS"):
        email_cfg["imap_password"] = os.environ["ULTRON_EMAIL_PASS"]

    # Merge back
    data["model"] = model_cfg
    data["email"] = email_cfg

    return UltronConfig(**data)


def ensure_directories(config: UltronConfig) -> None:
    """Ensure all configured directories exist."""
    dirs = [
        "./data",
        config.documents.persist_directory,
        config.coding.work_dir,
        config.memory.persist_dir,
    ]
    for path in config.documents.paths:
        dirs.append(path)

    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
