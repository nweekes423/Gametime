from django.contrib import admin
from django.urls import include, path

from game_monitor.views import root_view  # Import the root view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", root_view, name="root"),  # Add the root view URL pattern
    path("game-monitor/", include("game_monitor.urls")),
    # You can add more apps' URLs here
]
