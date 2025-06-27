@echo off
echo ============================================
echo  🔗 Starting Italian Medical NER API Service
echo  Nino Medical AI - Professional Platform
echo ============================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Starting FastAPI service...
echo.
echo 🔗 API Service: http://localhost:8000
echo 📖 API Documentation: http://localhost:8000/docs
echo 📝 API Redoc: http://localhost:8000/redoc
echo.
echo Press Ctrl+C to stop the service
echo.

start http://localhost:8000/docs

uvicorn api_service:app --host localhost --port 8000 --reload

echo.
echo API service stopped.
pause
