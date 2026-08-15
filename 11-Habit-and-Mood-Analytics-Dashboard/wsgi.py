import sys
import os

# CRITICAL FIX: Add the current directory to Python's system path
# This tells Vercel exactly where to find the 'app' folder
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

app = create_app()