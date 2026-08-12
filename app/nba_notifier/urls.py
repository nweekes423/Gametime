from django.contrib import admin
from django.urls import include, path

from game_monitor.views import games_view, root_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("games/", games_view, name="games"),
    path("", root_view, name="root"),
    path("game-monitor/", include("game_monitor.urls")),
]
