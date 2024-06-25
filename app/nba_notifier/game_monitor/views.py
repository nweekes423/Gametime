import json
import re
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from nba_api.live.nba.endpoints import scoreboard
from prometheus_client import generate_latest, Gauge, CONTENT_TYPE_LATEST

from .forms import PhoneForm
from .models import UserPhone
from .utils import send_text_message

# Define Prometheus metrics
REQUEST_COUNTER = Gauge('myapp_http_requests_total', 'Total HTTP Requests')
QUEUE_SIZE_GAUGE = Gauge('myapp_queue_size', 'Size of the Queue')


def games_view(request):
    REQUEST_COUNTER.inc()
    try:
        games = scoreboard.ScoreBoard()
        data = games.get_dict()

        game_info = [
            {
                "home_team": game["homeTeam"]["teamName"],
                "away_team": game["awayTeam"]["teamName"],
                "score": f"{game['homeTeam']['score']} - {game['awayTeam']['score']}",
                "time_left": game["gameClock"],
            }
            for game in data["scoreboard"]["games"]
        ]
        return render(request, 'game_template.html', {'games_info': game_info})
    except Exception as e:
        print(f"Error fetching games: {e}")
        # Log error
        return render(request, 'error_template.html', {'error_message': 'No games available'})


def root_view(request):
    return render(request, "root.html")


def phone_view(request):
    if request.method == "POST":
        form = PhoneForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            user_phone, created = UserPhone.objects.get_or_create(
                phone_number=phone_number
            )
            if created:
                print("New phone number registered.")
                messages.success(request, "New phone number registered.")
            else:
                print("Phone number already exists.")
                messages.warning(request, "Phone number already exists!")
            return redirect("success-page")
        else:
            print("[+] Form is not valid")
            messages.error(request, "There was an error with your submission.")
            print(form.errors)  # Add this line for debugging
            return render(request, "phone-form.html", {"form": form})
    else:
        form = PhoneForm()
    return render(request, "phone-form.html", {"form": form})


def success_view(request):
    return render(request, "success.html")


def prometheus_metrics(request):
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)
