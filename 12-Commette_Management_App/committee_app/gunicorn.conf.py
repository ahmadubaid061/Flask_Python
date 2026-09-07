
# gunicorn.conf.py
preload_app = False  # This disables preload
bind = "0.0.0.0:10000"
workers = 1
timeout = 120