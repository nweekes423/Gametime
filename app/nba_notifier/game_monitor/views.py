import json
import os
import re
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from nba_api.live.nba.endpoints import scoreboard
from prometheus_client import CollectorRegistry, generate_latest, Gauge, CONTENT_TYPE_LATEST

from game_monitor.forms import PhoneForm
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
                messages.success(
                    request, "New phone number registered."
                )
            else:
                print("Phone number already exists.")
                messages.warning(
                    request, "Phone number already exists!"
                )
            return redirect("success-page")
        else:
            print("[+] Form is not valid")
            messages.error(
                request, "There was an error with your submission."
            )
            print(form.errors)  # Add this line for debugging
            return render(request, "phone-form.html", {"form": form})
    else:
        form = PhoneForm()

    return render(request, "phone-form.html", {"form": form})




def success_view(request):
    # Render a simple success page (you'll need to create this template)

    return render(request, "success.html")


def parse_duration(duration_str):
    """Parse ISO 8601 duration string into minutes and seconds."""
    match = re.match(r"PT(\d+)M(\d+\.?\d*)S", duration_str)
    if match:
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        return minutes, seconds
    else:
        return 0, 0


def parse_time(game_clock):
    # Assuming game_clock format is "MM:SS"
    minutes, seconds = map(int, game_clock.split(":"))
    return minutes + seconds / 60


def is_close_game(game):
    """Check if the game is within a 10-point margin and under 8 minutes left."""
    try:
        home_score = game["homeTeam"]["score"]
        away_score = game["awayTeam"]["score"]
        point_difference = abs(home_score - away_score)

        game_clock = game["gameClock"]
        minutes, seconds = parse_duration(game_clock)
        time_left = minutes + seconds / 60

        if point_difference <= 10 and time_left <= 8 and game["period"] >= 4:
            print(
                f"Close game detected: {game['homeTeam']['teamName']} vs {game['awayTeam']['teamName']}"
            )
            print(
                f"Score: {home_score} - {away_score}, Time Left: {minutes}m {seconds}s"
            )
            return True

        return False

    except KeyError:
        # In case any key is missing, which can happen for pre-game or post-game data
        return False


def fetch_and_update_scoreboard():
    """Fetches live NBA data and checks for close games."""
    try:
        # Fetching live data
        games = scoreboard.ScoreBoard()
        data = games.get_dict()

        # Check each game
        close_games = [game for game in data["scoreboard"]["games"] if is_close_game(game)]
        QUEUE_SIZE_GAUGE.set(len(close_games))

        # Send sms to all registered users
        for user_phone in UserPhone.objects.all():
            send_text_message(user_phone.phone_number, "Close game detected!")

        # Saving to scoreboard.json
        with open("scoreboard.json", "w") as file:
            json.dump(data, file)

        print("Scoreboard updated successfully.")

    except Exception as e:
        print(f"Error updating scoreboard: {e}")


def prometheus_metrics(request):
    # Expose metrics endpoint (NEW)
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    fetch_and_update_scoreboard()
