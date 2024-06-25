from django.urls import path

from . import views  # Import views from this app
from django.urls import path, include

from django.urls import path
from .views import test_cache_view




urlpatterns = [
    path(
        "mock-api/", views.mock_nba_api, name="mock-nba-api"
    ),  # App specific URL pattern
    path("phone-form/", views.phone_view, name="phone-form"),  # Corrected view name
    path('test-cache/', test_cache_view, name='test_cache'),
    path("success/", views.success_view, name="success-page"),  # Added success page URL
    #path("game-monitor/", include("game_monitor.urls")),

    # Add other URL patterns specific to this app here
]
