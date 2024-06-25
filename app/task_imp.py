import requests

from myproject.tasks import app  # app is your celery application
from myproject.exceptions import InvalidUserInput

from utils.mail import api_send_mail

@app.task(bind=True, max_retries=3)
def send_mail(self, recipients, sender_email, subject, body):
    """Send a plaintext email with argument subject, sender and body to a list of recipients."""
    try:
        data = api_send_mail(recipients, sender_email, subject, body)
    except InvalidUserInput:
        # No need to retry as the user provided an invalid input
        raise
    except Exception as exc:
        # Any other exception. Log the exception to sentry and retry in 10s.
        sentrycli.captureException()
        self.retry(countdown=10, exc=exc)
    return data