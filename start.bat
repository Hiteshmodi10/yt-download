@echo off
echo Starting YouTube Downloader...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo Starting server on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
