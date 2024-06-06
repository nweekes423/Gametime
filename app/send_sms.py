import logging
from django.http import HttpResponse
from twilio.rest import Client
from django.conf import settings

# Configure logger
logger = logging.getLogger('twilio')

def send_sms(request):
    try:
        logger.debug("send_sms function called.")
        logger.debug(f"TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID}")
        logger.debug(f"TWILIO_AUTH_TOKEN: {settings.TWILIO_AUTH_TOKEN}")
        logger.debug(f"TWILIO_PHONE_NUMBER: {settings.TWILIO_PHONE_NUMBER}")

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=settings.TWILIO_PHONE_NUMBER,
            to="+15105194907",
            body="Hello from Django!"
        )
        logger.debug(f"SMS sent with message ID: {message.sid}")
        return HttpResponse(f"SMS sent with message ID: {message.sid}")
    except Exception as e:
        logger.error(f"Failed to send SMS: {e}", exc_info=True)
        return HttpResponse(f"Failed to send SMS: {e}", status=500)

