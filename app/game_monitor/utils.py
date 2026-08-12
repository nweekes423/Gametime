import re

from django.conf import settings
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client


def send_text_message(to_number, body):
    """Send an SMS, or print it when Twilio fake mode is enabled."""

    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    from_phone = getattr(settings, "TWILIO_PHONE_NUMBER", None)

    is_fake = (
        getattr(settings, "TWILIO_FAKE_MODE", False)
        or not account_sid
        or not auth_token
        or not from_phone
        or "default-sid" in str(account_sid)
        or "default-token" in str(auth_token)
        or "YOUR" in str(from_phone)
    )

    if is_fake:
        print(f"[FAKE SMS] To: {to_number} Body: {body}")
        return True

    try:
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_=from_phone,
            body=body,
            to=to_number,
        )
    except TwilioRestException as exc:
        print(f"[SMS ERROR] {exc}")
        return False
    else:
        print(f"[SMS SENT] SID: {message.sid}")
        return True


def parse_duration(duration_str):
    """Parse ISO 8601 duration string into minutes and seconds."""

    match = re.match(r"PT(\d+)M(\d+\.?\d*)S", duration_str)

    if match:
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        return minutes, seconds

    return 0, 0
