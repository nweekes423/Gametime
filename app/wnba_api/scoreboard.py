import requests

ESPN_WNBA_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard"
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.espn.com/",
    "Origin": "https://www.espn.com",
}


def get_scoreboard():
    response = requests.get(
        ESPN_WNBA_URL,
        headers=HEADERS,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def clock_to_duration(clock):
    """
    Convert ESPN's MM:SS clock format into the ISO-style
    duration format expected by Gametime's existing logic.

    Examples:
        5:32 -> PT5M32S
        0:45 -> PT0M45S
        10:00 -> PT10M0S
    """

    try:
        minutes, seconds = str(clock).split(":")

        minutes = int(minutes)
        seconds = int(float(seconds))

    except (ValueError, AttributeError):
        return "PT0M0S"

    return f"PT{minutes}M{seconds}S"


def convert_to_nba_format(data):
    """
    Convert ESPN WNBA scoreboard data into the structure
    expected by the existing Gametime game-monitor logic.
    """

    games = []

    for event in data.get("events", []):
        competition = event["competitions"][0]
        competitors = competition["competitors"]
        status = competition["status"]

        home = next(team for team in competitors if team["homeAway"] == "home")

        away = next(team for team in competitors if team["homeAway"] == "away")

        game = {
            "homeTeam": {
                "teamName": home["team"]["displayName"],
                "score": int(home.get("score", 0)),
            },
            "awayTeam": {
                "teamName": away["team"]["displayName"],
                "score": int(away.get("score", 0)),
            },
            "gameClock": clock_to_duration(status.get("displayClock", "0:00")),
            "period": status.get("period", 0),
            "status": status.get("type", {}).get("name"),
            "gameId": event.get("id"),
        }

        games.append(game)

    return {"scoreboard": {"games": games}}
