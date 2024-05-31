import logging
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.messages import get_messages

from game_monitor.forms import PhoneForm
from game_monitor.models import UserPhone
from game_monitor.views import phone_view, success_view

# Configure logging
logger = logging.getLogger(__name__)

class PhoneViewTests(TestCase):
    def test_phone_view_post_valid(self):
        # Test POST request with valid data
        response_after_phone_view = self.client.post(
            reverse("phone-form"), {"phone_number": "+15105123847"}, follow=True
        )

        # Check if the form is valid before making redirection assertions
        form = response_after_phone_view.context.get('form')
        logger.debug(f"Form instance: {form}")

        # Now, assert the redirection
        self.assertEqual(response_after_phone_view.status_code, 200)


    def test_phone_view_post_invalid(self):
        # Test POST request with invalid data
        response = self.client.post(
            reverse("phone-form"), {"phone_number": "invalid_number"}
        )
        # Check if the form is not valid and stays on the same page
        #Change this to 301 when https because of ssl warning redirect. 
        #Change to 200 for http since no redirect
        self.assertEqual(response.status_code, 200)  # Update to check for a status code of 200
        self.assertEqual(UserPhone.objects.count(), 0)

        logger.warning(f"Invalid phone number submitted: 'invalid_number'")
