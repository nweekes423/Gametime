from django.urls import path

from . import views  # Import views from this app
from django.urls import path, include


urlpatterns = [
    path(
        "mock-api/", views.mock_nba_api, name="mock-nba-api"
    ),  # App specific URL pattern
    # Corrected view name
    path("phone-form/", views.phone_view, name="phone-form"),
    # Added success page URL
    path("success/", views.success_view, name="success-page"),
    # NEW: Endpoint for Prometheus metrics
    path("metrics/", views.prometheus_metrics, name="prometheus-metrics"),

    #path("game-monitor/", include("game_monitor.urls")),

    # Add other URL patterns specific to this app here
]
