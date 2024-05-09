from django.http import HttpResponse
from prometheus_client import CollectorRegistry, generate_latest, Gauge

registry = CollectorRegistry()

# Define metrics for HTTP and HTTPS requests
http_requests_total = Gauge('http_requests_total', 'Total number of HTTP requests', registry=registry)
https_requests_total = Gauge('https_requests_total', 'Total number of HTTPS requests', registry=registry)

# Define metrics for redirection attempts and successes
redirection_attempts_total = Gauge('redirection_attempts_total', 'Total number of redirection attempts', registry=registry)
redirection_successes_total = Gauge('redirection_successes_total', 'Total number of successful redirections', registry=registry)

def prometheus_metrics(request):
    # Increment HTTP or HTTPS request metric based on request scheme
    if request.scheme == 'http':
        http_requests_total.inc()
    elif request.scheme == 'https':
        https_requests_total.inc()

    # Check if the request is redirected from HTTP to HTTPS
    if request.scheme == 'http':
        redirection_attempts_total.inc()
        # Logic to check if redirection was successful and increment redirection_successes_total accordingly

    # Generate the latest metrics in the Prometheus text-based format
    response = HttpResponse(content_type='text/plain')
    response.write(generate_latest(registry))
    return response

