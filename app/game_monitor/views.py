import json
import os
import re
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from nba_api.live.nba.endpoints import scoreboard
from game_monitor.forms import PhoneForm
from .models import UserPhone
from .utils import send_text_message
from django.core.cache import cache
import time
# In game_monitor/views.py
from django.shortcuts import render

def test_cache_view(request):
    start_time = time.time()
    data = cache.get('test_data')
    if not data:
        # Simulate a time-consuming process
        data = {'message': 'This is a test data'}
        time.sleep(2)  # Simulate delay
        cache.set('test_data', data, timeout=60 * 15)
        fetch_source = 'Generated'
    else:
        fetch_source = 'Cache'
    
    end_time = time.time()
    response = {
        'data': data,
        'fetch_source': fetch_source,
        'elapsed_time': end_time - start_time,
    }
    return JsonResponse(response)



def games_view(request):
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


"""
def is_game_close(game_data):
    # Check if it's the 3rd or 4th quarter and time is less than 5 minutes
    if game_data['period'] in [3, 4] and parse_time(game_data['gameClock']) < 5:
        # Check if the score difference is 5 points or fewer
        score_diff = abs(game_data['homeTeam']['score'] - game_data['awayTeam']['score'])
        return score_diff <= 5
    return False
"""


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
        for game in data["scoreboard"]["games"]:
            if is_close_game(game):
                message_body = f"Close game {game['homeTeam']['teamName']} vs {game['awayTeam']['teamName']} - Score: {game['homeTeam']['score']} - {game['awayTeam']['score']}"
                # Send sms to all registered users
                for user_phone in UserPhone.objects.all():
                    send_text_message(user_phone.phone_number, message_body)
                print(
                    f"Close game detected: {game['homeTeam']['teamName']} vs {game['awayTeam']['teamName']}"
                )
                # You can add more logic here, like notifications

        # Saving to scoreboard.json
        with open("scoreboard.json", "w") as file:
            json.dump(data, file)

        print("Scoreboard updated successfully.")

    except Exception as e:
        print(f"Error updating scoreboard: {e}")


if __name__ == "__main__":
    fetch_and_update_scoreboard()


def mock_nba_api(request):
    file_path = os.path.join(os.path.dirname(__file__), "scoreboard.json")

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        close_games = [
            game for game in data["scoreboard"]["games"] if is_close_game(game)
        ]
        close_games_info = [
            {
                "home_team": game["homeTeam"]["teamName"],
                "away_team": game["awayTeam"]["teamName"],
                "score": f"{game['homeTeam']['score']} - {game['awayTeam']['score']}",
                "time_left": game["gameClock"],
            }
            for game in close_games
        ]

        return JsonResponse({"close_games": close_games_info})

    except FileNotFoundError:
        return JsonResponse({"error": "File not found"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=500)
