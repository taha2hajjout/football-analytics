import os
import time
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("FOOTBALL_API_TOKEN")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
BASE_URL  = "https://api.football-data.org/v4"
HEADERS   = {"X-Auth-Token": API_TOKEN}


def get_db():
    """Create a fresh DB connection — called inside each function, not at import time."""
    client = MongoClient(MONGO_URI)
    return client["football_analytics"]


def find_season():
    """
    Ask the API which season is currently active for the Premier League.
    Returns the season start year as an integer (e.g. 2025 for the 2025/26 season).
    Falls back to probing recent years if the competition endpoint fails.
    """
    r = requests.get(f"{BASE_URL}/competitions/PL", headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        start_date = data.get("currentSeason", {}).get("startDate", "")
        if start_date:
            return int(start_date[:4])  # "2025-08-16" → 2025

    # fallback: probe the last 3 years and use whichever has standings
    from datetime import date
    today = date.today()
    start = today.year if today.month >= 8 else today.year - 1
    for year in [start, start - 1, start - 2]:
        probe = requests.get(
            f"{BASE_URL}/competitions/PL/standings?season={year}", headers=HEADERS
        )
        if probe.status_code == 200:
            return year
        time.sleep(3)

    raise RuntimeError(
        "Could not determine a valid season from football-data.org. "
        "Check your API token or try again later."
    )


def fetch_standings(db, season):
    response = requests.get(
        f"{BASE_URL}/competitions/PL/standings?season={season}", headers=HEADERS
    )
    response.raise_for_status()
    standings = response.json()["standings"][0]["table"]
    db.standings.drop()
    db.standings.insert_many(standings)
    print(f"Saved {len(standings)} team standings")


def fetch_matches(db, season):
    response = requests.get(
        f"{BASE_URL}/competitions/PL/matches?season={season}", headers=HEADERS
    )
    response.raise_for_status()
    matches = response.json()["matches"]
    db.matches.drop()
    db.matches.insert_many(matches)
    print(f"Saved {len(matches)} matches")


def fetch_scorers(db, season):
    response = requests.get(
        f"{BASE_URL}/competitions/PL/scorers?season={season}&limit=20", headers=HEADERS
    )
    response.raise_for_status()
    scorers = response.json()["scorers"]
    db.scorers.drop()
    db.scorers.insert_many(scorers)
    print(f"Saved {len(scorers)} top scorers")


def fetch_teams(db, season):
    response = requests.get(
        f"{BASE_URL}/competitions/PL/teams?season={season}", headers=HEADERS
    )
    response.raise_for_status()
    teams = response.json()["teams"]
    db.teams.drop()
    db.teams.insert_many(teams)
    print(f"Saved {len(teams)} teams with squads")


def fetch_all():
    """
    Downloads all Premier League data and saves to MongoDB.
    Auto-detects the current season, respects the free tier rate limit (10 req/min).
    Returns the season year used, so the app can display it.
    """
    db     = get_db()
    season = find_season()
    print(f"Using season {season}")

    print("Fetching standings...")
    fetch_standings(db, season)
    time.sleep(7)

    print("Fetching matches...")
    fetch_matches(db, season)
    time.sleep(7)

    print("Fetching top scorers...")
    fetch_scorers(db, season)
    time.sleep(7)

    print("Fetching teams & squads...")
    fetch_teams(db, season)

    # store the season so the app can read it
    db.meta.drop()
    db.meta.insert_one({"season": season})

    print("All data saved!")
    return season


if __name__ == "__main__":
    fetch_all()
