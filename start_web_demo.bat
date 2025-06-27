@echo off
echo ============================================
echo  🌐 Starting Italian Medical NER Web Demo
echo  Nino Medical AI - Professional Platform
echo ============================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Starting Streamlit web demo...
echo.
echo 🌐 Web Demo will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the service
echo.

start http://localhost:8501

streamlit run web_demo_app.py --server.port=8501 --server.address=localhost

echo.
echo Web demo stopped.
pause
