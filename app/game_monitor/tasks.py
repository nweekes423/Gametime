import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, ignore_result=True)
def update_nba_scores(self):
    try:
        from .views import fetch_and_update_scoreboard

        fetch_and_update_scoreboard()
        logger.info("NBA/WNBA scores updated successfully.")

    except Exception as exc:
        logger.exception("Error updating scores")
        raise self.retry(exc=exc, countdown=60) from exc


@shared_task
def frequent_game_score_checks():
    try:
        from .views import fetch_and_update_scoreboard

        logger.info("[CELERY] Running game score check...")
        fetch_and_update_scoreboard()

    except Exception:
        logger.exception("Error in frequent checks")
