import json
from unittest.mock import mock_open, patch

from django.contrib.messages import get_messages
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from game_monitor.factories import UserPhoneFactory
from game_monitor.models import UserPhone


class ViewsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_root_view_basic(self):
        """Test root view basic functionality."""
        response = self.client.get("/")  # Root URL
        self.assertEqual(response.status_code, 200)

    def test_phone_view_get_renders_form(self):
        """Test phone view GET request renders form."""
        response = self.client.get(reverse("phone-form"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, "phone_number")

    def test_phone_view_post_creates_new_user(self):
        """Test phone view POST creates new user."""
        response = self.client.post(
            reverse("phone-form"),
            {"phone_number": "+15555555555"},
            follow=True
        )
        self.assertRedirects(response, reverse("success-page"))
        self.assertEqual(UserPhone.objects.count(), 1)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("New phone number registered" in str(m) for m in messages))

    def test_phone_view_post_duplicate_user(self):
        """Test phone view POST with duplicate user."""
        UserPhoneFactory(phone_number="+15555555555")
        
        response = self.client.post(
            reverse("phone-form"),
            {"phone_number": "+15555555555"},
            follow=True
        )
        self.assertEqual(UserPhone.objects.count(), 1)
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("already exists" in str(m) for m in messages))

    def test_phone_view_post_invalid_format(self):
        """Test phone view POST with invalid format."""
        response = self.client.post(
            reverse("phone-form"),
            {"phone_number": "invalid"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid phone number")
        self.assertEqual(UserPhone.objects.count(), 0)

    def test_success_view(self):
        """Test success view."""
        response = self.client.get(reverse("success-page"))
        self.assertEqual(response.status_code, 200)

    @patch("game_monitor.views.get_nba_scoreboard")
    def test_games_view_successful_fetch(self, mock_get_scoreboard):
        """Test games view with successful data fetch."""
        mock_data = {
            "scoreboard": {
                "games": [
                    {
                        "homeTeam": {"teamName": "Lakers", "score": 100},
                        "awayTeam": {"teamName": "Warriors", "score": 95},
                        "gameClock": "PT8M30S",
                        "period": 4
                    }
                ]
            }
        }
        mock_get_scoreboard.return_value = mock_data
        
        response = self.client.get(reverse("games"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lakers")
        self.assertContains(response, "Warriors")
        self.assertContains(response, "100 - 95")

    @patch("game_monitor.views.get_nba_scoreboard")
    def test_games_view_key_error(self, mock_get_scoreboard):
        """Test games view handles KeyError."""
        mock_get_scoreboard.side_effect = KeyError("Missing key")
        
        response = self.client.get(reverse("games"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games available")

    @patch("game_monitor.views.get_nba_scoreboard")
    def test_games_view_type_error(self, mock_get_scoreboard):
        """Test games view handles TypeError."""
        mock_get_scoreboard.side_effect = TypeError("Invalid type")
        
        response = self.client.get(reverse("games"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games available")

    @patch("game_monitor.views.get_nba_scoreboard")
    def test_games_view_value_error(self, mock_get_scoreboard):
        """Test games view handles ValueError."""
        mock_get_scoreboard.side_effect = ValueError("Invalid value")
        
        response = self.client.get(reverse("games"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games available")

    @patch("game_monitor.views.get_nba_scoreboard")
    def test_games_view_unexpected_error(self, mock_get_scoreboard):
        """Test games view handles unexpected errors."""
        mock_get_scoreboard.side_effect = Exception("Unexpected")
        
        response = self.client.get(reverse("games"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games available")

    def test_parse_duration_valid(self):
        """Test parse_duration with valid input."""
        from game_monitor.views import parse_duration
        minutes, seconds = parse_duration("PT7M30S")
        self.assertEqual(minutes, 7)
        self.assertEqual(seconds, 30.0)

    def test_parse_duration_decimal_seconds(self):
        """Test parse_duration with decimal seconds."""
        from game_monitor.views import parse_duration
        minutes, seconds = parse_duration("PT2M15.5S")
        self.assertEqual(minutes, 2)
        self.assertEqual(seconds, 15.5)

    def test_parse_duration_invalid(self):
        """Test parse_duration with invalid input."""
        from game_monitor.views import parse_duration
        minutes, seconds = parse_duration("invalid")
        self.assertEqual(minutes, 0)
        self.assertEqual(seconds, 0)

    def test_parse_time_valid(self):
        """Test parse_time with valid input."""
        from game_monitor.views import parse_time
        result = parse_time("5:30")
        self.assertEqual(result, 5.5)

    def test_is_close_game_true(self):
        """Test is_close_game returns True for close game."""
        from game_monitor.views import is_close_game
        game = {
            "homeTeam": {"teamName": "Lakers", "score": 100},
            "awayTeam": {"teamName": "Warriors", "score": 98},
            "gameClock": "PT5M30S",
            "period": 4
        }
        self.assertTrue(is_close_game(game))

    def test_is_close_game_false_score_diff(self):
        """Test is_close_game returns False for score difference > 10."""
        from game_monitor.views import is_close_game
        game = {
            "homeTeam": {"teamName": "Lakers", "score": 100},
            "awayTeam": {"teamName": "Warriors", "score": 85},
            "gameClock": "PT5M30S",
            "period": 4
        }
        self.assertFalse(is_close_game(game))

    def test_is_close_game_false_time_left(self):
        """Test is_close_game returns False for time > 8 minutes."""
        from game_monitor.views import is_close_game
        game = {
            "homeTeam": {"teamName": "Lakers", "score": 100},
            "awayTeam": {"teamName": "Warriors", "score": 98},
            "gameClock": "PT10M00S",
            "period": 4
        }
        self.assertFalse(is_close_game(game))

    def test_is_close_game_false_period(self):
        """Test is_close_game returns False for period < 4."""
        from game_monitor.views import is_close_game
        game = {
            "homeTeam": {"teamName": "Lakers", "score": 100},
            "awayTeam": {"teamName": "Warriors", "score": 98},
            "gameClock": "PT5M30S",
            "period": 3
        }
        self.assertFalse(is_close_game(game))

    def test_is_close_game_invalid_data(self):
        """Test is_close_game handles invalid data."""
        from game_monitor.views import is_close_game
        game = {"invalid": "data"}
        self.assertFalse(is_close_game(game))

    @patch("game_monitor.views.send_text_message")
    def test_send_close_game_notifications(self, mock_send):
        """Test _send_close_game_notifications calls send_text_message."""
        from game_monitor.views import _send_close_game_notifications
        UserPhoneFactory(phone_number="+15555555555")
        
        game = {
            "homeTeam": {"teamName": "Lakers", "score": 100},
            "awayTeam": {"teamName": "Warriors", "score": 98}
        }
        
        _send_close_game_notifications(game, "NBA")
        self.assertEqual(mock_send.call_count, 1)

    @patch("game_monitor.views.get_nba_scoreboard")
    @patch("game_monitor.views._send_close_game_notifications")
    def test_fetch_and_update_scoreboard_nba_success(self, mock_send, mock_get):
        """Test fetch_and_update_scoreboard NBA success case."""
        mock_data = {
            "scoreboard": {
                "games": [
                    {
                        "homeTeam": {"teamName": "Lakers", "score": 100},
                        "awayTeam": {"teamName": "Warriors", "score": 98},
                        "gameClock": "PT5M30S",
                        "period": 4
                    }
                ]
            }
        }
        mock_get.return_value = mock_data
        
        with patch("builtins.open", mock_open()):
            from game_monitor.views import fetch_and_update_scoreboard
            fetch_and_update_scoreboard()
        
        mock_get.assert_called_once()

    @patch("game_monitor.views.get_nba_scoreboard")
    def test_fetch_and_update_scoreboard_nba_error(self, mock_get):
        """Test fetch_and_update_scoreboard NBA error handling."""
        mock_get.side_effect = KeyError("Error")
        
        with patch("builtins.open", mock_open()):
            from game_monitor.views import fetch_and_update_scoreboard
            fetch_and_update_scoreboard()
        
        # Should not raise exception
        mock_get.assert_called_once()

    @patch("wnba_api.scoreboard.get_scoreboard")
    @patch("wnba_api.scoreboard.convert_to_nba_format")
    def test_fetch_and_update_scoreboard_wnba_success(self, mock_convert, mock_get):
        """Test fetch_and_update_scoreboard WNBA success case."""
        mock_raw = {"games": []}
        mock_converted = {"scoreboard": {"games": []}}
        mock_get.return_value = mock_raw
        mock_convert.return_value = mock_converted
        
        with patch("builtins.open", mock_open()):
            from game_monitor.views import fetch_and_update_scoreboard
            fetch_and_update_scoreboard()
        
        mock_get.assert_called_once()
        mock_convert.assert_called_once()

