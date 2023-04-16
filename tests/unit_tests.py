import json

from dateutil import tz

from src.sports_line_scrape import get_odds, get_game_data


def test_get_odds():
    with open("tests/source/moneyline_resp.html", "r") as html:
        odds = get_odds(html.read())
        print(json.dumps(odds[0], indent=2))
        # print(odds[0]["sportsBookOdds"].keys())
        print(json.dumps(get_game_data(odds[0], tz.tzlocal(), "")))

if __name__=="__main__":
    test_get_odds()