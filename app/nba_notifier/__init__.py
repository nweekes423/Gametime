# nba_notifier/__init__.py
from __future__ import absolute_import, unicode_literals
from .celeryy import app as celery_app
import logging
import time

logger = logging.getLogger(__name__)

# Log server startup time
start_time = time.time()
logger.info("Server starting...")

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.


__all__ = ("celery_app",)


# Log server startup duration
end_time = time.time()
startup_duration = end_time - start_time
logger.info(f"Server startup complete. Duration: {startup_duration:.2f} seconds.")


