from datetime import datetime, timedelta

import pytz
from django.test import TestCase

from .utils import is_time_to_check_scores


class UtilsTests(TestCase):
    def test_is_time_to_check_scores_within_time(self):
        # Test when the current time is within the specified time range
        now_pacific = datetime.now(pytz.timezone("America/Los_Angeles"))
        valid_time = now_pacific.replace(hour=18, minute=0, second=0, microsecond=0)
        with self.override_settings(TIME_ZONE="America/Los_Angeles"):
            self.assertEqual(is_time_to_check_scores(valid_time), True)

    def test_is_time_to_check_scores_outside_time(self):
        # Test when the current time is outside the specified time range
        now_pacific = datetime.now(pytz.timezone("America/Los_Angeles"))
        invalid_time = now_pacific.replace(hour=12, minute=0, second=0, microsecond=0)
        with self.override_settings(TIME_ZONE="America/Los_Angeles"):
            self.assertEqual(is_time_to_check_scores(invalid_time), False)
