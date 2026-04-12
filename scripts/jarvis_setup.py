#!/usr/bin/env python3
"""Setup script for Jarvis - checks dependencies and initializes the project."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def print_step(num: int, total: int, title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  Step {num}/{total}: {title}")
    print(f"{'='*60}")


def check_python_version() -> bool:
    """Check Python version."""
    if sys.version_info < (3, 10):
        print(f"❌ Python 3.10+ required. You have {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]}")
    return True


def check_ollama() -> bool:
    """Check if Ollama is installed and running."""
    ollama = shutil.which("ollama")
    if not ollama:
        print("⚠️  Ollama not found in PATH")
        print("   Install from: https://ollama.ai")
        return False

    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("✅ Ollama is installed and running")
            # Check for recommended models
            output = result.stdout.lower()
            recommended = ["qwen3.5", "llama3", "mistral", "phi3", "llama3.1", "llama3.2"]
            found = [m for m in recommended if m in output]
            if found:
                print(f"   Found models: {', '.join(found)}")
            else:
                print("   ⚠️  No recommended models found")
                print("   Run: ollama pull qwen3.5:27b")
            return True
        else:
            print("⚠️  Ollama server not running")
            print("   Run: ollama serve")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Ollama command timed out")
        return False
    except Exception as e:
        print(f"⚠️  Ollama check failed: {e}")
        return False


def install_dependencies() -> bool:
    """Install Python dependencies."""
    print("\nInstalling Python dependencies...")

    # Try uv first, fall back to pip
    if shutil.which("uv"):
        print("Using uv (fast)...")
        result = subprocess.run(["uv", "sync"], capture_output=True, text=True)
    else:
        print("Using pip...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            capture_output=True, text=True
        )

    if result.returncode == 0:
        print("✅ Dependencies installed")
        return True
    else:
        print("❌ Failed to install dependencies")
        print(result.stderr)
        return False


def setup_config() -> None:
    """Create config file from template."""
    config_path = Path("config.yaml")
    if config_path.exists():
        print("✅ config.yaml already exists")
        return

    template = Path("config.template.yaml")
    if template.exists():
        shutil.copy("config.template.yaml", "config.yaml")
        print("✅ config.yaml created from template")
    else:
        print("⚠️  config.template.yaml not found")


def setup_env() -> None:
    """Create .env file from template."""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env already exists")
        return

    template = Path(".env.example")
    if template.exists():
        shutil.copy(".env.example", ".env")
        print("✅ .env created from template")


def create_directories() -> None:
    """Create required directories."""
    dirs = ["data", "documents", "notes", "workspace", "data/chroma_db"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print(f"✅ Created {len(dirs)} directories")


def setup_sample_documents() -> None:
    """Create sample documents for testing."""
    docs_dir = Path("documents")
    if docs_dir.exists():
        sample = docs_dir / "sample_notes.md"
        if not sample.exists():
            sample.write_text(
                "# Sample Notes\n\n"
                "These are sample notes for testing the document RAG system.\n\n"
                "## Project Ideas\n"
                "- Build a personal AI assistant\n"
                "- Create a home automation system\n"
                "- Learn Rust programming\n\n"
                "## Meeting Notes\n"
                "- Discussed Q4 roadmap\n"
                "- Priority: improve API performance\n"
            )
            print("✅ Created sample notes document")


def main() -> None:
    """Run setup."""
    print("\n" + "=" * 60)
    print("  Jarvis Personal AI Assistant - Setup")
    print("=" * 60)

    step = 0
    total = 7

    # Step 1: Python version
    step += 1
    print_step(step, total, "Checking Python version")
    if not check_python_version():
        sys.exit(1)

    # Step 2: Check Ollama
    step += 1
    print_step(step, total, "Checking Ollama")
    has_ollama = check_ollama()

    # Step 3: Install deps
    step += 1
    print_step(step, total, "Installing dependencies")
    install_dependencies()

    # Step 4: Config
    step += 1
    print_step(step, total, "Setting up configuration")
    setup_config()
    setup_env()

    # Step 5: Directories
    step += 1
    print_step(step, total, "Creating directories")
    create_directories()

    # Step 6: Sample docs
    step += 1
    print_step(step, total, "Adding sample documents")
    setup_sample_documents()

    # Step 7: Summary
    step += 1
    print_step(step, total, "Summary")

    print("""
🎉 Setup complete! Next steps:

1. Edit config.yaml to customize settings
2. If using Ollama: ollama pull qwen3.5:27b
3. If using OpenAI: Set OPENAI_API_KEY in .env
4. Optional: Add email credentials for briefing
5. Run: jarvis

Modes:
  jarvis              # Interactive chat (default)
  jarvis --mode briefing    # Morning briefing
  jarvis --mode research    # Research assistant
  jarvis --mode coding      # Coding assistant
""")


if __name__ == "__main__":
    main()
