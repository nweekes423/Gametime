from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
import pytz
import re

def send_email(to_email, subject, body):
    send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )

def send_email(to_number, body):
    # Convert phone number to email address format
    to_email = f"{to_number}@{settings.LOCAL_SMTP_DOMAIN}"
    
    # Call the send_email function
    send_email(to_email, "SMS Notification", body)

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

