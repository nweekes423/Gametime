from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from . import views  # Import views from this app
from .api_views import GameViewSet, UserPhoneViewSet
from .views import test_cache_view

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'games', GameViewSet, basename='game')
router.register(r'phones', UserPhoneViewSet, basename='userphone')

urlpatterns = [
    # API Documentation URLs (root level for easy access)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API URLs
    path('api/', include(router.urls)),
    
    # Existing URLs
    path(
        "mock-api/", views.mock_nba_api, name="mock-nba-api"
    ),  # App specific URL pattern
    path("phone-form/", views.phone_view, name="phone-form"),  # Corrected view name
    path("test-cache/", test_cache_view, name="test_cache"),
    path("success/", views.success_view, name="success-page"),  # Added success page URL
    # path("game-monitor/", include("game_monitor.urls")),
    # Add other URL patterns specific to this app here
]
