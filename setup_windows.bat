@echo off
title AI Jira Test Agent - Windows Setup
cd /d "%~dp0"

echo ==========================================
echo       AI Jira Test Agent - Setup
echo ==========================================
echo.

where py >nul 2>&1
if %errorlevel%==0 (
    echo Creating Python virtual environment...
    py -3 -m venv .venv
) else (
    echo Creating Python virtual environment...
    python -m venv .venv
)

if errorlevel 1 goto failed

echo.
echo Installing project dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed

echo.
echo Installing Playwright Chromium...
".venv\Scripts\python.exe" -m playwright install chromium
if errorlevel 1 goto failed

echo.
echo ==========================================
echo SETUP COMPLETED SUCCESSFULLY
echo ==========================================
echo.
echo Next:
echo 1. Configure your Groq API key in .streamlit\secrets.toml
echo 2. Double-click launch_windows.bat to start the app.
echo.
pause
exit /b 0

:failed
echo.
echo SETUP FAILED. Please check the error messages above.
echo Refer to README.md for troubleshooting.
pause
exit /b 1
