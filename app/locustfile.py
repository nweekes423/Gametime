from locust import HttpUser, between, task, events
from bs4 import BeautifulSoup
from prometheus_client import start_http_server, Gauge, Counter
import time

# Prometheus metrics
REQUEST_LATENCY = Gauge('locust_request_latency_seconds', 'Request latency in seconds', ['method', 'endpoint'])
REQUEST_COUNT = Counter('locust_request_count', 'Request count', ['method', 'endpoint', 'status'])

class WebUser(HttpUser):
    wait_time = between(1, 5)
    csrf_token = None

    def on_start(self):
        """On start, fetch the CSRF token."""
        self.fetch_csrf_token()

    def fetch_csrf_token(self):
        """Fetch CSRF token from the form page."""
        response = self.client.get("/game-monitor/phone-form/")
        if response.status_code == 200:
            self.csrf_token = self.extract_csrf_token(response.text)
            if not self.csrf_token:
                raise ValueError("CSRF token not found in response")

    def extract_csrf_token(self, html_content):
        """Extract CSRF token from HTML."""
        soup = BeautifulSoup(html_content, "html.parser")
        token_tag = soup.find("input", {"name": "csrfmiddlewaretoken"})
        if token_tag:
            return token_tag["value"]
        return None

    @task(1)
    def view_mock_api(self):
        """Simulate users viewing the mock API endpoint."""
        start_time = time.time()
        response = self.client.get("/game-monitor/mock-api/")
        latency = time.time() - start_time
        REQUEST_LATENCY.labels('GET', '/game-monitor/mock-api/').set(latency)
        REQUEST_COUNT.labels('GET', '/game-monitor/mock-api/', response.status_code).inc()
        print(f"GET /game-monitor/mock-api/ status code: {response.status_code}")

    @task(2)
    def submit_phone_form(self):
        """Simulate submitting a phone number through the form."""
        if not self.csrf_token:
            self.fetch_csrf_token()

        phone_number = "+12125552368"  # Replace with your test data
        start_time = time.time()
        response = self.client.post(
            "/game-monitor/phone-form/",
            {
                "csrfmiddlewaretoken": self.csrf_token,
                "phone_number": phone_number,
            },
            headers={"Referer": "http://localhost:8000/game-monitor/phone-form/"}
        )
        latency = time.time() - start_time
        REQUEST_LATENCY.labels('POST', '/game-monitor/phone-form/').set(latency)
        REQUEST_COUNT.labels('POST', '/game-monitor/phone-form/', response.status_code).inc()
        print(f"POST /game-monitor/phone-form/ status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response text: {response.text}")

        if response.status_code == 200:
            self.fetch_csrf_token()

    @task(1)
    def view_success_page(self):
        """Simulate users viewing the success page."""
        start_time = time.time()
        response = self.client.get("/game-monitor/success/")
        latency = time.time() - start_time
        REQUEST_LATENCY.labels('GET', '/game-monitor/success/').set(latency)
        REQUEST_COUNT.labels('GET', '/game-monitor/success/', response.status_code).inc()
        print(f"GET /game-monitor/success/ status code: {response.status_code}")

        if response.status_code == 200:
            self.fetch_csrf_token()

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    # Start up the server to expose the metrics.
    start_http_server(8000)

