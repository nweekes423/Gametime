from unittest.mock import patch

from django.test import TestCase
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from game_monitor.tasks import (
    frequent_game_score_checks,
    update_nba_scores,
)


class CeleryTasksTest(TestCase):
    def test_update_nba_scores_task(self):
        """Verify the NBA score update task calls the scoreboard updater."""
        with patch("game_monitor.views.fetch_and_update_scoreboard") as mock_fetch:
            update_nba_scores.run()
            mock_fetch.assert_called_once()

    def test_frequent_game_score_checks_task(self):
        """Verify the frequent score-check task calls the scoreboard updater."""
        with patch("game_monitor.views.fetch_and_update_scoreboard") as mock_fetch:
            frequent_game_score_checks()
            mock_fetch.assert_called_once()

    def test_periodic_task_exists(self):
        """Verify the expected periodic Celery task can be registered."""
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="*",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
        )

        PeriodicTask.objects.get_or_create(
            name="Update NBA Scores Every Hour",
            task="game_monitor.tasks.update_nba_scores",
            crontab=schedule,
        )

        self.assertTrue(
            PeriodicTask.objects.filter(name="Update NBA Scores Every Hour").exists()
        )
