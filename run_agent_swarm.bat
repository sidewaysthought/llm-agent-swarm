@echo off

REM Check Python Installation
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is required but it's not installed. Aborting.
    exit /b
)

REM Check pip Installation
python -m pip --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo pip is required but it's not installed. Aborting.
    exit /b
)

REM Install dependencies
python -m pip install -r requirements.txt

REM Run Python Script
python -m main