@echo off
echo ====================================
echo Italian Medical NER - Build Script
echo Enhanced by NinoF840
echo ====================================
echo.

echo Installing required packages...
pip install cx_Freeze>=6.13.1

echo.
echo Checking Python and dependencies...
python --version
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
python -c "import numpy; print(f'NumPy: {numpy.__version__}')"

echo.
echo Building executable...
python setup_exe.py build

echo.
echo Copying executable to desktop...
if exist "build\exe.win-amd64-3.11\ItalianMedicalNER.exe" (
    copy "build\exe.win-amd64-3.11\ItalianMedicalNER.exe" "C:\Users\nino\Desktop\ItalianMedicalNER.exe"
    echo Executable copied to C:\Users\nino\Desktop\ItalianMedicalNER.exe
) else if exist "build\exe.win-amd64-3.12\ItalianMedicalNER.exe" (
    copy "build\exe.win-amd64-3.12\ItalianMedicalNER.exe" "C:\Users\nino\Desktop\ItalianMedicalNER.exe"
    echo Executable copied to C:\Users\nino\Desktop\ItalianMedicalNER.exe
) else (
    echo Looking for executable in build directory...
    dir build /s /b *.exe
    echo Please manually copy the executable to your desktop
)

echo.
echo Build process completed!
echo Check C:\Users\nino\Desktop for ItalianMedicalNER.exe
echo.
pause

