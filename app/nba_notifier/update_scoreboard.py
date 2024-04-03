import json

import requests
from nba_api.live.nba.endpoints import scoreboard


def fetch_and_update_scoreboard():
    """
    Fetches live NBA data and updates the scoreboard.json file.
    This function can be deployed as a cloud function.
    """
    try:
        # Fetching live data
        games = scoreboard.ScoreBoard()
        data = games.get_dict()

        # Saving to scoreboard.json
        with open("scoreboard.json", "w") as file:
            json.dump(data, file)

        print("Scoreboard updated successfully.")

    except Exception as e:
        print(f"Error updating scoreboard: {e}")


# For local execution
if __name__ == "__main__":
    fetch_and_update_scoreboard()
    # For cloud deployment, the above line can be triggered by a cloud
