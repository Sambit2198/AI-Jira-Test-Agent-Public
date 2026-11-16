@echo off
title AI Jira Test Agent
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Setup not completed. Please run setup_windows.bat first.
    pause
    exit /b 1
)

if not exist ".streamlit\secrets.toml" (
    echo Groq API key configuration is missing.
    echo Please create .streamlit\secrets.toml using the README instructions.
    pause
    exit /b 1
)

echo Starting AI Jira Test Agent...
echo Your browser should open automatically.
echo Keep this window open while using the application.
echo.

".venv\Scripts\python.exe" -m streamlit run app.py

echo.
echo AI Jira Test Agent has stopped.
pause
