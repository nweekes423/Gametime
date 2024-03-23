from django.apps import AppConfig


class GameMonitorConfig(AppConfig):
    name = "game_monitor"

    def ready(self):
        from django_celery_beat.models import CrontabSchedule, PeriodicTask

        # Your scheduling code here
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute="0", hour="*", day_of_week="*", day_of_month="*", month_of_year="*"
        )
        PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name="Update NBA Scores Every Hour",
            task="game_monitor.tasks.update_nba_scores",
        )
