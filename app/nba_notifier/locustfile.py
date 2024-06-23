import random
import time
from bs4 import BeautifulSoup
from locust import HttpUser, between, task

class WebUser(HttpUser):
    wait_time = between(1, 5)
    csrf_token = None  # LOOK: Initialize csrf_token attribute

    def on_start(self):
        """On start, get the CSRF token."""
        self.csrf_token = self.get_csrf_token("/game-monitor/phone-form/")

    def get_csrf_token(self, url):
        """Fetch the CSRF token from a specified URL."""
        max_retries = 3
        for attempt in range(max_retries):
            response = self.client.get(url)
            if response.status_code == 200:
                csrf_token = self.extract_csrf_token(response.text)
                if csrf_token:
                    print(f"CSRF token fetched: {csrf_token}")
                    return csrf_token
            time.sleep(1)  # Wait before retrying
        raise Exception("Failed to fetch CSRF token after multiple attempts.")

    def extract_csrf_token(self, html_content):
        """Extract CSRF token from HTML."""
        soup = BeautifulSoup(html_content, "html.parser")
        token_tag = soup.find("input", {"name": "csrfmiddlewaretoken"})
        if token_tag:
            return token_tag["value"]
        return None

    @task(2)
    def view_mock_api(self):
        """Simulate users viewing the mock API endpoint."""
        response = self.client.get("/game-monitor/mock-api/")
        print(f"GET /game-monitor/mock-api/ status code: {response.status_code}")

    @task(1)
    def submit_phone_form(self):
        """Simulate submitting a phone number through the form."""
        phone_number = "+15105194907"  # Specific phone number
        response = self.client.post(
            "/game-monitor/phone-form/",  # LOOK: Ensure no extra slash here
            {
                "csrfmiddlewaretoken": self.csrf_token,
                "phone_number": phone_number,
            },
            headers={"Referer": "http://localhost:8000/game-monitor/phone-form/"}  # LOOK: Correct Referer URL
        )

        print(f"POST /game-monitor/phone-form/ response status: {response.status_code}")
        print(f"POST /game-monitor/phone-form/ response text: {response.text}")

        if response.status_code == 302:  # Assuming a successful submission redirects to success page
            self.csrf_token = self.get_csrf_token("/game-monitor/phone-form/")  # Refresh CSRF token

        # Add a wait time after the POST request
        time.sleep(random.uniform(0.5, 2.0))

    @task(1)
    def view_success_page(self):
        """Simulate users viewing the success page."""
        response = self.client.get("/game-monitor/success/")  # LOOK: Ensure no extra slash here
        print(f"GET /game-monitor/success/ status code: {response.status_code}")
