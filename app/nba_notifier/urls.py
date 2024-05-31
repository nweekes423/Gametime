from django.contrib import admin
from django.urls import include, path
#from game_monitor.views import my_view, prometheus_metrics

from game_monitor.views import root_view  # Import the root view
from game_monitor.views import games_view
from app.send_sms import send_sms

urlpatterns = [
    path("admin/", admin.site.urls),
    path('games/', games_view, name='games'),
    path("", root_view, name="root"),  # Add the root view URL pattern
    path("game-monitor/", include("game_monitor.urls")),
   #path('metrics/', prometheus_metrics, name='prometheus-metrics'),
    path('send-sms/', send_sms),

    # You can add more apps' URLs here
]
