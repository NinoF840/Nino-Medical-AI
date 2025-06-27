@echo off
echo ============================================
echo  Nino Medical AI - Docker Launch Script
echo  Professional Italian Medical NER Platform
echo ============================================
echo.

echo Checking Docker Desktop status...
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Desktop is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Docker Desktop is running ✓
echo.

echo Building and starting Nino Medical AI containers...
echo This may take a few minutes on first run...
echo.

docker-compose up --build -d

if errorlevel 1 (
    echo ERROR: Failed to start containers!
    pause
    exit /b 1
)

echo.
echo ============================================
echo  🚀 Nino Medical AI is now running!
echo ============================================
echo.
echo  📱 Streamlit Web Demo: http://localhost:8501
echo  🔗 FastAPI Service:    http://localhost:8000
echo  📖 API Documentation:  http://localhost:8000/docs
echo.
echo Press any key to view container status...
pause >nul

echo.
echo Container Status:
docker-compose ps

echo.
echo To stop the services, run: docker-compose down
echo To view logs, run: docker-compose logs -f
echo.
echo Opening Streamlit demo in your default browser...
start http://localhost:8501

echo.
echo Press any key to exit...
pause >nul
