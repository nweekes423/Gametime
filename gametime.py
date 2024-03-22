import logging
from nba_api.live.nba.endpoints import scoreboard
import time

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_close_games():
    try:
        # Fetching today's scoreboard
        games = scoreboard.ScoreBoard().get_dict()

        close_games = []

        for game in games['scoreboard']['games']:
            # Check if the game is in the last 5 minutes of the 4th period
            if game['period'] == 4 and parse_time(game['gameClock']) <= 5:
                # Check if the score difference is 6 points or fewer
                score_diff = abs(game['homeTeam']['score'] - game['awayTeam']['score'])
                if score_diff <= 6:
                    close_games.append(game)
                    logging.info(f"Close game found: {game}")

        return close_games

    except Exception as e:
        logging.error("Error while checking for close games: %s", e)
        return []

def parse_time(game_clock):
    try:
        # Parses the game clock string and returns the minutes
        minutes, seconds = game_clock.split(':')
        return int(minutes)
    except Exception as e:
        logging.error("Error while parsing game clock: %s", e)
        return 0

# Monitoring the games (example: check every 30 seconds)
while True:
    try:
        close_games = check_close_games()
        if not close_games:
            logging.info("No close games at the moment.")
        time.sleep(30)  # Wait for 30 seconds before checking again
    except KeyboardInterrupt:
        logging.info("Stopped monitoring games.")
        break
    except Exception as e:
        logging.error("Error during monitoring: %s", e)
        time.sleep(30)  # Wait before retrying in case of error

