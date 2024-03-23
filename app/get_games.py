from nba_api.live.nba.endpoints import scoreboard
import json

# Fetching today's scoreboard
games = scoreboard.ScoreBoard()

# Getting the JSON data
json_data = games.get_json()

# Writing the JSON data to a file
with open('scoreboard.json', 'w') as file:
    file.write(json_data)

print("Data written to scoreboard.json")

