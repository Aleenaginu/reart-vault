import multiprocessing

# Number of worker processes
workers = multiprocessing.cpu_count() * 2 + 1

# Maximum requests before worker restart
max_requests = 1000
max_requests_jitter = 50

# Timeout settings
timeout = 120
graceful_timeout = 30

# Worker class
worker_class = 'sync'

# Log level
loglevel = 'info'

# Process name
proc_name = 'reart_gunicorn'

# Prevent memory leaks
preload_app = True

# Worker timeout
timeout = 60

# Maximum number of simultaneous clients
worker_connections = 1000

# Maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'

# SSL configuration (if needed)
# keyfile = 'path/to/keyfile'
# certfile = 'path/to/certfile' 
