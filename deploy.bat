@echo off
setlocal enabledelayedexpansion

echo ============================================
echo  🚀 Nino Medical AI - Advanced Deployment
echo  Professional Italian Medical NER Platform
echo ============================================
echo.

:main_menu
echo Choose deployment option:
echo.
echo 1. 🏠 Local Development (Quick Start)
echo 2. 🐳 Docker Development 
echo 3. 🌐 Docker Production (with monitoring)
echo 4. ☁️  Cloud Deployment (AWS/Azure/GCP)
echo 5. 🔧 System Check & Prerequisites
echo 6. 📊 View Deployment Status
echo 7. 🛑 Stop All Services
echo 8. 🗑️  Clean & Reset
echo 9. 📖 Help & Documentation
echo 0. Exit
echo.
set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto local_dev
if "%choice%"=="2" goto docker_dev
if "%choice%"=="3" goto docker_prod
if "%choice%"=="4" goto cloud_deploy
if "%choice%"=="5" goto system_check
if "%choice%"=="6" goto deployment_status
if "%choice%"=="7" goto stop_services
if "%choice%"=="8" goto clean_reset
if "%choice%"=="9" goto help_docs
if "%choice%"=="0" goto exit
goto main_menu

:local_dev
echo.
echo ============================================
echo  🏠 Local Development Deployment
echo ============================================
echo.

echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    echo Visit: https://python.org/downloads/
    pause
    goto main_menu
)

echo ✅ Python found
echo.

echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment exists
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
pip install -r web_demo_requirements.txt
pip install -r api_requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies!
    pause
    goto main_menu
)

echo ✅ Dependencies installed successfully
echo.

echo Choose local service to start:
echo 1. Streamlit Web Demo (Port 8501)
echo 2. FastAPI Service (Port 8000)
echo 3. Both Services
echo.
set /p local_choice="Enter choice (1-3): "

if "%local_choice%"=="1" (
    echo Starting Streamlit Web Demo...
    echo 🌐 Opening http://localhost:8501
    start http://localhost:8501
    streamlit run web_demo_app.py --server.port=8501
) else if "%local_choice%"=="2" (
    echo Starting FastAPI Service...
    echo 🌐 API Documentation: http://localhost:8000/docs
    start http://localhost:8000/docs
    python api_service.py
) else if "%local_choice%"=="3" (
    echo Starting both services...
    start /B streamlit run web_demo_app.py --server.port=8501
    start http://localhost:8501
    timeout /t 3 /nobreak >nul
    start http://localhost:8000/docs
    python api_service.py
)

pause
goto main_menu

:docker_dev
echo.
echo ============================================
echo  🐳 Docker Development Deployment
echo ============================================
echo.

echo Checking Docker Desktop...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Desktop is not running!
    echo Please start Docker Desktop and try again.
    pause
    goto main_menu
)

echo ✅ Docker Desktop is running
echo.

echo Building and starting development containers...
docker-compose up --build -d

if errorlevel 1 (
    echo ❌ Failed to start containers!
    pause
    goto main_menu
)

echo.
echo ✅ Development containers started successfully!
echo.
echo 📱 Streamlit Web Demo: http://localhost:8501
echo 🔗 FastAPI Service:    http://localhost:8000
echo 📖 API Documentation:  http://localhost:8000/docs
echo.

echo Opening services in browser...
start http://localhost:8501
timeout /t 2 /nobreak >nul
start http://localhost:8000/docs

echo.
echo Container Status:
docker-compose ps

pause
goto main_menu

:docker_prod
echo.
echo ============================================
echo  🌐 Docker Production Deployment
echo ============================================
echo.

echo ⚠️  PRODUCTION DEPLOYMENT CHECKLIST:
echo.
echo ✓ Update domain names in docker-compose.production.yml
echo ✓ Change default passwords
echo ✓ Configure SSL certificates
echo ✓ Review resource limits
echo ✓ Set environment variables
echo.
set /p prod_confirm="Continue with production deployment? (y/n): "

if /i not "%prod_confirm%"=="y" goto main_menu

echo.
echo Checking system resources...
docker system df

echo.
echo Starting production deployment...
docker-compose -f docker-compose.production.yml up --build -d

if errorlevel 1 (
    echo ❌ Production deployment failed!
    pause
    goto main_menu
)

echo.
echo ✅ Production deployment successful!
echo.
echo 🌐 Web Application: http://localhost (or your domain)
echo 🔗 API Service: http://localhost:8000 (or api.your-domain.com)
echo 📊 Traefik Dashboard: http://localhost:8080
echo 📈 Grafana Dashboard: http://localhost:3000
echo 🔍 Prometheus: http://localhost:9090
echo.

echo Production Services Status:
docker-compose -f docker-compose.production.yml ps

pause
goto main_menu

:cloud_deploy
echo.
echo ============================================
echo  ☁️  Cloud Deployment Options
echo ============================================
echo.

echo Select cloud provider:
echo.
echo 1. 🟠 AWS (Elastic Beanstalk / ECS)
echo 2. 🔵 Microsoft Azure (Container Instances)
echo 3. 🟡 Google Cloud Platform (Cloud Run)
echo 4. 🔴 DigitalOcean (App Platform)
echo 5. 🟣 Railway (Simple deployment)
echo 6. 🔵 Streamlit Cloud (Free tier)
echo.
set /p cloud_choice="Enter choice (1-6): "

if "%cloud_choice%"=="1" goto aws_deploy
if "%cloud_choice%"=="2" goto azure_deploy
if "%cloud_choice%"=="3" goto gcp_deploy
if "%cloud_choice%"=="4" goto digitalocean_deploy
if "%cloud_choice%"=="5" goto railway_deploy
if "%cloud_choice%"=="6" goto streamlit_cloud_deploy

goto main_menu

:aws_deploy
echo.
echo 🟠 AWS Deployment Instructions:
echo.
echo 1. Install AWS CLI: aws configure
echo 2. Install EB CLI: pip install awsebcli
echo 3. Initialize: eb init
echo 4. Deploy: eb create nino-medical-ner
echo.
echo Creating AWS deployment files...

if not exist "aws" mkdir aws

echo version: 1 > aws\Dockerrun.aws.json
echo { >> aws\Dockerrun.aws.json
echo   "AWSEBDockerrunVersion": "1", >> aws\Dockerrun.aws.json
echo   "Image": { >> aws\Dockerrun.aws.json
echo     "Name": "nino-medical-ner", >> aws\Dockerrun.aws.json
echo     "Update": "true" >> aws\Dockerrun.aws.json
echo   }, >> aws\Dockerrun.aws.json
echo   "Ports": [ >> aws\Dockerrun.aws.json
echo     { >> aws\Dockerrun.aws.json
echo       "ContainerPort": "8501" >> aws\Dockerrun.aws.json
echo     } >> aws\Dockerrun.aws.json
echo   ] >> aws\Dockerrun.aws.json
echo } >> aws\Dockerrun.aws.json

echo ✅ AWS files created in ./aws/ directory
pause
goto main_menu

:azure_deploy
echo.
echo 🔵 Azure Deployment Instructions:
echo.
echo 1. Install Azure CLI: az login
echo 2. Create resource group: az group create
echo 3. Deploy container: az container create
echo.
echo Creating Azure deployment script...

echo @echo off > azure_deploy.bat
echo az group create --name nino-medical-rg --location eastus >> azure_deploy.bat
echo az container create ^^ >> azure_deploy.bat
echo   --resource-group nino-medical-rg ^^ >> azure_deploy.bat
echo   --name nino-medical-ner ^^ >> azure_deploy.bat
echo   --image nino-medical-ner:latest ^^ >> azure_deploy.bat
echo   --cpu 2 --memory 4 ^^ >> azure_deploy.bat
echo   --ports 8501 8000 ^^ >> azure_deploy.bat
echo   --dns-name-label nino-medical-ai >> azure_deploy.bat

echo ✅ Azure deployment script created: azure_deploy.bat
pause
goto main_menu

:gcp_deploy
echo.
echo 🟡 Google Cloud Platform Deployment:
echo.
echo 1. Install gcloud CLI and authenticate
echo 2. Enable Cloud Run API
echo 3. Deploy with: gcloud run deploy
echo.
echo Creating GCP deployment files...

if not exist "gcp" mkdir gcp

echo steps: > gcp\cloudbuild.yaml
echo - name: 'gcr.io/cloud-builders/docker' >> gcp\cloudbuild.yaml
echo   args: ['build', '-t', 'gcr.io/$PROJECT_ID/nino-medical-ner', '.'] >> gcp\cloudbuild.yaml
echo - name: 'gcr.io/cloud-builders/docker' >> gcp\cloudbuild.yaml
echo   args: ['push', 'gcr.io/$PROJECT_ID/nino-medical-ner'] >> gcp\cloudbuild.yaml
echo - name: 'gcr.io/cloud-builders/gcloud' >> gcp\cloudbuild.yaml
echo   args: ['run', 'deploy', 'nino-medical-ner', '--image', 'gcr.io/$PROJECT_ID/nino-medical-ner', '--platform', 'managed', '--region', 'us-central1', '--allow-unauthenticated'] >> gcp\cloudbuild.yaml

echo ✅ GCP files created in ./gcp/ directory
pause
goto main_menu

:streamlit_cloud_deploy
echo.
echo 🔵 Streamlit Cloud Deployment (FREE):
echo.
echo 1. Push your code to GitHub
echo 2. Visit https://share.streamlit.io
echo 3. Connect your GitHub repo
echo 4. Set main file: web_demo_app.py
echo 5. Deploy automatically!
echo.
echo Creating streamlit config...

if not exist ".streamlit" mkdir .streamlit

echo [general] > .streamlit\config.toml
echo dataFrameSerialization = "legacy" >> .streamlit\config.toml
echo [server] >> .streamlit\config.toml
echo headless = true >> .streamlit\config.toml
echo enableCORS = false >> .streamlit\config.toml
echo enableXsrfProtection = true >> .streamlit\config.toml

echo ✅ Streamlit config created
echo 🌐 Visit: https://share.streamlit.io to deploy
pause
goto main_menu

:system_check
echo.
echo ============================================
echo  🔧 System Check & Prerequisites
echo ============================================
echo.

echo Checking system requirements...
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python: Not installed
    echo    Install from: https://python.org/downloads/
) else (
    for /f "tokens=2" %%a in ('python --version 2^>^&1') do echo ✅ Python: %%a
)

:: Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker: Not installed
    echo    Install from: https://docker.com/products/docker-desktop
) else (
    for /f "tokens=3" %%a in ('docker --version 2^>^&1') do echo ✅ Docker: %%a
)

:: Check Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose: Not available
) else (
    for /f "tokens=3" %%a in ('docker-compose --version 2^>^&1') do echo ✅ Docker Compose: %%a
)

:: Check Git
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git: Not installed
    echo    Install from: https://git-scm.com/downloads
) else (
    for /f "tokens=3" %%a in ('git --version 2^>^&1') do echo ✅ Git: %%a
)

:: Check disk space
echo.
echo 💾 Disk Space Check:
for /f "tokens=3" %%a in ('dir /-c 2^>nul ^| find "bytes free"') do echo Available: %%a bytes

:: Check memory
echo.
echo 🧠 System Memory:
wmic computersystem get TotalPhysicalMemory /value | find "TotalPhysicalMemory"

pause
goto main_menu

:deployment_status
echo.
echo ============================================
echo  📊 Deployment Status
echo ============================================
echo.

echo Checking running services...
echo.

:: Check local processes
echo 🏠 Local Services:
netstat -an | find ":8501" >nul 2>&1
if not errorlevel 1 (
    echo ✅ Streamlit running on port 8501
) else (
    echo ❌ Streamlit not running
)

netstat -an | find ":8000" >nul 2>&1
if not errorlevel 1 (
    echo ✅ API service running on port 8000
) else (
    echo ❌ API service not running
)

echo.

:: Check Docker containers
echo 🐳 Docker Containers:
docker ps 2>nul
if errorlevel 1 (
    echo ❌ Docker not running or no containers
) else (
    echo ✅ Docker containers listed above
)

echo.

:: Check system resources
echo 📊 System Resources:
echo CPU Usage:
wmic cpu get loadpercentage /value | find "LoadPercentage"

pause
goto main_menu

:stop_services
echo.
echo ============================================
echo  🛑 Stopping All Services
echo ============================================
echo.

echo Stopping local processes...
taskkill /f /im streamlit.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
echo ✅ Local processes stopped

echo.
echo Stopping Docker containers...
docker-compose down >nul 2>&1
docker-compose -f docker-compose.production.yml down >nul 2>&1
echo ✅ Docker containers stopped

echo.
echo 🛑 All services stopped successfully!
pause
goto main_menu

:clean_reset
echo.
echo ============================================
echo  🗑️  Clean & Reset Environment
echo ============================================
echo.

echo ⚠️  This will remove:
echo   - Docker containers and images
echo   - Virtual environment
echo   - Log files
echo   - Temporary files
echo.
set /p clean_confirm="Are you sure? This cannot be undone! (y/n): "

if /i not "%clean_confirm%"=="y" goto main_menu

echo.
echo Cleaning Docker environment...
docker-compose down --volumes --remove-orphans >nul 2>&1
docker-compose -f docker-compose.production.yml down --volumes --remove-orphans >nul 2>&1
docker system prune -f >nul 2>&1
echo ✅ Docker cleaned

echo.
echo Removing virtual environment...
if exist "venv" rmdir /s /q venv
echo ✅ Virtual environment removed

echo.
echo Cleaning logs and temporary files...
if exist "logs" rmdir /s /q logs
if exist "__pycache__" rmdir /s /q __pycache__
if exist ".pytest_cache" rmdir /s /q .pytest_cache
echo ✅ Temporary files cleaned

echo.
echo 🗑️  Environment reset complete!
pause
goto main_menu

:help_docs
echo.
echo ============================================
echo  📖 Help & Documentation
echo ============================================
echo.

echo Available Documentation:
echo.
echo 📖 README.md - Project overview and quick start
echo 📖 USER_GUIDE.md - Comprehensive user guide
echo 📖 DEPLOYMENT_INSTRUCTIONS.md - Detailed deployment guide
echo.
echo Online Resources:
echo 🌐 Live Demo: https://italian-medical-ai-4opjehvsybqncwjnaaq8a4.streamlit.app/
echo 🐛 Issues: GitHub Issues
echo 💼 Contact: medical-ner@yourdomain.com
echo.
echo Troubleshooting:
echo 1. Check system requirements (Option 5)
echo 2. View deployment status (Option 6)
echo 3. Reset environment if needed (Option 8)
echo.

pause
goto main_menu

:exit
echo.
echo ============================================
echo  👋 Thank you for using Nino Medical AI!
echo ============================================
echo.
echo Professional Italian Medical NER Platform
echo © 2025 Nino Medical AI. All Rights Reserved.
echo.
pause
exit /b 0
