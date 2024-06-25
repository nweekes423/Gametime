import json
from nba_api.live.nba.endpoints import scoreboard
from prometheus_client import Gauge

QUEUE_SIZE_GAUGE = Gauge('myapp_queue_size', 'Size of the Queue')


def fetch_and_update_scoreboard():
    try:
        games = scoreboard.ScoreBoard()
        data = games.get_dict()

        close_games = [game for game in data["scoreboard"]["games"] if is_close_game(game)]
        QUEUE_SIZE_GAUGE.set(len(close_games))

        for user_phone in UserPhone.objects.all():
            send_text_message(user_phone.phone_number, "Close game detected!")

        with open("scoreboard.json", "w") as file:
            json.dump(data, file)

        print("Scoreboard updated successfully.")

    except Exception as e:
        print(f"Error updating scoreboard: {e}")


def is_close_game(game):
    try:
        home_score = game["homeTeam"]["score"]
        away_score = game["awayTeam"]["score"]
        point_difference = abs(home_score - away_score)

        game_clock = game["gameClock"]
        minutes, seconds = parse_duration(game_clock)
        time_left = minutes + seconds / 60

        if point_difference <= 10 and time_left <= 8 and game["period"] >= 4:
            print(f"Close game detected: {game['homeTeam']['teamName']} vs {game['awayTeam']['teamName']}")
            print(f"Score: {home_score} - {away_score}, Time Left: {minutes}m {seconds}s")
            return True

        return False

    except KeyError:
        return False


def parse_duration(duration_str):
    match = re.match(r"PT(\d+)M(\d+\.?\d*)S", duration_str)
    if match:
        minutes = int(match.group(1))
        seconds = float(match.group(2))
        return minutes, seconds
    else:
        return 0, 0
