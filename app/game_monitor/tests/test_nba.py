from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from game_monitor.nba import get_scoreboard


class NbaScoreboardTests(SimpleTestCase):
    @patch("game_monitor.nba.requests.get")
    @patch("game_monitor.nba.scoreboard.ScoreBoard")
    def test_uses_espn_when_official_scoreboard_is_invalid(
        self,
        mock_scoreboard,
        mock_get,
    ):
        mock_scoreboard.side_effect = ValueError("invalid response")
        response = MagicMock()
        response.json.return_value = {
            "events": [
                {
                    "id": "1",
                    "competitions": [
                        {
                            "competitors": [
                                {
                                    "homeAway": "home",
                                    "score": "100",
                                    "team": {"displayName": "Home"},
                                },
                                {
                                    "homeAway": "away",
                                    "score": "95",
                                    "team": {"displayName": "Away"},
                                },
                            ],
                            "status": {"displayClock": "5:30", "period": 4},
                        }
                    ],
                }
            ]
        }
        mock_get.return_value = response

        result = get_scoreboard()

        response.raise_for_status.assert_called_once()
        self.assertEqual(result["scoreboard"]["games"][0]["homeTeam"]["score"], 100)
        self.assertEqual(result["scoreboard"]["games"][0]["gameClock"], "PT5M30S")
