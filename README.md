# sports_line_scraper

An easy tool to scrape the current odds listed on sportsline.com

### Use as a command line:

```cmd
python3 src/sports_line_scrape/__init__py --sport "NFL" --current_line True
```

### Import and use as a package:

```python
from sports_line_scrape import OddsScraper
import json
odds_scraper = OddsScraper(sport="NBA", current_line=True)
print(json.dumps(odds_scraper.odds[0], indent=2))
{
  "date": "2023-02-01",
  "datetime": "2023-02-01T16:00:00Z",
  "home_team": "Philadelphia 76ers",
  "home_team_loc": "Philadelphia",
  "home_team_name": "76ers",
  "home_team_abrv": "PHI",
  "away_team": "Orlando Magic",
  "away_team_loc": "Orlando",
  "away_team_name": "Magic",
  "away_team_abrv": "ORL",
  "home_spread": {
    "consensus": -9.5,
    "whnj": -10.0,
    "draftkings": -9.0,
    "fanduel": -9.5,
    "bet365newjersey": -9.5
  },
  "home_spread_odds": {
    "consensus": -110,
    "whnj": -110,
    "draftkings": -110,
    "fanduel": -110,
    "bet365newjersey": -110
  },
  "away_spread": {
    "consensus": 9.5,
    "whnj": 10.0,
    "draftkings": 9.0,
    "fanduel": 9.5,
    "bet365newjersey": 9.5
  },
  "away_spread_odds": {
    "consensus": -110,
    "whnj": -110,
    "draftkings": -110,
    "fanduel": -110,
    "bet365newjersey": -110
  },
  "under_odds": {
    "consensus": -111,
    "whnj": -110,
    "draftkings": -110,
    "fanduel": -110,
    "bet365newjersey": -110
  },
  "over_odds": {
    "consensus": -110,
    "whnj": -110,
    "draftkings": -110,
    "fanduel": -110,
    "bet365newjersey": -110
  },
  "total": {
    "consensus": 230.5,
    "whnj": 230.5,
    "draftkings": 230.5,
    "fanduel": 231.0,
    "bet365newjersey": 230.5
  },
  "home_ml": {
    "consensus": -426,
    "whnj": -440,
    "draftkings": -410,
    "fanduel": -460,
    "bet365newjersey": -425
  },
  "away_ml": {
    "consensus": 332,
    "whnj": 335,
    "draftkings": 330,
    "fanduel": 360,
    "bet365newjersey": 325
  }
}
```
