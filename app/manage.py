#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class DjangoImportError(ImportError):
    """Raised when Django is unavailable in the active Python environment."""

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
        logger.exception("Django import failed.")
        raise DjangoImportError from exc
    logger.debug("Starting Django management command")
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    logger.debug("Running main()")
    main()
