@echo off
title PARIS Assistant
cd /d "%~dp0"
set PLAYWRIGHT_BROWSERS_PATH=E:\ms-playwright
set PYTHONIOENCODING=utf-8
echo Starting PARIS...
".venv\Scripts\python.exe" "main.py"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code %ERRORLEVEL%.
    pause
)
