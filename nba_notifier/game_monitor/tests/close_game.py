# Import necessary modules
import logging

from game_monitor.utils import parse_duration  # Import the parse_duration function
from game_monitor.utils import send_text_message

# Add this line to configure the logging settings
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


def is_close_game(game):
    """Check if the game is within a 10-point margin and under 8 minutes left."""
    try:
        # Extract relevant information from the game data
        home_score = game["homeTeam"]["score"]
        away_score = game["awayTeam"]["score"]
        point_difference = abs(home_score - away_score)

        game_clock = game["gameClock"]
        minutes, seconds = parse_duration(game_clock)
        time_left = minutes + seconds / 60

        # Check if the conditions for a close game are met
        if point_difference <= 10 and time_left <= 8 and game["period"] >= 4:
            # Log a verbose message indicating that a close game is detected
            logging.debug(
                f"Close game detected: {game['homeTeam']['teamName']} vs {game['awayTeam']['teamName']}"
            )
            logging.debug(
                f"Score: {home_score} - {away_score}, Time Left: {minutes}m {seconds}s"
            )

            # Send text message to all registered users
            message_body = f"Close game {game['homeTeam']['teamName']} vs {game['awayTeam']['teamName']} - Score: {home_score} - {away_score}"
            for user_phone in UserPhone.objects.all():
                try:
                    send_text_message(user_phone.phone_number, message_body)
                    logging.info(f"Text message sent to {user_phone.phone_number}")
                except Exception as e:
                    # Log an error if there's an issue sending the text message
                    logging.error(
                        f"Error sending text message to {user_phone.phone_number}: {e}"
                    )

            return True

        return False

    except KeyError as ke:
        # Log an error if a KeyError occurs while checking for a close game
        logging.error(f"KeyError occurred while checking for a close game: {ke}")
        return False
