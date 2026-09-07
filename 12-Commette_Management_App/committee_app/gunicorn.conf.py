# gunicorn.conf.py
import os

# Render assigns the actual port via the $PORT env var - hardcoding 10000
# risks binding to the wrong port if Render ever assigns something else,
# which is exactly what "No open HTTP ports detected" in the logs means.
bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"

workers = 1
timeout = 120
preload_app = False  # keep app import (and the Turso connection) post-fork