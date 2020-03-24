import requests
import json

seasons = ["four", "five", "six", "seven", "eight"]

for season in seasons:
    player_data_request = requests.get(
        "https://api.octane.gg/api/staging/stats/by-date/rlcs-season-{}-north-america".format(season))
    player_data = json.loads(player_data_request.content)

    for player in player_data['data']:
        print(player['Player'], player['Date'], player['Score'])
