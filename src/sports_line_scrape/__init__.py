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
    "NHL": "nhl",
    "CBB": "cbb",
}

JSON_REGEX = '<script id="__NEXT_DATA__" type="application/json">(.*)</script>'
BASE_URL = "https://www.sportsline.com"


def extract_json(json_string: str) -> json:
    return json.loads(json_string)["props"]["initialState"]["oddsPageState"]["pageState"]["data"][
        "competitionOdds"
    ]


def safe_cast(value: str, to_type: type, default=None):
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default


def scrape_games(sport: str = "NFL", current_line: bool = True, time_zone: str = None):
    _line = "current" if current_line else "opening"

    odds_url = f"{BASE_URL}/{SPORT_DICT[sport]}/odds/picks-against-the-spread/"

    r = requests.get(odds_url)
    j = re.findall(JSON_REGEX, r.text)

    if len(j) > 0:
        odds = extract_json(j[0])

    local_tz = pytz.timezone(time_zone) if time_zone else tz.tzlocal()

    game_odds = []
    for event in odds:
        game = {}
        game["date"] = (
            datetime.strptime(event["scheduledTime"], "%Y-%m-%dT%H:%M:%SZ")
            .replace(tzinfo=pytz.UTC)
            .astimezone(local_tz)
            .date()
            .strftime(format="%Y-%m-%d")
        )
        game["datetime"] = (
            datetime.strptime(event["scheduledTime"], "%Y-%m-%dT%H:%M:%SZ")
            .replace(tzinfo=pytz.UTC)
            .astimezone(local_tz)
            .strftime(format="%Y-%m-%dT%H:%M:%SZ")
        )
        game["home_team"] = event["homeTeam"]["location"] + " " + event["homeTeam"]["nickName"]
        game["home_team_loc"] = event["homeTeam"]["location"]
        game["home_team_name"] = event["homeTeam"]["nickName"]
        game["home_team_abrv"] = event["homeTeam"]["abbr"]
        game["away_team"] = event["awayTeam"]["location"] + " " + event["awayTeam"]["nickName"]
        game["away_team_loc"] = event["awayTeam"]["location"]
        game["away_team_name"] = event["awayTeam"]["nickName"]
        game["away_team_abrv"] = event["awayTeam"]["abbr"]
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
                game["home_spread"][line["sportsbookName"]] = safe_cast(
                    line["odd"]["pointSpread"][f"{_line}HomeHandicap"], float
                )
                game["home_spread_odds"][line["sportsbookName"]] = safe_cast(
                    line["odd"]["pointSpread"][f"{_line}HomeOdds"], int
                )
                game["away_spread"][line["sportsbookName"]] = safe_cast(
                    line["odd"]["pointSpread"][f"{_line}AwayHandicap"], float
                )
                game["away_spread_odds"][line["sportsbookName"]] = safe_cast(
                    line["odd"]["pointSpread"][f"{_line}AwayOdds"], int
                )
                game["under_odds"][line["sportsbookName"]] = safe_cast(
                    line["odd"]["overUnder"][f"{_line}UnderOdd"], int
                )
                game["over_odds"][line["sportsbookName"]] = safe_cast(
                    line["odd"]["overUnder"][f"{_line}OverOdd"], int
                )
                game["total"][line["sportsbookName"]] = safe_cast(
                    line["odd"]["overUnder"][f"{_line}Total"], float
                )
                game["home_ml"][line["sportsbookName"]] = safe_cast(
                    line["odd"]["moneyLine"][f"{_line}HomeOdds"], int
                )
                game["away_ml"][line["sportsbookName"]] = safe_cast(
                    line["odd"]["moneyLine"][f"{_line}AwayOdds"], int
                )
        game_odds.append(game)
    return game_odds


class OddsScraper:
    def __init__(self, sport: str = "NFL", current_line: bool = True, time_zone: str = None):
        try:
            self.odds = scrape_games(sport, current_line, time_zone)
        except Exception as e:
            print(f"An error occurred:\n{e}")
            return


def main(sport: str = "NFL", current_line: bool = True, time_zone: str = None):
    games = OddsScraper(sport=sport, current_line=current_line)
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
    parser.add_argument(
        "--time_zone",
        required=False,
        help="Pass the time zone you'd like the date to be converted to, otherwise will try to convert local time.",
    )
    args = parser.parse_args()
    main(args.sport, args.current_line, args.time_zone)
