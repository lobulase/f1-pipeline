import fastf1
import pandas as pd
import os

# Create a cache folder so data is not re-downloaded every run
os.makedirs("cache", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)
fastf1.Cache.enable_cache("cache")

# Load the 2024 Bahrain Grand Prix Race session
session = fastf1.get_session(2024, "Bahrain", "R")
session.load()

# --- Lap data ---
laps = session.laps[["Driver","LapNumber","LapTime","Compound",
                       "TyreLife","Stint","IsPersonalBest"]]
laps = laps.copy()
laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()
laps.drop(columns=["LapTime"], inplace=True)
laps.to_parquet("data/raw/laps.parquet", index=False)
print(f"Saved {len(laps)} laps")

# --- Pit stop data ---
pit_stops = session.laps[["Driver","LapNumber","PitInTime","PitOutTime"]]
pit_stops = pit_stops.dropna(subset=["PitInTime"])
pit_stops = pit_stops.copy()
pit_stops["PitDurationSeconds"] = (
    pit_stops["PitOutTime"] - pit_stops["PitInTime"]
).dt.total_seconds()
pit_stops.to_parquet("data/raw/pit_stops.parquet", index=False)
print(f"Saved {len(pit_stops)} pit stops")