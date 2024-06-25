#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the path to your project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Add the path to your project's parent directory
sys.path.append(os.path.join(BASE_DIR, ".."))

def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nba_notifier.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        logger.error("Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable? Did you forget to activate a virtual environment?")
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    logger.debug("Starting Django management command")
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    logger.debug("Running main()")
    main()
