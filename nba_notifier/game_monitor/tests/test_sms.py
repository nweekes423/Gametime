import unittest
from unittest.mock import patch

from django.conf import settings

from game_monitor.utils import send_text_message


class TestSMSSending(unittest.TestCase):
    @patch("game_monitor.utils.Client")
    def test_send_text_message(self, mock_client):
        # Mock data
        to_number = "+15105374865"
        body = "Test Message 1/31 5:40PM"

        # Call the function
        send_text_message(to_number, body)

        # Assertions to check if Twilio client is called correctly
        mock_client.assert_called_once()
        mock_client.return_value.messages.create.assert_called_with(
            from_=settings.TWILIO_PHONE_NUMBER,  # Your Twilio number
            body=body,
            to=to_number,
        )


if __name__ == "__main__":
    unittest.main()
