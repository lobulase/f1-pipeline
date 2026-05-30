import fastf1
import pandas as pd
import os

os.makedirs("cache", exist_ok=True)
os.makedirs("data/raw", exist_ok=True)
fastf1.Cache.enable_cache("cache")

# All 24 rounds of the 2024 F1 season
races = [
    (1, "Bahrain"), (2, "Saudi Arabia"), (3, "Australia"),
    (4, "Japan"), (5, "China"), (6, "Miami"),
    (7, "Emilia Romagna"), (8, "Monaco"), (9, "Canada"),
    (10, "Spain"), (11, "Austria"), (12, "Britain"),
    (13, "Hungary"), (14, "Belgium"), (15, "Netherlands"),
    (16, "Italy"), (17, "Azerbaijan"), (18, "Singapore"),
    (19, "United States"), (20, "Mexico"), (21, "Brazil"),
    (22, "Las Vegas"), (23, "Qatar"), (24, "Abu Dhabi")
]

all_laps = []
all_pit_stops = []

for round_num, race_name in races:
    try:
        print(f"Fetching Round {round_num}: {race_name}...")
        session = fastf1.get_session(2024, round_num, "R")
        session.load()

        laps = session.laps[["Driver","LapNumber","LapTime",
                              "Compound","TyreLife","Stint",
                              "IsPersonalBest"]].copy()
        laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()
        laps["Race"] = race_name
        laps["Round"] = round_num
        laps.drop(columns=["LapTime"], inplace=True)
        all_laps.append(laps)

        pit_stops = session.laps[["Driver","LapNumber",
                           "PitInTime","PitOutTime"]].copy()
        pit_stops = pit_stops.dropna(subset=["PitInTime"])
        pit_stops["PitDurationSeconds"] = (
            pit_stops["PitOutTime"] - pit_stops["PitInTime"]
        ).dt.total_seconds()
        pit_stops["Race"] = race_name
        pit_stops["Round"] = round_num
        # Convert timedelta columns to seconds so BigQuery can handle them
        pit_stops["PitInTime"] = pit_stops["PitInTime"].dt.total_seconds()
        pit_stops["PitOutTime"] = pit_stops["PitOutTime"].dt.total_seconds()
        all_pit_stops.append(pit_stops)

        print(f"  Done — {len(laps)} laps, {len(pit_stops)} pit stops")

    except Exception as e:
        print(f"  Skipping {race_name}: {e}")

# Combine all races into single files
final_laps = pd.concat(all_laps, ignore_index=True)
final_pits = pd.concat(all_pit_stops, ignore_index=True)

final_laps.to_parquet("data/raw/laps.parquet", index=False)
final_pits.to_parquet("data/raw/pit_stops.parquet", index=False)

print(f"\nAll done!")
print(f"Total laps: {len(final_laps)}")
print(f"Total pit stops: {len(final_pits)}")