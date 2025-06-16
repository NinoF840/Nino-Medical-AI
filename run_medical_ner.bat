@echo off
REM Italian Medical NER GUI Launcher
REM This batch file runs the Italian Medical NER GUI application

echo Starting Italian Medical NER GUI...
echo Please wait while the application loads...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if the GUI script exists
if not exist "medical_ner_gui.py" (
    echo Error: medical_ner_gui.py not found
    echo Please make sure you're running this from the project directory
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
python -c "import transformers, torch, tkinter" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    pip install transformers torch tkinter
    if errorlevel 1 (
        echo Error installing dependencies
        pause
        exit /b 1
    )
)

REM Run the GUI application
echo Launching GUI...
python medical_ner_gui.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application closed with an error
    pause
)

