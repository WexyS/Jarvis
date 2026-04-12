@echo off
title J.A.R.V.I.S v2.1 — CLI Launcher
color 0A
echo.
echo ============================================================
echo  J.A.R.V.I.S v2.1 — Personal AI Assistant (CLI)
echo  Multi-Agent | Self-Healing | 13 AI Providers | Voice
echo ============================================================
echo.

:: Set working directory to script location
cd /d "%~dp0"

:: Activate virtual environment
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
    echo [1/4] Virtual environment activated.
) else (
    echo [-] Virtual environment not found: .venv
    echo     Create one: python -m venv .venv ^&^& .venv\Scripts\pip install -e .
    pause
    exit /b 1
)

:: Check Ollama
echo [2/4] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Ollama is not running. Some features may not work.
    echo     Start Ollama: ollama serve
    echo     Pull model: ollama pull qwen2.5:14b
) else (
    echo      Ollama is running.
)

:: Check model
echo [3/4] Checking model (qwen2.5:14b)...
ollama list 2>&1 | findstr "qwen2.5:14b" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Model not found. Downloading qwen2.5:14b...
    ollama pull qwen2.5:14b
) else (
    echo      Model ready.
)

:: Launch CLI
echo [4/4] Starting Jarvis CLI...
echo.
python -m jarvis.cli --cli
echo.
pause
