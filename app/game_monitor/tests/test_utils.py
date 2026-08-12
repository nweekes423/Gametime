from unittest.mock import MagicMock, patch

from django.test import TestCase

from game_monitor.utils import parse_duration, send_text_message


class UtilsTests(TestCase):
    def test_parse_duration(self):
        minutes, seconds = parse_duration("PT7M30S")

        self.assertEqual(minutes, 7)
        self.assertEqual(seconds, 30.0)

    def test_parse_duration_with_decimal_seconds(self):
        minutes, seconds = parse_duration("PT2M15.5S")

        self.assertEqual(minutes, 2)
        self.assertEqual(seconds, 15.5)

    def test_parse_duration_invalid_value(self):
        minutes, seconds = parse_duration("invalid")

        self.assertEqual(minutes, 0)
        self.assertEqual(seconds, 0)

    @patch("game_monitor.utils.Client")
    def test_send_text_message_fake_mode(self, mock_client):
        with self.settings(
            TWILIO_FAKE_MODE=True,
            TWILIO_ACCOUNT_SID="test-sid",  # nosec B106
            TWILIO_AUTH_TOKEN="test-token",  # nosec B106
            TWILIO_PHONE_NUMBER="+15555555555",
        ):
            result = send_text_message(
                "+15555555556",
                "Test message",
            )

        self.assertTrue(result)
        mock_client.assert_not_called()

    @patch("game_monitor.utils.Client")
    def test_send_text_message_success(self, mock_client):
        mock_message = MagicMock()
        mock_message.sid = "SM123456"
        mock_client.return_value.messages.create.return_value = mock_message

        with self.settings(
            TWILIO_FAKE_MODE=False,
            TWILIO_ACCOUNT_SID="test-sid",  # nosec B106
            TWILIO_AUTH_TOKEN="test-token",  # nosec B106
            TWILIO_PHONE_NUMBER="+15555555555",
        ):
            result = send_text_message(
                "+15555555556",
                "Test message",
            )

        self.assertTrue(result)
        mock_client.assert_called_once_with(
            "test-sid",
            "test-token",
        )
        mock_client.return_value.messages.create.assert_called_once_with(
            from_="+15555555555",
            body="Test message",
            to="+15555555556",
        )
