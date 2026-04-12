"""Coding assistant with file interaction and optional code execution."""

from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional

from jarvis.config import JarvisConfig
from jarvis.llm import LLMRouter

logger = logging.getLogger(__name__)


class FileManager:
    """Safe file read/write operations."""

    def __init__(self, config: JarvisConfig):
        self.config = config.coding
        self.work_dir = Path(self.config.work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self._allowed_extensions = set(self.config.allowed_read_extensions)

    def read_file(self, path: str) -> Optional[str]:
        """Read a file with safety checks."""
        file_path = self._resolve_path(path)
        if file_path is None:
            return None

        if not file_path.exists():
            return f"Error: File not found: {file_path}"

        if not file_path.is_file():
            return f"Error: Not a file: {file_path}"

        # Size limit (100KB)
        if file_path.stat().st_size > 100 * 1024:
            return f"Error: File too large ({file_path.stat().st_size} bytes). Max 100KB."

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            logger.info("Read %d bytes from %s", len(content), file_path)
            return content
        except Exception as e:
            return f"Error reading file: {e}"

    def write_file(self, path: str, content: str) -> str:
        """Write content to a file."""
        file_path = self._resolve_path(path)
        if file_path is None:
            return "Error: Invalid path"

        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            logger.info("Wrote %d bytes to %s", len(content), file_path)
            return f"Successfully wrote {len(content)} bytes to {file_path}"
        except Exception as e:
            return f"Error writing file: {e}"

    def list_directory(self, path: str = ".") -> Optional[str]:
        """List directory contents."""
        dir_path = self._resolve_path(path)
        if dir_path is None:
            return None

        try:
            items = []
            for item in sorted(dir_path.iterdir()):
                prefix = "📁" if item.is_dir() else "📄"
                items.append(f"  {prefix} {item.name}")
            return f"Contents of {dir_path}:\n" + "\n".join(items)
        except Exception as e:
            return f"Error listing directory: {e}"

    def _resolve_path(self, path: str) -> Optional[Path]:
        """Resolve a path safely, preventing directory traversal."""
        if not path:
            return None

        p = Path(path)

        # If absolute, check it's within work_dir
        if p.is_absolute():
            try:
                resolved = p.resolve()
                # Allow reading from anywhere for absolute paths, but writing to work_dir
                return resolved
            except Exception:
                return None

        # Relative path: resolve within work_dir
        resolved = (self.work_dir / p).resolve()
        return resolved

    def search_files(self, pattern: str, directory: str = ".") -> list[Path]:
        """Search for files matching a glob pattern."""
        dir_path = self._resolve_path(directory)
        if dir_path is None or not dir_path.exists():
            return []

        try:
            return list(dir_path.rglob(pattern))
        except Exception:
            return []


class CodeExecutor:
    """Execute code safely (when explicitly allowed)."""

    def __init__(self, config: JarvisConfig):
        self.config = config.coding
        self.work_dir = Path(self.config.work_dir)

    def execute(self, code: str, language: str = "python", timeout: int = 30) -> dict:
        """Execute code and return output."""
        if not self.config.allow_execution:
            return {
                "success": False,
                "output": "",
                "error": "Code execution is disabled. Set coding.allow_execution=true in config to enable.",
            }

        if language == "python":
            return self._execute_python(code, timeout)
        elif language == "bash" or language == "shell":
            return self._execute_shell(code, timeout)
        else:
            return {
                "success": False,
                "output": "",
                "error": f"Unsupported language: {language}. Supported: python, bash/shell",
            }

    def _execute_python(self, code: str, timeout: int) -> dict:
        """Execute Python code."""
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.work_dir),
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else "",
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Execution timed out after {timeout} seconds",
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Execution failed: {e}",
            }

    def _execute_shell(self, code: str, timeout: int) -> dict:
        """Execute shell code."""
        import os
        shell = os.environ.get("COMSPEC", "cmd.exe") if sys.platform == "win32" else "/bin/bash"
        try:
            result = subprocess.run(
                code,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.work_dir),
                executable=shell,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else "",
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": f"Execution timed out after {timeout} seconds",
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Execution failed: {e}",
            }


class CodingAssistant:
    """AI coding assistant with file access and code execution."""

    def __init__(self, config: JarvisConfig, llm: LLMRouter):
        self.config = config
        self.llm = llm
        self.file_manager = FileManager(config)
        self.code_executor = CodeExecutor(config)
        self._conversation_history: list[dict] = []

    async def help_with(self, task: str, files: Optional[list[str]] = None) -> str:
        """Help with a coding task, optionally reading files for context."""
        context = ""

        # Read relevant files for context
        if files:
            for file_path in files:
                content = self.file_manager.read_file(file_path)
                if content and not content.startswith("Error:"):
                    context += f"\n\n--- File: {file_path} ---\n{content}"

        prompt = f"""You are an expert software engineering assistant. Help with the following task:

{task}
{context}

Guidelines:
- Provide clear, well-commented code
- Explain your approach and reasoning
- Highlight any potential issues or edge cases
- Use modern best practices
- If file operations are needed, use the available tools

Available tools:
- read_file <path> - Read a file
- write_file <path> - Write content to a file
- list_directory [path] - List directory contents
- execute_python <code> - Run Python code
- execute_shell <code> - Run shell commands

Provide your answer in a structured format with code blocks where appropriate."""

        messages = [
            {"role": "system", "content": (
                "You are Jarvis, an expert coding assistant. "
                "You can read files, write code, and execute code when permitted. "
                "Always explain your reasoning and provide production-quality code."
            )},
            {"role": "user", "content": prompt},
        ]

        response = await self.llm.chat(messages)
        self._conversation_history = messages + [{"role": "assistant", "content": response}]
        return response

    async def chat(self, message: str) -> str:
        """Continue a coding conversation."""
        messages = self._conversation_history + [{"role": "user", "content": message}]
        response = await self.llm.chat(messages)
        self._conversation_history = messages + [{"role": "assistant", "content": response}]
        return response

    async def generate_and_run(self, description: str, language: str = "python") -> str:
        """Generate code and optionally execute it."""
        messages = [
            {"role": "system", "content": (
                "You are a coding assistant. Generate clean, working code for the described task. "
                f"Language: {language}. Include comments explaining the code."
            )},
            {"role": "user", "content": description},
        ]

        code_response = await self.llm.chat(messages)

        # Extract code from response
        code = self._extract_code(code_response, language)

        result = f"Generated code:\n\n{code_response}"

        if code and self.config.coding.allow_execution:
            exec_result = self.code_executor.execute(code, language)
            if exec_result["success"]:
                result += f"\n\n✅ Execution output:\n{exec_result['output']}"
            else:
                result += f"\n\n❌ Execution failed:\n{exec_result['error']}"
        elif code:
            result += "\n\n(Code execution disabled - set coding.allow_execution=true to enable)"

        return result

    @staticmethod
    def _extract_code(response: str, language: str) -> Optional[str]:
        """Extract code block from markdown response."""
        import re
        # Match ```language ... ``` blocks
        pattern = rf"```{language}\n(.*?)```"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Fallback: match any code block
        pattern = r"```(?:\w*)\n(.*?)```"
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1).strip()

        return None

    def reset(self) -> None:
        """Clear conversation history."""
        self._conversation_history = []
