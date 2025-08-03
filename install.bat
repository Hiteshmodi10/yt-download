@echo off
echo Installing YouTube Downloader...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Error installing dependencies. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Installation complete!
echo.
echo To start the application, run: python app.py
echo Then open your browser to: http://localhost:5000
echo.
pause
