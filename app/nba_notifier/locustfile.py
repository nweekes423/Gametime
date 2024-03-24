import random

from bs4 import BeautifulSoup
from locust import HttpUser, between, task


class WebUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        """On start, get the CSRF token."""
        self.csrf_token = self.get_csrf_token("/game-monitor/phone-form/")

    def get_csrf_token(self, url):
        """Fetch the CSRF token from a specified URL."""
        response = self.client.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Extract CSRF token from the HTML content
        csrf_token = self.extract_csrf_token(response.text)
        return csrf_token

    def extract_csrf_token(self, html_content):
        """Extract CSRF token from HTML."""
        soup = BeautifulSoup(html_content, "html.parser")
        token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
        return token

    @task(2)
    def view_mock_api(self):
        """Simulate users viewing the mock API endpoint."""
        self.client.get("/game-monitor/mock-api/")

    @task(1)
    def submit_phone_form(self):
        """Simulate submitting a phone number through the form."""
        phone_number = f"+{random.randint(1000000000, 9999999999)}"
        self.client.post(
            "/game-monitor/phone-form/",
            {"csrfmiddlewaretoken": self.csrf_token, "phone_number": phone_number},
            headers={"Referer": "/game-monitor/phone-form/"},
        )

    @task(1)
    def view_success_page(self):
        """Simulate users viewing the success page."""
        self.client.get("/game-monitor/success/")
