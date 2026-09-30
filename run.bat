@echo off
title PARIS Assistant
cd /d "%~dp0"
set PLAYWRIGHT_BROWSERS_PATH=E:\ms-playwright
set PYTHONIOENCODING=utf-8
:loop
echo Starting PARIS...
".venv\Scripts\python.exe" "main.py"
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% EQU 42 (
    echo.
    echo Paris requested a restart. Rebooting immediately...
    goto loop
)

if %EXIT_CODE% NEQ 0 (
    echo.
    echo Application crashed with error code %EXIT_CODE%. Restarting in 5 seconds...
    timeout /t 5
    goto loop
)

echo Paris shutdown gracefully.
pause
