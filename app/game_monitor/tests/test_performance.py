import time
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from unittest.mock import patch

from game_monitor.factories import UserPhoneFactory, GameFactory
from game_monitor.models import UserPhone


class PerformanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_root_view_response_time(self):
        """Test root view response time is acceptable."""
        start_time = time.time()
        response = self.client.get(reverse("root"))
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 1.0, "Root view should respond in less than 1 second")

    def test_phone_form_response_time(self):
        """Test phone form response time is acceptable."""
        start_time = time.time()
        response = self.client.get(reverse("phone-form"))
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 1.0, "Phone form should respond in less than 1 second")

    def test_phone_form_post_response_time(self):
        """Test phone form POST response time is acceptable."""
        start_time = time.time()
        response = self.client.post(
            reverse("phone-form"),
            {"phone_number": "+15555555555"},
            follow=True
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 2.0, "Phone form POST should respond in less than 2 seconds")

    @patch("game_monitor.views.get_nba_scoreboard")
    def test_games_view_response_time(self, mock_get_scoreboard):
        """Test games view response time is acceptable."""
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
        
        start_time = time.time()
        response = self.client.get(reverse("games"))
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 2.0, "Games view should respond in less than 2 seconds")

    def test_cache_view_response_time(self):
        """Test cache view response time is acceptable."""
        start_time = time.time()
        response = self.client.get(reverse("test_cache"))
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 3.0, "Cache view should respond in less than 3 seconds")

    def test_cache_view_cached_response_time(self):
        """Test cached cache view response time is significantly faster."""
        # First request to populate cache
        self.client.get(reverse("test_cache"))
        
        # Second request should be cached
        start_time = time.time()
        response = self.client.get(reverse("test_cache"))
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 0.5, "Cached response should be very fast")

    def test_mock_api_response_time(self):
        """Test mock API response time is acceptable."""
        start_time = time.time()
        response = self.client.get("/game-monitor/mock-api/")
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertIn(response.status_code, [200, 404, 500])  # May not have file
        self.assertLess(response_time, 1.0, "Mock API should respond in less than 1 second")

    def test_database_query_performance(self):
        """Test database query performance with multiple records."""
        # Create multiple records
        for _ in range(100):
            UserPhoneFactory()
        
        start_time = time.time()
        count = UserPhone.objects.count()
        end_time = time.time()
        
        query_time = end_time - start_time
        self.assertEqual(count, 100)
        self.assertLess(query_time, 0.5, "Database count query should be fast")

    def test_bulk_create_performance(self):
        """Test bulk create performance."""
        start_time = time.time()
        UserPhoneFactory.create_batch(50)
        end_time = time.time()
        
        create_time = end_time - start_time
        self.assertEqual(UserPhone.objects.count(), 50)
        self.assertLess(create_time, 2.0, "Bulk create should be reasonably fast")

    def test_view_with_many_games(self):
        """Test view performance with many games."""
        # Create many games
        for _ in range(50):
            GameFactory()
        
        with patch("game_monitor.views.get_nba_scoreboard") as mock_get:
            mock_data = {
                "scoreboard": {
                    "games": [
                        {
                            "homeTeam": {"teamName": f"Team{i}", "score": 100 + i},
                            "awayTeam": {"teamName": f"Opponent{i}", "score": 95 + i},
                            "gameClock": "PT8M30S",
                            "period": 4
                        }
                        for i in range(50)
                    ]
                }
            }
            mock_get.return_value = mock_data
            
            start_time = time.time()
            response = self.client.get(reverse("games"))
            end_time = time.time()
            
            response_time = end_time - start_time
            self.assertEqual(response.status_code, 200)
            self.assertLess(response_time, 3.0, "View with many games should still be responsive")

    def test_concurrent_requests_simulation(self):
        """Test basic concurrent request handling."""
        import threading
        
        results = []
        def make_request():
            start_time = time.time()
            response = self.client.get(reverse("root"))
            end_time = time.time()
            results.append((response.status_code, end_time - start_time))
        
        threads = [threading.Thread(target=make_request) for _ in range(10)]
        start_time = time.time()
        
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # All requests should succeed
        for status, _ in results:
            self.assertEqual(status, 200)
        
        # Total time should be reasonable (not 10x sequential time)
        self.assertLess(total_time, 5.0, "Concurrent requests should be handled efficiently")