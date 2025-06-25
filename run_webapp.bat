@echo off
echo 🏥 Starting Italian Medical NER Web Application...
echo.
echo Installing dependencies...
pip install -r webapp_requirements.txt
echo.
echo 🚀 Launching Streamlit Web App...
echo.
echo 📱 The app will open in your browser at: http://localhost:8501
echo.
streamlit run medical_ner_webapp.py
pause

