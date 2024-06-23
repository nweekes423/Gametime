from locust import HttpUser, between, task
from bs4 import BeautifulSoup

class WebUser(HttpUser):
    wait_time = between(1, 5)
    csrf_token = None

    def on_start(self):
        """On start, fetch the CSRF token."""
        self.fetch_csrf_token()

    def fetch_csrf_token(self):
        """Fetch CSRF token from the form page."""
        # LOOK: Fetch CSRF token by making a GET request to the form page
        response = self.client.get("/game-monitor/phone-form/")
        if response.status_code == 200:
            self.csrf_token = self.extract_csrf_token(response.text)
            if not self.csrf_token:
                raise ValueError("CSRF token not found in response")

    def extract_csrf_token(self, html_content):
        """Extract CSRF token from HTML."""
        # LOOK: Extract CSRF token from HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        token_tag = soup.find("input", {"name": "csrfmiddlewaretoken"})
        if token_tag:
            return token_tag["value"]
        return None

    @task(1)
    def view_mock_api(self):
        """Simulate users viewing the mock API endpoint."""
        response = self.client.get("/game-monitor/mock-api/")
        print(f"GET /game-monitor/mock-api/ status code: {response.status_code}")

    @task(2)
    def submit_phone_form(self):
        """Simulate submitting a phone number through the form."""
        if not self.csrf_token:
            self.fetch_csrf_token()

        phone_number = "+12125552368"  # Replace with your test data
        # LOOK: Make a POST request to submit the phone form with CSRF token
        response = self.client.post(
            "/game-monitor/phone-form/",
            {
                "csrfmiddlewaretoken": self.csrf_token,
                "phone_number": phone_number,
            },
            headers={"Referer": "http://localhost:8000/game-monitor/phone-form/"}
        )

        print(f"POST /game-monitor/phone-form/ status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response text: {response.text}")

        # LOOK: Refresh CSRF token after form submission to prevent stale token usage
        if response.status_code == 200:
            self.fetch_csrf_token()

    @task(1)
    def view_success_page(self):
        """Simulate users viewing the success page."""
        response = self.client.get("/game-monitor/success/")
        print(f"GET /game-monitor/success/ status code: {response.status_code}")

        # LOOK: Fetch a new CSRF token after viewing the success page to ensure it is up-to-date
        if response.status_code == 200:
            self.fetch_csrf_token()

