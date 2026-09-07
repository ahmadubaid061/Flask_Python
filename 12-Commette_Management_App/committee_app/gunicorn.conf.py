# gunicorn.conf.py
import multiprocessing
import os

# Bind to the port Render provides
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"

# Worker settings
workers = 2  # Start with 2 workers
worker_class = "sync"
timeout = 120  # 2 minutes timeout
graceful_timeout = 30
preload_app = True  # Preload app to reduce memory per worker

# Prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"