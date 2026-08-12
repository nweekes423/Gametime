import json
import logging
import os
import re
import time

from django.contrib import messages
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render

from game_monitor.forms import PhoneForm
from game_monitor.nba import get_scoreboard as get_nba_scoreboard

from .models import UserPhone
from .utils import send_text_message

logger = logging.getLogger(__name__)


def test_cache_view(request):
    """Test Django cache performance."""
    start_time = time.time()
    data = cache.get("test_data")

    if not data:
        data = {"message": "This is a test data"}
        time.sleep(2)
        cache.set("test_data", data, timeout=60 * 15)
        fetch_source = "Generated"
    else:
        fetch_source = "Cache"

    end_time = time.time()

    response = {
        "data": data,
        "fetch_source": fetch_source,
        "elapsed_time": end_time - start_time,
    }

    return JsonResponse(response)


def games_view(request):
    """Display current NBA games."""
    try:
        data = get_nba_scoreboard()

        game_info = [
            {
                "home_team": game["homeTeam"]["teamName"],
                "away_team": game["awayTeam"]["teamName"],
                "score": (f"{game['homeTeam']['score']} - {game['awayTeam']['score']}"),
                "time_left": game["gameClock"],
            }
            for game in data["scoreboard"]["games"]
        ]

    except (KeyError, TypeError, ValueError):
        logger.exception("Error parsing NBA scoreboard.")
        return render(
            request,
            "error_template.html",
            {"error_message": "No games available"},
        )

    except Exception:
        logger.exception("Unexpected error fetching NBA games.")
        return render(
            request,
            "error_template.html",
            {"error_message": "No games available"},
        )

    return render(
        request,
        "game_template.html",
        {"games_info": game_info},
    )


def root_view(request):
    """Render the application home page."""
    return render(request, "root.html")


def phone_view(request):
    """Register a user's phone number for SMS notifications."""
    form = PhoneForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]

            _, created = UserPhone.objects.get_or_create(
                phone_number=phone_number
            )

            if created:
                logger.info("New phone number registered.")
                messages.success(
                    request,
                    "New phone number registered.",
                )
            else:
                logger.info("Phone number already exists.")
                messages.warning(
                    request,
                    "Phone number already exists!",
                )

            return redirect("success-page")

        logger.warning("Phone registration form is invalid.")

    return render(request, "phone-form.html", {"form": form})


def success_view(request):
    """Render the phone registration success page."""
    return render(request, "success.html")


def parse_duration(duration_str):
    """Parse an ISO 8601 duration into minutes and seconds."""
    match = re.match(r"PT(\d+)M(\d+(?:\.\d+)?)S", duration_str)

    if match:
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        return minutes, seconds

    return 0, 0


def parse_time(game_clock):
    """Convert an MM:SS game clock into minutes."""
    minutes, seconds = map(int, game_clock.split(":"))
    return minutes + seconds / 60


def is_close_game(game):
    """
    Determine whether a game meets the close-game notification criteria.

    Criteria:
    - Fourth quarter or later
    - 10 points or fewer separating the teams
    - 8 minutes or less remaining
    """
    try:
        home_score = game["homeTeam"]["score"]
        away_score = game["awayTeam"]["score"]
        point_difference = abs(home_score - away_score)

        game_clock = game["gameClock"]
        minutes, seconds = parse_duration(game_clock)
        time_left = minutes + seconds / 60

        is_close = point_difference <= 10 and time_left <= 8 and game["period"] >= 4

    except (KeyError, TypeError, ValueError):
        logger.warning("Unable to evaluate game data.")
        return False

    if is_close:
        logger.info(
            "Close game detected: %s vs %s",
            game["homeTeam"]["teamName"],
            game["awayTeam"]["teamName"],
        )
        logger.info(
            "Score: %s - %s, Time Left: %sm %ss",
            home_score,
            away_score,
            minutes,
            seconds,
        )

    return is_close


def _send_close_game_notifications(game, league):
    """Send an SMS notification to all registered users."""
    message_body = (
        f"{league} close game "
        f"{game['homeTeam']['teamName']} vs "
        f"{game['awayTeam']['teamName']} - Score: "
        f"{game['homeTeam']['score']} - "
        f"{game['awayTeam']['score']}"
    )

    for user_phone in UserPhone.objects.all():
        send_text_message(
            user_phone.phone_number,
            message_body,
        )


def fetch_and_update_scoreboard():
    """Fetch NBA and WNBA scoreboards and notify users of close games."""
    nba_data = None
    wnba_data = None

    # ---------------------------------
    # NBA
    # ---------------------------------
    try:
        logger.info("[NBA] Fetching scoreboard...")

        nba_data = get_nba_scoreboard()

        logger.info(
            "[NBA] Successfully fetched %s games.",
            len(nba_data["scoreboard"]["games"]),
        )

        for game in nba_data["scoreboard"]["games"]:
            if is_close_game(game):
                _send_close_game_notifications(game, "NBA")

    except (KeyError, TypeError, ValueError):
        logger.exception("[NBA] Error parsing scoreboard.")

    except Exception:
        logger.exception("[NBA] Unexpected error fetching scoreboard.")

    # ---------------------------------
    # WNBA
    # ---------------------------------
    try:
        logger.info("[WNBA] Fetching scoreboard...")

        from wnba_api.scoreboard import (
            convert_to_nba_format,
            get_scoreboard,
        )

        wnba_raw_data = get_scoreboard()
        wnba_data = convert_to_nba_format(wnba_raw_data)

        logger.info(
            "[WNBA] Successfully fetched %s games.",
            len(wnba_data["scoreboard"]["games"]),
        )

        for game in wnba_data["scoreboard"]["games"]:
            if is_close_game(game):
                _send_close_game_notifications(game, "WNBA")

    except (KeyError, TypeError, ValueError):
        logger.exception("[WNBA] Error parsing scoreboard.")

    except Exception:
        logger.exception("[WNBA] Unexpected error fetching scoreboard.")

    # ---------------------------------
    # Save scoreboards separately
    # ---------------------------------
    if nba_data is not None:
        try:
            with open("scoreboard.json", "w", encoding="utf-8") as file:
                json.dump(nba_data, file, indent=2)

            logger.info("[NBA] scoreboard.json updated.")

        except (OSError, TypeError, ValueError):
            logger.exception("[NBA] Error saving scoreboard.json.")

    if wnba_data is not None:
        try:
            with open(
                "wnba_scoreboard.json",
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(wnba_data, file, indent=2)

            logger.info("[WNBA] wnba_scoreboard.json updated.")

        except (OSError, TypeError, ValueError):
            logger.exception("[WNBA] Error saving wnba_scoreboard.json.")

    logger.info("Scoreboard update complete.")


if __name__ == "__main__":
    fetch_and_update_scoreboard()


def mock_nba_api(request):
    """Return close games from the local scoreboard fixture."""
    file_path = os.path.join(
        os.path.dirname(__file__),
        "scoreboard.json",
    )

    try:
        with open(file_path, encoding="utf-8") as file:
            data = json.load(file)

        close_games = [
            game for game in data["scoreboard"]["games"] if is_close_game(game)
        ]

        close_games_info = [
            {
                "home_team": game["homeTeam"]["teamName"],
                "away_team": game["awayTeam"]["teamName"],
                "score": (f"{game['homeTeam']['score']} - {game['awayTeam']['score']}"),
                "time_left": game["gameClock"],
            }
            for game in close_games
        ]

    except FileNotFoundError:
        return JsonResponse(
            {"error": "File not found"},
            status=404,
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=500,
        )
    except KeyError:
        return JsonResponse(
            {"error": "Invalid scoreboard structure"},
            status=500,
        )

    return JsonResponse({"close_games": close_games_info})


def health_check(request):
    """Health check endpoint for Docker health checks and monitoring."""
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {e!s}"
    
    # Check cache connection
    try:
        cache.set("health_check", "ok", timeout=10)
        cache.get("health_check")
        cache_status = "healthy"
    except Exception as e:
        cache_status = f"unhealthy: {e!s}"
    
    health_data = {
        "status": "healthy" if db_status == "healthy" and cache_status == "healthy" else "unhealthy",
        "database": db_status,
        "cache": cache_status,
        "timestamp": time.time(),
    }
    
    status_code = 200 if health_data["status"] == "healthy" else 503
    return JsonResponse(health_data, status=status_code)
