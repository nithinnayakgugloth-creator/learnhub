# Gunicorn Configuration for LearnHub
# Optimized for 50+ concurrent users

import multiprocessing

# Workers = 2-4 x CPU cores
# For a basic VPS with 1-2 CPUs: use 3-4 workers
workers = 3

# Worker class: 'sync' is simplest and works well for Flask
worker_class = 'sync'

# Timeout in seconds (120 for slow connections, 30 for fast)
timeout = 120

# Keep-alive connections (helps with connection overhead)
keepalive = 5

# Max requests per worker (helps prevent memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Access log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Bind address
bind = '0.0.0.0:8000'

# Server socket
backlog = 2048

# Process naming
proc_name = 'learnhub'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed for local HTTPS testing)
# keyfile = 'key.pem'
# certfile = 'cert.pem'
