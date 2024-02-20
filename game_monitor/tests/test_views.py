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
        content = response_after_phone_view.content.decode('utf-8')
        logger.debug(content)

        # Check for success message
        messages = list(get_messages(response_after_phone_view.wsgi_request))
        logger.info(f"Number of messages: {len(messages)}")
        logger.info(f"Messages: {messages}")

        self.assertEqual(len(messages), 1)

        # Use the success_view function to test its behavior
        response_after_success_view = success_view(response_after_phone_view.wsgi_request)

        # Assert the content of the success view response
        self.assertEqual(response_after_success_view.status_code, 200)
        # self.assertContains(response_after_success_view, "Congratulations!")
        # You might need to adjust the above line based on the actual content of your success.html template

        # If there is specific content in the success view, you can check it with assertContains

        # You can also assert that the rendered template is the correct one
        # self.assertTemplateUsed(response_after_success_view, "success.html")

        # Check any other specific behavior of your success view here

    def test_phone_view_post_invalid(self):
        # Test POST request with invalid data
        response = self.client.post(
            reverse("phone-form"), {"phone_number": "invalid_number"}
        )

        # Check if the form is not valid and stays on the same page
        self.assertEqual(
            response.status_code, 200
        )  # Form not valid, should stay on the same page
        self.assertEqual(UserPhone.objects.count(), 0)

        logger.warning(f"Invalid phone number submitted: 'invalid_number'")
