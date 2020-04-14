import requests
import json
import pandas as pd
import os
from tqdm import tqdm

'''
    Helper function for get requests to the API
    API by Slokh: https://github.com/Slokh
'''
def get(url):
    request = requests.get("https://api.octane.gg/api{}".format(url))
    return json.loads(request.content)

def getSeriesInfo(match_url):

    series = get("/series/{}".format(match_url))

    # data is an array for some reason
    bestOf = series['data'][0]['best_of']
    winnerOfSeries = True if series['data'][0]['Result'] == series['data'][0]['Team1'] else False
    return {
        "best_of": bestOf,
        "winner": winnerOfSeries
    }

def getHead2Head(match_url):
    try:
        matchData = get("/match/{}".format(match_url))['data']
        blueTeam = matchData["Team1"]
        blueWins = 0
        orangeWins = 0
        head2headmatches = get("/head_to_head/{}".format(match_url))['data']
        for match in head2headmatches:
            if (match["Team1"] == blueTeam):
                blueWins += match["Team1Games"]
                orangeWins += match["Team2Games"]
            else:
                blueWins += match["Team2Games"]
                orangeWins += match["Team1Games"]
        return (blueWins - orangeWins) / (blueWins + orangeWins)
    except:
        return 0


def getData(match):
    match_url = match['match_url']
    seriesInfo = getSeriesInfo(match_url)
    best_of = seriesInfo["best_of"]
    did_blue_win = seriesInfo["winner"]
    head2head = getHead2Head(match_url)

    blueWins = 0
    orangeWins = 0
    blueGoals = 0
    orangeGoals = 0
    game_results = []

    for i in range(1, best_of):
        try: # not all series go to the max game so we need to stop once we reach the end of the series
            match_data = get("/match_scoreboard_info/{}/{}".format(match_url, i))['data']
        except:
            return game_results[:len(game_results) - 1] # we don't care about the last game as it isn't helping us predict

        blueGoals += match_data['Team1Goals']
        orangeGoals += match_data['Team2Goals']

        if (match_data['Result'] == match_data["Team1"]):
            blueWins += 1
        else:
            orangeWins += 1

        game_results.append([match_url, blueGoals, orangeGoals, blueWins, orangeWins, best_of, did_blue_win, head2head])

    return game_results



def main():
    all_results = []

    for i in tqdm(range(1, 200)):
        events = get("/matches/?sort=&page={}&per_page=10".format(i))

        for match in events['data']:
            series = getData(match)
            for game in series:
                all_results.append(game)

    df = pd.DataFrame(all_results, columns = ["match_url", "blue_goals", "orange_goals", "blue_wins", "orange_wins", "best_of", "did_blue_win", "head2head"])
    df.to_csv("rawData.csv", index=False)

if __name__ == "__main__":
    main()