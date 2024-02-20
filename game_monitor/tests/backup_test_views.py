from django.test import Client, TestCase
from django.urls import reverse

from game_monitor.forms import PhoneForm
from game_monitor.models import UserPhone


class PhoneViewTests(TestCase):
    def test_phone_view_post_valid(self):
        # Test POST request with valid data
        response = self.client.post(
            reverse("phone-form"), {"phone_number": "+1234567890"}
        )
        self.assertRedirects(response, reverse("success-page"))
        self.assertEqual(UserPhone.objects.count(), 1)

    def test_phone_view_post_invalid(self):
        # Test POST request with invalid data
        response = self.client.post(
            reverse("phone-form"), {"phone_number": "invalid_number"}
        )
        self.assertEqual(
            response.status_code, 200
        )  # Form not valid, should stay on the same page
        self.assertEqual(UserPhone.objects.count(), 0)
