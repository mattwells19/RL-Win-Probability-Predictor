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

def getMatchUrls():
    f = open("match_urls.txt", "a")

    for i in range(1, 268):
        events = get("/matches/?sort=&page={}&per_page=50".format(i))

        for match in events['data']:
            f.write(match['match_url'] + "\n")

    f.close()

def getSeriesInfo(match_url):

    series = get("/series/{}".format(match_url))

    # data is an array for some reason
    bestOf = series['data'][0]['best_of']
    winnerOfSeries = True if series['data'][0]['Result'] == series['data'][0]['Team1'] else False
    return {
        "best_of": bestOf,
        "winner": winnerOfSeries
    }

def getGameResults(match_url):
    game_results = []
    series_info = getSeriesInfo(match_url)
    blueWins = 0
    orangeWins = 0
    goalsDiff = 0
    
    for i in range(1, series_info['best_of']):
        try: # not all series go to the max game so we need to stop once we reach the end of the series
            match_data = get("/match_scoreboard_info/{}/{}".format(match_url, i))['data']
        except:
            return game_results[:len(game_results) - 1] # we don't care about the last game as it isn't helping us predict

        goalsDiff += (match_data['Team1Goals'] - match_data['Team2Goals'])

        if (match_data['Result'] == match_data["Team1"]):
            blueWins += 1
        else:
            orangeWins += 1

        game_results.append([goalsDiff, (blueWins - orangeWins) / series_info['best_of'], series_info['winner']])

    return game_results


def main():
    all_results = []
    f = open("match_urls.txt", "r")
    for url in tqdm(f):
        game_results = getGameResults(str(url).rstrip()) # make sure we strip off the endline character
        for game in game_results:
            all_results.append(game)

    f.close()
    df = pd.DataFrame(all_results, columns = ["goal_diff", "win_diff", "won_series"])
    df.to_csv("data.csv", index=False)


if __name__ == "__main__":
    main()