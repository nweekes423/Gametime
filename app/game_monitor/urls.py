from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from . import views  # Import views from this app
from .api_views import GameViewSet, UserPhoneViewSet
from .views import health_check

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'games', GameViewSet, basename='game')
router.register(r'phones', UserPhoneViewSet, basename='userphone')

urlpatterns = [
    # Health check endpoint
    path('health/', health_check, name='health_check'),
    
    # API Documentation URLs (root level for easy access)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API URLs
    path('api/', include(router.urls)),
    
    # Existing URLs
    path("phone-form/", views.phone_view, name="phone-form"),  # Corrected view name
    path("success/", views.success_view, name="success-page"),  # Added success page URL
    # path("game-monitor/", include("game_monitor.urls")),
    # Add other URL patterns specific to this app here
]
