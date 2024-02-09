from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from game_monitor.views import is_close_game

from .models import Game
from .utils import send_text_message


class GameMonitorTests(TestCase):
    def test_str_representation(self):
        game = Game(title="Lakers vs Celtics")
        self.assertEqual(str(game), "Lakers vs Celtics")

    def test_is_close_game(self):
        game_data = {
            "homeTeam": {"score": 100, "teamName": "Team A"},
            "awayTeam": {"score": 95, "teamName": "Team B"},
            "gameClock": "PT7M30S",
            "period": 4,
        }
        self.assertTrue(is_close_game(game_data), "should return True")

    def test_is_close_game_false(self):
        game_data = {
            "homeTeam": {"score": 120, "teamName": "Lakers"},
            "awayTeam": {"score": 90, "teamName": "Celtics"},
            "gameClock": "PT12M00S",
            "period": 2,
        }
        self.assertFalse(is_close_game(game_data), "should return False")


class TwilioSMSTests(TestCase):
    @patch("game_monitor.utils.Client")  # Mocking the Twilio Client
    def test_send_text_message(self, mock_client):
        # These lines should be indented as they are part of the test function
        mock_client.return_value.messages.create.return_value.sid = "TestSID"
        send_text_message("+15105194907", "Test message")
        mock_client.return_value.messages.create.assert_called_once_with(
            to="+15105194907", from_=settings.TWILIO_PHONE_NUMBER, body="Test message"
        )


class ViewTests(TestCase):
    def test_phone_view_get(self):
        # Test the GET request
        # response = self.client.get(reverse('mock-nba-api'))  # URL of app from urls.py
        response = self.client.get(reverse("phone-form"))
        print("Response Content:", response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "phone-form.html")

    def test_phone_view_post_valid(self):
        # Test POST request with valid data
        response = self.client.post(
            reverse("phone-form"), {"phone_number": "+15105194907"}
        )
        self.assertRedirects(response, reverse("success-page"))


class GameViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_games = 5
        for game_id in range(number_of_gamesx):
            Game.objects.create(title=f"Game {game_id}")

        def test_view_url_exists_at_desired_location(self):
            response = self.client.get("/games/")
            self.assertEqual(response.status_code, 200)

        def test_view_uses_correct_template(self):
            response = self.client.get(reverse("games"))
            self.assertEqual(resonse.status_code, 200)
            self.assertTemplateUsed(response, "game_monitor/game_list.html")
