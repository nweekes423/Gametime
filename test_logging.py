import os
import django
import logging

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nba_notifier.settings")
django.setup()

# Get the logger for the "django" namespace
logger = logging.getLogger("django")

# Log a test message
logger.info("LOOK This is a test log message")
