import logging
import os
from dotenv import load_dotenv
from twilio.rest import Client
from celery import shared_task

from .utils import is_time_to_check_scores
from .views import fetch_and_update_scoreboard


# Load environment variables from .env file
load_dotenv()

# Import necessary modules
from twilio.rest import Client
import os
from dotenv import load_dotenv


# Your Twilio credentials
# Import necessary modules

import logging

# Load environment variables from .env file


# Your Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_phone = os.getenv("TWILIO_PHONE_NUMBER")

# Get the logger for this module
logger = logging.getLogger(__name__)


def send_test_sms(
    body="[+] This is a test message from your NBA notifier app!",
    to_phone="+15105194907",
):
    try:
        # Initialize Twilio client
        client = Client(account_sid, auth_token)

        # Send test SMS
        message = client.messages.create(body=body, from_=from_phone, to=to_phone)

        logger.info("SMS sent successfully. SID: %s", message.sid)

    except Exception as e:
        # Log any exceptions
        logger.error("Error sending SMS: %s", e)


# Example usage:
# send_test_sms()  # Uses default values
# send_test_sms(body="Custom test message", to_phone="+1234567890")  # Custom values


@shared_task(bind=True, max_retries=3, ignore_result=True)
def update_nba_scores(self):
    try:
        # Call the function to fetch and update the scoreboard
        fetch_and_update_scoreboard()

        # Log a successful update
        logger.info("NBA scores updated successfully.")

        # Send a test SMS to the specified phone number
        send_test_sms()

    except Exception as e:
        # Log any exceptions
        logger.error(f"Error updating NBA scores: {e}")


@shared_task
def frequent_game_score_checks():
    if is_time_to_check_scores():
        try:
            fetch_and_update_scoreboard()
            logger.info("Frequent NBA score check performed successfully.")
        except Exception as e:
            logger.error(f"Error during frequent NBA score check: {e}")
