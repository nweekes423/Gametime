from multiprocessing import cpu_count

bind = "0.0.0.0:8000"
workers = cpu_count() * 2 + 1  # Use twice the number of CPU cores plus one
worker_class = "gthread"  # Use gthread worker type
threads = 2
user = "will"
group = "staff"
loglevel = "info"
accesslog = "app/nba_notifier/logs/gunicorn_access.log"
errorlog = "app/nba_notifier/logs/gunicorn_error.log"
wsgi_app = "app.nba_notifier.wsgi"
timeout = 60  # Increase the timeout to 60 seconds
graceful_timeout = 60  # Increase the graceful timeout to 60 seconds

