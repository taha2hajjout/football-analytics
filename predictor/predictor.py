"""
predictor.py — estimates each team's probability of winning the Premier League.

How it works (Monte Carlo simulation):
1. We know current points for each team.
2. We get all remaining (unplayed) matches.
3. For each remaining match, we estimate who will win based on current form & points per game.
4. We simulate the rest of the season 10,000 times, using random outcomes weighted by those probabilities.
5. We count how many times each team finishes top — that becomes their win probability %.

Example: if Arsenal wins in 6,200 out of 10,000 simulations → 62% chance of winning the league.
"""

import os
import random                      # built-in Python module — generates random numbers
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client["football_analytics"]

SIMULATIONS = 10_000   # how many times we simulate the rest of the season
# more simulations = more accurate but slower. 10,000 is fast (~2 seconds) and accurate enough.
# the underscore in 10_000 is just a readability trick — Python ignores it, same as 10000


def get_team_strengths():
    """
    Reads standings from MongoDB and calculates a "strength score" for each team.

    The strength score combines:
    - Points per game (60% weight) — best overall indicator
    - Goal difference per game (20% weight) — shows dominance, not just results
    - Recent form score (20% weight) — last 5 games, more recent = more relevant

    Returns a dict like: {"Arsenal": 2.1, "Manchester City": 2.3, ...}
    """
    standings = list(db.standings.find({}, {"_id": 0}))
    # find({}) with no filter returns ALL documents
    # {"_id": 0} excludes MongoDB's internal ID field (we don't need it)
    # list() converts the MongoDB cursor (like a pointer) into a regular Python list

    strengths = {}   # empty dict, we'll fill it with {team_name: score}

    for row in standings:
        # row is a dict representing one team's row in the standings table
        team_name = row["team"]["name"]    # e.g. "Arsenal FC"
        played = row["playedGames"]        # number of games played so far
        points = row["points"]             # total points
        gd = row["goalDifference"]         # goals scored minus goals conceded

        # avoid dividing by zero if no games have been played yet
        if played == 0:
            ppg = 0.0          # points per game
            gdpg = 0.0         # goal difference per game
        else:
            ppg = points / played
            gdpg = gd / played

        # form is a string like "W,D,L,W,W" from the API (last 5 results)
        form_str = row.get("form") or ""
        # .get("form") returns None if the key doesn't exist (safer than row["form"])
        # "or ''" means: if it's None or empty, use an empty string instead

        form_results = [r for r in form_str.split(",") if r]
        # split(",") turns "W,D,L,W,W" into ["W", "D", "L", "W", "W"]
        # the "if r" part filters out any empty strings from trailing commas

        # convert results to points: W=3, D=1, L=0
        form_points = sum(3 if r == "W" else 1 if r == "D" else 0 for r in form_results)
        # this is a "generator expression" inside sum() — it loops and adds all values
        # e.g. ["W","D","L","W","W"] → 3+1+0+3+3 = 10

        form_games = max(len(form_results), 1)   # avoid dividing by zero
        form_avg = form_points / form_games       # form points per game (0 to 3 scale)

        # weighted combination of all three factors
        strengths[team_name] = (ppg * 0.6) + (gdpg * 0.2) + (form_avg * 0.2)
        # ponytail: simple weighted average, use ML model if accuracy becomes critical

    return strengths


def simulate_match(home_strength, away_strength):
    """
    Simulates a single match and returns the result.

    Returns: "H" (home win), "A" (away win), or "D" (draw)

    Home teams win ~46% of Premier League games historically, so we add a 0.3 bonus.
    """
    home_adj = home_strength + 0.3   # home advantage boost
    total = home_adj + away_strength

    if total == 0:
        # edge case: both teams have 0 strength (e.g. before any games played)
        return random.choice(["H", "D", "A"])

    # calculate raw win probabilities
    p_home = (home_adj / total) * 0.75     # scale down to leave room for draws
    p_away = (away_strength / total) * 0.75
    p_draw = 1.0 - p_home - p_away        # remainder goes to draws

    # random.random() returns a float between 0.0 and 1.0
    # we use it to "spin the wheel" based on our probabilities
    r = random.random()

    if r < p_home:
        return "H"
    elif r < p_home + p_draw:
        return "D"
    else:
        return "A"


def run_simulation():
    """
    Runs the full Monte Carlo simulation and saves results to MongoDB.

    Steps:
    1. Load team strengths from standings
    2. Load remaining (unplayed) matches
    3. Simulate the season SIMULATIONS times
    4. Count how often each team wins
    5. Convert to percentages and save
    """
    strengths = get_team_strengths()

    if not strengths:
        print("No standings data found. Run fetcher first.")
        return {}

    # get all matches not yet played
    # "$in" is a MongoDB query operator meaning "where status is in this list"
    remaining = list(db.matches.find(
        {"status": {"$in": ["SCHEDULED", "TIMED"]}},
        {"_id": 0, "homeTeam": 1, "awayTeam": 1}   # only fetch the fields we need
    ))
    # {"homeTeam": 1, "awayTeam": 1} means "return only these two fields"

    # get current points as our starting baseline for each simulation
    standings = list(db.standings.find({}, {"_id": 0, "team": 1, "points": 1}))
    current_points = {row["team"]["name"]: row["points"] for row in standings}
    # dict comprehension: builds a dict from a loop in one line
    # result: {"Arsenal FC": 45, "Manchester City": 42, ...}

    teams = list(current_points.keys())  # list of all team names

    # initialise championship counter: every team starts at 0 wins
    championship_counts = {team: 0 for team in teams}

    print(f"Simulating {SIMULATIONS:,} seasons with {len(remaining)} matches remaining...")

    for _ in range(SIMULATIONS):
        # _ is a convention for "I don't need this loop variable"
        # we just need to repeat the block SIMULATIONS times

        # copy current points so we can add to them without changing the original
        # .copy() is important — without it, all simulations would share the same dict
        sim_points = current_points.copy()

        for match in remaining:
            home = match["homeTeam"]["name"]
            away = match["awayTeam"]["name"]

            # skip if we don't have strength data for these teams (edge case)
            if home not in strengths or away not in strengths:
                continue

            result = simulate_match(strengths[home], strengths[away])

            if result == "H":
                sim_points[home] = sim_points.get(home, 0) + 3
            elif result == "A":
                sim_points[away] = sim_points.get(away, 0) + 3
            else:
                # draw: both teams get 1 point
                sim_points[home] = sim_points.get(home, 0) + 1
                sim_points[away] = sim_points.get(away, 0) + 1

        # find the team with the most points in this simulation
        # max() with key= lets us compare dicts by their values
        champion = max(sim_points, key=lambda team: sim_points[team])
        championship_counts[champion] += 1

    # convert raw counts to percentages
    # round(..., 1) keeps one decimal place: 62.3%
    results = {
        team: round(count / SIMULATIONS * 100, 1)
        for team, count in championship_counts.items()
    }

    # sort by probability, highest first
    results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

    # save to MongoDB — replace old prediction with new one
    db.predictions.drop()
    db.predictions.insert_one({"predictions": results})

    print("Prediction saved to MongoDB!")
    return results


if __name__ == "__main__":
    results = run_simulation()
    print("\n=== Championship Win Probabilities ===")
    for team, pct in results.items():
        if pct > 0:
            bar = "█" * int(pct / 2)   # visual bar: each block = 2%
            print(f"{team:<30} {pct:>5}%  {bar}")
