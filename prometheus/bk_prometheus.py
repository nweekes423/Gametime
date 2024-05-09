from django.http import HttpResponse
from prometheus_client import CollectorRegistry, generate_latest, Gauge

registry = CollectorRegistry()

# Define a gauge metric
requests_total = Gauge('http_requests_total', 'Total number of HTTP requests', registry=registry)

def prometheus_metrics(request):
    # Update the gauge metric
    requests_total.set(10)

    # Generate the latest metrics in the Prometheus text-based format
    response = HttpResponse(content_type='text/plain')
    response.write(generate_latest(registry))
    return response
