"""
scheduler.py — automatically updates data and predictions every day at 6am.

You run this once: python scheduler/scheduler.py
It keeps running in the background, waking up every morning to refresh everything.
You don't have to manually run the fetcher anymore.
"""

import sys
import os

# We need to tell Python where to find our other modules (fetcher, predictor)
# sys.path is the list of directories Python searches when you do "import something"
# dirname(__file__) = folder of this file (scheduler/)
# dirname(dirname(...)) = one level up = the project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)   # add project root to Python's search path

from apscheduler.schedulers.blocking import BlockingScheduler
# BlockingScheduler = keeps the script running indefinitely, waiting to fire jobs
# (there's also BackgroundScheduler if you want it to run alongside other code)

from fetcher.fetcher import fetch_all
from predictor.predictor import run_simulation


def daily_update():
    """
    This function runs once per day automatically.
    It fetches fresh data then re-runs the prediction simulation.
    """
    print("Starting daily update...")
    fetch_all()          # download latest standings, matches, scorers
    run_simulation()     # recalculate championship probabilities with new data
    print("Daily update complete!")


# Create the scheduler object
scheduler = BlockingScheduler()

# Register the daily_update function as a scheduled job
# cron trigger: fires at 6:00 AM every day
# 'cron' is a Unix scheduling format — 'hour=6' means "at 6am"
scheduler.add_job(daily_update, trigger="cron", hour=6, minute=0)

print("Scheduler running. Will auto-update every day at 6:00 AM.")
print("Press Ctrl+C to stop.")

# start() blocks here — the script sits and waits until 6am, runs the job, waits again
scheduler.start()
