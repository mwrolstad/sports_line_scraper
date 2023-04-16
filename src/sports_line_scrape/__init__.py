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


def get_odds(html: str) -> json:
    j = re.findall(JSON_REGEX, html)

    return extract_json(j[0]) if len(j) > 0 else []


def get_game_data(event: dict, local_tz: str, _line: str) -> dict:
    game = {}
    try:
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
        if "sportsBookOdds" in event:
            sportsbook_odds = event["sportsBookOdds"]
            for sportsbook in sportsbook_odds.keys():
                line = sportsbook_odds[sportsbook]
                game["home_spread"][sportsbook] = safe_cast(
                    line["spread"]["home"][f"{_line}{'value' if len(_line) == 0 else 'Value'}"], float, default=1
                )
                game["home_spread_odds"][sportsbook] = safe_cast(
                    line["spread"]["home"][f"{_line}{'outcomeOdds' if len(_line) == 0 else 'OutcomeOdds'}"], int, default=100
                )
                game["away_spread"][sportsbook] = safe_cast(
                    line["spread"]["away"][f"{_line}{'value' if len(_line) == 0 else 'Value'}"], float, default=1
                )
                game["away_spread_odds"][sportsbook] = safe_cast(
                    line["spread"]["away"][f"{_line}{'outcomeOdds' if len(_line) == 0 else 'OutcomeOdds'}"], int, default=100
                )
                game["under_odds"][sportsbook] = safe_cast(
                    line["total"]["under"][f"{_line}{'outcomeOdds' if len(_line) == 0 else 'OutcomeOdds'}"], int, default=100
                )
                game["over_odds"][sportsbook] = safe_cast(
                    line["total"]["over"][f"{_line}{'outcomeOdds' if len(_line) == 0 else 'OutcomeOdds'}"], int, default=100
                )
                game["total"][sportsbook] = safe_cast(
                    line["total"]["over"][f"{_line}{'value' if len(_line) == 0 else 'Value'}"], float
                )
                game["home_ml"][sportsbook] = safe_cast(
                    line["moneyline"]["home"][f"{_line}{'outcomeOdds' if len(_line) == 0 else 'OutcomeOdds'}"], int, default=100
                )
                game["away_ml"][sportsbook] = safe_cast(
                    line["moneyline"]["away"][f"{_line}{'outcomeOdds' if len(_line) == 0 else 'OutcomeOdds'}"], int, default=100
                )
    except Exception as e:
        print("Exception:", e)
    finally:
        return game


def scrape_games(sport: str = "NFL", current_line: bool = True, time_zone: str = None):
    _line = "" if current_line else "opening"

    odds_url = f"{BASE_URL}/{SPORT_DICT[sport]}/odds/picks-against-the-spread/"

    r = requests.get(odds_url)
    
    odds = get_odds(r.text)
    
    local_tz = pytz.timezone(time_zone) if time_zone else tz.tzlocal()

    game_odds = []
    for event in odds:
        game_odds.append(get_game_data(event, local_tz, _line))

    return game_odds


class OddsScraper:
    def __init__(self, sport: str = "NFL", current_line: bool = True, time_zone: str = None):
        try:
            self.odds = scrape_games(sport, current_line, time_zone)
        except Exception as e:
            print(f"An error occurred:\n{e}")
            return


def main(sport: str = "NFL", current_line: bool = True, time_zone: str = None):
    games = OddsScraper(sport=sport, current_line=current_line, time_zone=time_zone)
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
