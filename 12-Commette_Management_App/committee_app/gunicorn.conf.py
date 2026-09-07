# gunicorn.conf.py
import platform

# Disable preload to prevent fork-related crashes with libSQL
preload_app = platform.system() != "Darwin"  # Disable on macOS
# Or simply:
preload_app = False  # Force disable for all platforms

bind = "0.0.0.0:10000"
workers = 1  # Start with just 1 worker
timeout = 120