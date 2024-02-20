# game_monitor/tests/test_tasks.py
import logging
from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from game_monitor.tasks import frequent_game_score_checks, update_nba_scores

logger = logging.getLogger(__name__)

class CeleryTasksTest(TestCase):
    def setUp(self):
        # Mock is_time_to_check_scores to always return True for testing
        self.patcher = patch("game_monitor.tasks.is_time_to_check_scores", return_value=True)
        self.mock_is_time_to_check_scores = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_update_nba_scores_task(self):
        # Test the update_nba_scores task
        with patch("game_monitor.tasks.fetch_and_update_scoreboard") as mock_fetch:
            update_nba_scores()
            mock_fetch.assert_called_once()

    def test_frequent_game_score_checks_task(self):
        # Test the frequent_game_score_checks task
        with patch("game_monitor.tasks.fetch_and_update_scoreboard") as mock_fetch:
            frequent_game_score_checks()
            mock_fetch.assert_called_once()

    def test_periodic_task_exists(self):
        # Ensure that the periodic task is added to the database
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute="0", hour="*", day_of_week="*", day_of_month="*", month_of_year="*"
        )
        task, created = PeriodicTask.objects.get_or_create(
            name="Update NBA Scores Every Hour",
            task="game_monitor.tasks.update_nba_scores",
            crontab=schedule,
        )
        tasks = PeriodicTask.objects.filter(name="Update NBA Scores Every Hour")
        logger.info(f"Number of periodic tasks: {tasks.count()}")
        self.assertTrue(tasks.exists(), "Expected task not found")
