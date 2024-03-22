from datetime import datetime

import pytz
from django.conf import settings
from twilio.rest import Client
import re


def send_text_message(to_number, body):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        from_=settings.TWILIO_PHONE_NUMBER, body=body, to=to_number
    )
    print(message.sid)


def is_time_to_check_scores(current_time=None):
    if current_time is None:
        current_time = datetime.now(pytz.timezone("America/Los_Angeles"))

    start_time = current_time.replace(hour=18, minute=0, second=0, microsecond=0)
    end_time = current_time.replace(hour=20, minute=0, second=0, microsecond=0)

    return start_time <= current_time <= end_time


def parse_duration(duration_str):
    """Parse ISO 8601 duration string into minutes and seconds."""
    match = re.match(r"PT(\d+)M(\d+\.?\d*)S", duration_str)
    if match:
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        return minutes, seconds
    else:
        return 0, 0
