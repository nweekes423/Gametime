"""NBA scoreboard retrieval with an ESPN fallback for blocked NBA CDN requests."""

import logging

import requests
from nba_api.live.nba.endpoints import scoreboard

from wnba_api.scoreboard import HEADERS, convert_to_nba_format

logger = logging.getLogger(__name__)

ESPN_NBA_URL = (
    "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
)


def get_scoreboard():
    """Return NBA games in the application's existing scoreboard format."""
    try:
        return scoreboard.ScoreBoard().get_dict()
    except (KeyError, TypeError, ValueError, requests.RequestException) as exc:
        logger.warning(
            "[NBA] Official scoreboard unavailable (%s); using ESPN fallback.",
            exc,
        )

    response = requests.get(ESPN_NBA_URL, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return convert_to_nba_format(response.json())
