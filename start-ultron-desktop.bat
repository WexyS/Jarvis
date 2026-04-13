@echo off
setlocal enabledelayedexpansion
title Ultron v2.0 — Web GUI Launcher
color 0B
echo.
echo ============================================================
echo  Ultron v2.0 — Web GUI (React + FastAPI)
echo  Backend : http://127.0.0.1:8000
echo  Frontend: http://localhost:5173
echo ============================================================
echo.

cd /d "%~dp0"

:: [1/4] Sanal ortam
if exist "%~dp0.venv\Scripts\activate.bat" (
    call "%~dp0.venv\Scripts\activate.bat"
    echo [1/4] Virtual environment activated.
) else (
    echo [-] .venv bulunamadi. Once: python -m venv .venv
    pause & exit /b 1
)

:: [2/4] Backend baslat
:: BUG #1 DUZELTME: eksik kapanış tırnak eklendi
:: BUG #2 DUZELTME: --host 0.0.0.0 -> 127.0.0.1 (guvenlik)
:: BUG #4 DUZELTME: python -> .venv\Scripts\python.exe (PATH sorunu)
echo [2/4] Starting FastAPI Backend (port 8000)...
start "Ultron Backend" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && .venv\Scripts\python.exe -m uvicorn ultron.api.main:app --host 127.0.0.1 --port 8000"

:: [3/4] Health check
:: BUG #3 DUZELTME: kör timeout -> curl dongusu (race condition)
echo [3/4] Waiting for backend...
set RETRY=0
:HEALTH_LOOP
    timeout /t 2 /nobreak >nul
    curl -sf http://127.0.0.1:8000/health >nul 2>&1
    if !errorlevel! equ 0 goto BACKEND_OK
    set /a RETRY+=1
    echo     Bekleniyor... (!RETRY!/30)
    if !RETRY! lss 30 goto HEALTH_LOOP
    echo [-] Backend 60 saniyede baslamadi. Ultron Backend penceresini kontrol et.
    pause & exit /b 1
:BACKEND_OK
echo     Backend hazir.
echo.

:: [4/4] Frontend
echo [4/4] Starting React Frontend (port 5173)...
cd /d "%~dp0ultron-desktop"
call npm run dev

echo.
echo [-] Frontend durdu.
pause
