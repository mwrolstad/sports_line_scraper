from datetime import datetime
from dateutil import tz

import argparse
import json
import re
import requests
import pytz

SPORT_DICT = {
    "NBA": "nba",
    "NFL": "nfl",
    "MLB": "mlb",
}

JSON_REGEX = '<script id="__NEXT_DATA__" type="application/json">(.*)</script>'
BASE_URL = "https://www.sportsline.com"


def extract_json(json_string: str) -> json:
    return json.loads(json_string)["props"]["initialState"]["oddsPageState"]["pageState"]["data"]["competitionOdds"]


def scrape_games(sport: str = "NFL", current_line: bool = True):
    _line = "current" if current_line else "opening"

    odds_url = f"{BASE_URL}/{SPORT_DICT[sport]}/odds/picks-against-the-spread/"

    r = requests.get(odds_url)
    j = re.findall(JSON_REGEX, r.text)

    if len(j) > 0:
        odds = extract_json(j[0])

    game_odds = []
    for event in odds:
        game = {}
        game["date"] = (
            datetime.strptime(event["scheduledTime"], "%Y-%m-%dT%H:%M:%SZ")
            .replace(tzinfo=pytz.UTC)
            .astimezone(tz.tzlocal())
            .date()
            .strftime(format="%Y-%m-%d")
        )
        game["datetime"] = (
            datetime.strptime(event["scheduledTime"], "%Y-%m-%dT%H:%M:%S")
            .replace(tzinfo=pytz.UTC)
            .astimezone(tz.tzlocal())
            .strftime(format="%Y-%m-%dT%H:%M:%SZ")
        )
        game["home_team"] = event["homeTeam"]["location"] + " " + event["homeTeam"]["nickName"]
        game["home_team_loc"] = event["homeTeam"]["location"]
        game["home_team_name"] = event["homeTeam"]["nickName"]
        game["home_team_abrv"] = event["homeTeam"]["abbr"]
        game["away_team"] = event["awayTeam"]["location"] + " " + event["awayTeam"]["nickName"]
        game["away_team_loc"] = event["awayTeam"]["location"]
        game["away_team_name"] = event["awayTeam"]["nickName"]
        game["away_team_abbr"] = event["awayTeam"]["abbr"]
        game["home_spread"] = {}
        game["home_spread_odds"] = {}
        game["away_spread"] = {}
        game["away_spread_odds"] = {}
        game["under_odds"] = {}
        game["over_odds"] = {}
        game["total"] = {}
        game["home_ml"] = {}
        game["away_ml"] = {}
        if "odds" in event:
            for line in event["odds"]:
                game["home_spread"][line["sportsbookName"]] = float(line["odd"]["pointSpread"][f"{_line}HomeHandicap"])
                game["home_spread_odds"][line["sportsbookName"]] = int(line["odd"]["pointSpread"][f"{_line}HomeOdds"])
                game["away_spread"][line["sportsbookName"]] = float(line["odd"]["pointSpread"][f"{_line}AwayHandicap"])
                game["away_spread_odds"][line["sportsbookName"]] = int(line["odd"]["pointSpread"][f"{_line}AwayOdds"])
                game["under_odds"][line["sportsbookName"]] = int(line["odd"]["overUnder"][f"{_line}UnderOdd"])
                game["over_odds"][line["sportsbookName"]] = int(line["odd"]["overUnder"][f"{_line}OverOdd"])
                game["total"][line["sportsbookName"]] = float(line["odd"]["overUnder"][f"{_line}Total"])
                game["home_ml"][line["sportsbookName"]] = int(line["odd"]["moneyLine"][f"{_line}HomeOdds"])
                game["away_ml"][line["sportsbookName"]] = int(line["odd"]["moneyLine"][f"{_line}AwayOdds"])
        game_odds.append(game)
    return game_odds


class Scoreboard:
    def __init__(self, sport: str = "NFL", current_line: bool = True):
        try:
            self.odds = scrape_games(sport, current_line)
        except Exception as e:
            print("An error occurred: {}".format(e))
            return


def main(sport: str = "NFL", current_line: bool = True):
    games = Scoreboard(sport=sport)
    print(json.dumps(games.odds, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Pass in a sports to get the current odds using --sport and --current_line."
    )
    parser.add_argument(
        "--sport",
        required=False,
        help="Pass in a sport to scrape, i.e. NFL, NBA, or MLB.",
    )
    parser.add_argument(
        "--current_line",
        required=False,
        help="Pass a value to indicate whether you want the opening line (`True`), or current line (`False`).",
    )
    args = parser.parse_args()
    main(args.sport, args.current_line)
