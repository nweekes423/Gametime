# game_monitor/tests/test_tasks.py
from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase
from django_celery_beat.models import PeriodicTask

from game_monitor.tasks import frequent_game_score_checks, update_nba_scores


class CeleryTasksTest(TestCase):
    def setUp(self):
        # Mock is_time_to_check_scores to always return True for testing
        self.patcher = patch(
            "game_monitor.tasks.is_time_to_check_scores", return_value=True
        )
        self.mock_is_time_to_check_scores = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_update_nba_scores_task(self):
        with patch("game_monitor.tasks.fetch_and_update_scoreboard") as mock_fetch:
            update_nba_scores()
            mock_fetch.assert_called_once()

    def test_frequent_game_score_checks_task(self):
        with patch("game_monitor.tasks.fetch_and_update_scoreboard") as mock_fetch:
            frequent_game_score_checks()
            mock_fetch.assert_called_once()

    def test_periodic_task_exists(self):
        # Ensure that the periodic task is added to the database
        task = PeriodicTask.objects.filter(name="Frequent NBA Score Checks")
        self.assertTrue(task.exists())
        self.assertEqual(
            task.first().task, "game_monitor.tasks.frequent_game_score_checks"
        )

    def test_periodic_task_schedule(self):
        # Ensure that the periodic task is set to run every minute
        task = PeriodicTask.objects.get(name="Frequent NBA Score Checks")
        self.assertEqual(task.crontab.minute, "*")
        self.assertEqual(task.crontab.hour, "*")
        self.assertEqual(task.crontab.day_of_week, "*")
