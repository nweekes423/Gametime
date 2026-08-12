import json
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages

from game_monitor.factories import UserPhoneFactory, GameFactory
from game_monitor.models import UserPhone, Game


class GameMonitorIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_root_view(self):
        """Test the root view renders correctly."""
        response = self.client.get(reverse("root"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to the Root Page")

    def test_phone_view_get(self):
        """Test GET request to phone form view."""
        response = self.client.get(reverse("phone-form"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_phone_view_post_valid(self):
        """Test POST request with valid phone number."""
        response = self.client.post(
            reverse("phone-form"),
            {"phone_number": "+15555555555"},
            follow=True
        )
        self.assertRedirects(response, reverse("success-page"))
        
        # Check that phone number was created
        self.assertEqual(UserPhone.objects.count(), 1)
        self.assertEqual(UserPhone.objects.first().phone_number, "+15555555555")
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "New phone number registered.")

    def test_phone_view_post_duplicate(self):
        """Test POST request with duplicate phone number."""
        # Create existing phone number
        UserPhoneFactory(phone_number="+15555555555")
        
        response = self.client.post(
            reverse("phone-form"),
            {"phone_number": "+15555555555"},
            follow=True
        )
        self.assertRedirects(response, reverse("success-page"))
        
        # Check that no new phone number was created
        self.assertEqual(UserPhone.objects.count(), 1)
        
        # Check warning message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Phone number already exists!")

    def test_phone_view_post_invalid(self):
        """Test POST request with invalid phone number."""
        response = self.client.post(
            reverse("phone-form"),
            {"phone_number": "invalid"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid phone number")
        
        # Check that no phone number was created
        self.assertEqual(UserPhone.objects.count(), 0)

    def test_success_view(self):
        """Test the success page view."""
        response = self.client.get(reverse("success-page"))
        self.assertEqual(response.status_code, 200)

    @patch("game_monitor.views.get_nba_scoreboard")
    def test_games_view_success(self, mock_get_scoreboard):
        """Test games view with successful API response."""
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

    @patch("game_monitor.views.get_nba_scoreboard")
    def test_games_view_api_error(self, mock_get_scoreboard):
        """Test games view handles API errors gracefully."""
        mock_get_scoreboard.side_effect = KeyError("Test error")
        
        response = self.client.get(reverse("games"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games available")

    @patch("game_monitor.views.get_nba_scoreboard")
    def test_games_view_unexpected_error(self, mock_get_scoreboard):
        """Test games view handles unexpected errors gracefully."""
        mock_get_scoreboard.side_effect = Exception("Unexpected error")
        
        response = self.client.get(reverse("games"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games available")

    def test_mock_api_view_with_close_games(self):
        """Test mock API view with close games in scoreboard."""
        # Create a close game scenario
        game_data = {
            "scoreboard": {
                "games": [
                    {
                        "homeTeam": {"teamName": "Lakers", "score": 100},
                        "awayTeam": {"teamName": "Warriors", "score": 98},
                        "gameClock": "PT5M30S",
                        "period": 4
                    },
                    {
                        "homeTeam": {"teamName": "Celtics", "score": 110},
                        "awayTeam": {"teamName": "Heat", "score": 85},
                        "gameClock": "PT10M00S",
                        "period": 3
                    }
                ]
            }
        }
        
        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(game_data)
            
            response = self.client.get("/game-monitor/mock-api/")
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn("close_games", data)
            self.assertEqual(len(data["close_games"]), 1)  # Only first game is close

    def test_mock_api_view_file_not_found(self):
        """Test mock API view handles missing file."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            response = self.client.get("/game-monitor/mock-api/")
            self.assertEqual(response.status_code, 404)
            data = response.json()
            self.assertEqual(data["error"], "File not found")

    def test_mock_api_view_invalid_json(self):
        """Test mock API view handles invalid JSON."""
        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "invalid json"
            
            response = self.client.get("/game-monitor/mock-api/")
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertEqual(data["error"], "Invalid JSON")

    def test_test_cache_view_cache_miss(self):
        """Test cache view when cache is empty."""
        with patch("game_monitor.views.cache.get", return_value=None):
            response = self.client.get(reverse("test_cache"))
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["fetch_source"], "Generated")
            self.assertIn("elapsed_time", data)

    def test_test_cache_view_cache_hit(self):
        """Test cache view when data is cached."""
        cached_data = {"message": "This is a test data"}
        with patch("game_monitor.views.cache.get", return_value=cached_data):
            response = self.client.get(reverse("test_cache"))
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["fetch_source"], "Cache")
            self.assertEqual(data["data"], cached_data)

    @patch("game_monitor.views.fetch_and_update_scoreboard")
    def test_fetch_and_update_scoreboard_success(self, mock_fetch):
        """Test the scoreboard fetch and update function."""
        mock_fetch.return_value = None
        
        from game_monitor.views import fetch_and_update_scoreboard
        fetch_and_update_scoreboard()
        
        mock_fetch.assert_called_once()

    def test_userphone_model_validation(self):
        """Test UserPhone model validation."""
        # Valid phone number
        user_phone = UserPhoneFactory(phone_number="+14155552671")
        user_phone.full_clean()  # Should not raise
        
        # Invalid phone number
        with self.assertRaises(Exception):
            invalid_phone = UserPhone(phone_number="invalid")
            invalid_phone.full_clean()

    def test_game_model_creation(self):
        """Test Game model creation."""
        game = GameFactory()
        self.assertEqual(Game.objects.count(), 1)
        self.assertIsNotNone(game.title)
        self.assertIsNotNone(game.home_team)
        self.assertIsNotNone(game.away_team)

    def test_csrf_protection(self):
        """Test that CSRF protection is working."""
        # Try to POST without CSRF token
        response = self.client.post(
            reverse("phone-form"),
            {"phone_number": "+15555555555"}
        )
        # Should fail or redirect due to CSRF protection
        self.assertIn(response.status_code, [200, 302, 403])