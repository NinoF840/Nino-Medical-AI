@echo off
REM Nino Medical AI - Italian Medical NER API Server Startup Script
REM Professional Medical AI Platform for Italian Healthcare
REM Copyright (C) 2025 Nino Medical AI. All Rights Reserved.

echo ====================================================
echo   🇮🇹 Nino Medical AI - Italian Medical NER
echo   Professional Medical AI Platform for Healthcare
echo   © 2025 Nino Medical AI - Built by NinoF840
echo ====================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update requirements
echo 📥 Installing/updating dependencies...
pip install -r api_requirements.txt
if errorlevel 1 (
    echo ⚠️  WARNING: Some dependencies might have failed to install
    echo The API might still work, continuing...
)

REM Check if model files exist
if not exist "improved_inference.py" (
    echo ❌ ERROR: improved_inference.py not found
    echo Please ensure all model files are in the current directory
    pause
    exit /b 1
)

if not exist "pytorch_model.bin" (
    echo ❌ ERROR: Model weights not found
    echo Please ensure pytorch_model.bin is in the current directory
    pause
    exit /b 1
)

echo ✅ Model files found
echo.
echo 🚀 Starting Italian Medical NER API Server...
echo 📊 Server will be available at: http://localhost:8000
echo 📖 API Documentation: http://localhost:8000/docs
echo 🌐 Web Demo: Open demo_web.html in your browser
echo.
echo Press Ctrl+C to stop the server
echo ====================================================
echo.

REM Start the API server
python api_service.py

REM If we get here, the server stopped
echo.
echo 🛑 API Server stopped
pause

