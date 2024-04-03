# game_monitor/tasks.py
import logging

from celery import shared_task

from .utils import is_time_to_check_scores
from .views import fetch_and_update_scoreboard

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, ignore_result=True)
def update_nba_scores(self):
    try:
        # Call the function to fetch and update the scoreboard
        fetch_and_update_scoreboard()

        # Log a successful update
        logger.info("NBA scores updated successfully.")
    # except SomeTransientException as e:
    # logger.warning(f"Retrying due to error: {e}")
    # self.retry(exc=e, countdown=60)
    except Exception as e:
        # Log any exceptions
        logger.error(f"Error updating NBA scores: {e}")


@shared_task
def frequent_game_score_checks():
    if is_time_to_check_scores():
        try:
            fetch_and_update_scoreboard()
            logger.info("Frequent NBA score check performed succesfully.")
        except Exception as e:
            logger.error(f"Error during frequent NBA score check: {e}")
