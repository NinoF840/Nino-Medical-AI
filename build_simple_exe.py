#!/usr/bin/env python3
"""
Simplified Executable Builder for Italian Medical NER GUI

This script creates a simplified build using PyInstaller instead of cx_Freeze
to avoid recursion issues with complex dependencies like PyTorch.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully")

def create_spec_file():
    """Create a PyInstaller spec file for better control"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['medical_ner_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('italian_medical_dict.json', '.'),
        ('medical_patterns.json', '.'),
    ],
    hiddenimports=[
        'transformers',
        'torch',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'json',
        're',
        'threading',
        'pathlib',
        'collections',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'numpy.distutils',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ItalianMedicalNER',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
'''
    
    with open('medical_ner.spec', 'w') as f:
        f.write(spec_content)
    print("Created PyInstaller spec file: medical_ner.spec")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    
    # Create the spec file
    create_spec_file()
    
    try:
        # Build using the spec file
        cmd = [sys.executable, "-m", "PyInstaller", "medical_ner.spec", "--clean"]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Build completed successfully!")
            
            # Check if the executable was created
            exe_path = Path("dist/ItalianMedicalNER.exe")
            if exe_path.exists():
                print(f"Executable created: {exe_path.absolute()}")
                
                # Copy to desktop
                desktop = Path.home() / "Desktop"
                if desktop.exists():
                    shutil.copy2(exe_path, desktop / "ItalianMedicalNER.exe")
                    print(f"Executable copied to desktop: {desktop / 'ItalianMedicalNER.exe'}")
                
                return True
            else:
                print("Warning: Executable file not found in expected location")
                return False
        else:
            print(f"Build failed with return code: {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during build: {e}")
        return False

def simple_build():
    """Simple one-line build without spec file"""
    print("Attempting simple PyInstaller build...")
    
    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name=ItalianMedicalNER",
            "--add-data=italian_medical_dict.json;.",
            "--add-data=medical_patterns.json;.",
            "--hidden-import=transformers",
            "--hidden-import=torch",
            "--hidden-import=tkinter",
            "medical_ner_gui.py"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Simple build completed successfully!")
            
            # Check if the executable was created
            exe_path = Path("dist/ItalianMedicalNER.exe")
            if exe_path.exists():
                print(f"Executable created: {exe_path.absolute()}")
                
                # Copy to desktop
                desktop = Path.home() / "Desktop"
                if desktop.exists():
                    shutil.copy2(exe_path, desktop / "ItalianMedicalNER.exe")
                    print(f"Executable copied to desktop: {desktop / 'ItalianMedicalNER.exe'}")
                
                return True
            else:
                print("Warning: Executable file not found in expected location")
                return False
        else:
            print(f"Simple build failed with return code: {result.returncode}")
            print(f"Error output: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"Error during simple build: {e}")
        return False

def main():
    """Main build function"""
    print("Italian Medical NER - Simplified Executable Builder")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("medical_ner_gui.py").exists():
        print("Error: medical_ner_gui.py not found in current directory")
        print("Please run this script from the project directory")
        return False
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Try simple build first
    print("\nAttempting simple build...")
    if simple_build():
        print("\n✅ Build completed successfully!")
        return True
    
    # If simple build fails, try with spec file
    print("\nSimple build failed, trying with spec file...")
    if build_executable():
        print("\n✅ Build completed successfully with spec file!")
        return True
    
    print("\n❌ Both build methods failed.")
    print("This might be due to the complexity of the PyTorch dependencies.")
    print("\nAlternative suggestions:")
    print("1. Use the Python script directly: python medical_ner_gui.py")
    print("2. Create a batch file to run the script")
    print("3. Use a virtual environment with all dependencies")
    
    return False

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)

