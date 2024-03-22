from datetime import datetime, timedelta
import pytz
from django.test import TestCase, override_settings
from game_monitor.utils import is_time_to_check_scores

class UtilsTests(TestCase):
    def test_is_time_to_check_scores_within_time(self):
        now_pacific = datetime.now(pytz.timezone("America/Los_Angeles"))
        valid_time = now_pacific.replace(hour=18, minute=0, second=0, microsecond=0)
        with override_settings(TIME_ZONE="America/Los_Angeles"):
            self.assertEqual(is_time_to_check_scores(valid_time), True)

    def test_is_time_to_check_scores_outside_time(self):
        now_pacific = datetime.now(pytz.timezone("America/Los_Angeles"))
        invalid_time = now_pacific.replace(hour=12, minute=0, second=0, microsecond=0)
        with override_settings(TIME_ZONE="America/Los_Angeles"):
            self.assertEqual(is_time_to_check_scores(invalid_time), False)

