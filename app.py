#!/usr/bin/env python3
"""
Italian Medical NER - Hugging Face Spaces Entry Point
"""

# This is the entry point for Hugging Face Spaces deployment
# It simply imports and runs the main Streamlit app

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main Streamlit app
from web_demo_app import main

if __name__ == "__main__":
    main()
