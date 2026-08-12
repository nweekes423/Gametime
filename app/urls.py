from django.contrib import admin
from django.urls import include, path

import send_sms
from game_monitor.views import (
    games_view,
    root_view,  # Import the root view
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("games/", games_view, name="games"),
    path("", root_view, name="root"),  # Add the root view URL pattern
    path("game-monitor/", include("game_monitor.urls")),
    path("send-sms/", send_sms.send_sms),
    # You can add more apps' URLs here
]
