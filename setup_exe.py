#!/usr/bin/env python3
"""
Setup script for creating Italian Medical NER executable
Created by: NinoF840
"""

import cx_Freeze
import sys
import os
from pathlib import Path

# Application details
name = "Italian Medical NER - Enhanced"
version = "1.0.0"
description = "Enhanced Italian Medical NER with +8% recall improvement by NinoF840"
author = "NinoF840"

# Build options
build_exe_options = {
    "packages": [
        "tkinter", "threading", "json", "datetime", "os", "sys", "re",
        "numpy", "torch", "transformers", "collections"
    ],
    "excludes": [
        "matplotlib", "scipy", "pandas", "PIL", "cv2", "sklearn",
        "tensorflow", "keras", "jupyter", "IPython"
    ],
    "include_files": [
        # Include model files and configurations
        ("config.json", "config.json"),
        ("vocab.txt", "vocab.txt"),
        ("tokenizer_config.json", "tokenizer_config.json"),
        ("special_tokens_map.json", "special_tokens_map.json"),
        ("improved_inference.py", "improved_inference.py"),
        # Include model weights if they exist
        ("pytorch_model.bin", "pytorch_model.bin") if os.path.exists("pytorch_model.bin") else None,
        ("model.safetensors", "model.safetensors") if os.path.exists("model.safetensors") else None,
    ],
    "optimize": 2,
    "zip_include_packages": ["*"],
    "zip_exclude_packages": [],
}

# Filter out None values from include_files
build_exe_options["include_files"] = [f for f in build_exe_options["include_files"] if f is not None]

# Executable definition
executables = [
    cx_Freeze.Executable(
        script="ner_gui_app.py",
        base="Win32GUI" if sys.platform == "win32" else None,
        target_name="ItalianMedicalNER.exe",
        icon=None,  # Add icon file path if you have one
        shortcut_name="Italian Medical NER",
        shortcut_dir="DesktopFolder",
    )
]

# Setup configuration
cx_Freeze.setup(
    name=name,
    version=version,
    description=description,
    author=author,
    options={"build_exe": build_exe_options},
    executables=executables,
)

