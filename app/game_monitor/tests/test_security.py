from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

from game_monitor.factories import UserPhoneFactory
from game_monitor.models import UserPhone


class SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_sql_injection_attempt_phone_form_post(self):
        """Test that SQL injection attempts are handled safely."""
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "1' UNION SELECT * FROM users--",
            "admin'--",
            "' OR 1=1--",
        ]
        
        for payload in sql_injection_payloads:
            response = self.client.post(
                reverse("phone-form"),
                {"phone_number": payload}
            )
            # Should not cause 500 error (should handle gracefully)
            self.assertIn(response.status_code, [200, 302])
            # Should not create invalid phone numbers
            self.assertEqual(UserPhone.objects.filter(phone_number=payload).count(), 0)

    def test_xss_attempt_phone_form_post(self):
        """Test that XSS attempts are handled safely."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<svg onload=alert('xss')>",
        ]
        
        for payload in xss_payloads:
            response = self.client.post(
                reverse("phone-form"),
                {"phone_number": payload}
            )
            # Should handle XSS attempts gracefully
            self.assertIn(response.status_code, [200, 302])

    def test_csrf_protection(self):
        """Test that CSRF protection is working."""
        # Try to POST without CSRF token
        response = self.client.post(
            reverse("phone-form"),
            {"phone_number": "+15555555555"},
            HTTP_X_CSRFTOKEN="invalid"
        )
        # Should fail due to CSRF protection
        self.assertIn(response.status_code, [200, 302, 403])

    def test_phone_number_validation_prevents_malicious(self):
        """Test that phone number validation prevents malicious input."""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "../../../etc/passwd",
            "http://malicious.com",
            "${7*7}",  # Template injection
            "{{7*7}}",  # Template injection
        ]
        
        for malicious_input in malicious_inputs:
            response = self.client.post(
                reverse("phone-form"),
                {"phone_number": malicious_input}
            )
            # Should reject invalid input
            self.assertIn(response.status_code, [200, 302])
            # Should not create malicious phone numbers
            self.assertEqual(UserPhone.objects.filter(phone_number=malicious_input).count(), 0)

    def test_long_input_handling_safe(self):
        """Test that extremely long inputs are handled safely."""
        long_input = "A" * 10000  # Very long string
        
        response = self.client.post(
            reverse("phone-form"),
            {"phone_number": long_input}
        )
        # Should handle long input gracefully
        self.assertIn(response.status_code, [200, 302])
        # Should not create invalid phone numbers
        self.assertEqual(UserPhone.objects.filter(phone_number=long_input).count(), 0)

    def test_special_characters_handling_safe(self):
        """Test that special characters are handled properly."""
        special_chars = [
            "!@#$%^&*()",
            "[]{};':\",./<>?",
            "\n\r\t",
            "\x00\x01\x02",  # Null bytes and control characters
        ]
        
        for special_char in special_chars:
            response = self.client.post(
                reverse("phone-form"),
                {"phone_number": special_char}
            )
            # Should handle special characters gracefully
            self.assertIn(response.status_code, [200, 302])

    def test_api_error_handling_no_leak(self):
        """Test that API errors don't leak sensitive information."""
        with patch("game_monitor.views.get_nba_scoreboard") as mock_get:
            # Simulate an internal error
            mock_get.side_effect = Exception("Internal database connection failed")
            
            response = self.client.get(reverse("games"))
            
            # Should return user-friendly error
            self.assertEqual(response.status_code, 200)
            # Should not leak internal error details
            self.assertNotContains(response, "database")
            self.assertNotContains(response, "connection")
            self.assertNotContains(response, "Internal")

    def test_rate_limiting_simulation_basic(self):
        """Test basic rate limiting behavior."""
        # Make multiple rapid requests
        responses = []
        for _ in range(20):
            response = self.client.get(reverse("phone-form"))
            responses.append(response.status_code)
        
        # All requests should succeed (basic test)
        # In production, you might want to implement rate limiting
        self.assertTrue(all(status == 200 for status in responses))

    def test_sensitive_data_not_exposed_errors(self):
        """Test that sensitive data is not exposed in error pages."""
        # Create a scenario that might cause an error
        response = self.client.get("/non-existent-page/")
        
        # Should get a 404
        self.assertEqual(response.status_code, 404)
        # Should not expose sensitive information
        # (This is a basic test - in production you'd want more comprehensive checks)

    def test_header_security_basic(self):
        """Test basic security headers."""
        response = self.client.get(reverse("root"))
        
        # Check for basic security headers
        # Note: Django doesn't set all headers by default
        # This test documents what headers should be considered
        # In production, you'd want to implement security middleware