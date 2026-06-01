import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score
from google.cloud import bigquery
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── 1. Load data from BigQuery ──────────────────────────────────────────────
print("Loading data from BigQuery...")
client = bigquery.Client(project="f1-pipeline-497820")

query = """
    SELECT
        Driver, Race, Year, Round, Compound,
        TyreLife, Stint, LapNumber,
        LapTimeSeconds
    FROM `f1-pipeline-497820.f1_raw.laps`
    WHERE LapTimeSeconds IS NOT NULL
      AND LapTimeSeconds BETWEEN 60 AND 180
      AND Compound IN ('SOFT','MEDIUM','HARD','INTERMEDIATE','WET')
"""

df = client.query(query).to_dataframe()
print(f"Loaded {len(df)} laps")

# ── 2. Feature engineering ──────────────────────────────────────────────────
print("Engineering features...")

# Encode categorical columns as numbers
le_driver   = LabelEncoder()
le_compound = LabelEncoder()
le_race     = LabelEncoder()

df["Driver_enc"]   = le_driver.fit_transform(df["Driver"])
df["Compound_enc"] = le_compound.fit_transform(df["Compound"])
df["Race_enc"]     = le_race.fit_transform(df["Race"])
df["Year_enc"]     = df["Year"] - 2024  # 2024=0, 2025=1, 2026=2
# Features we'll use to predict lap time
features = [
    "Driver_enc",
    "Compound_enc",
    "Race_enc",
    "Year_enc",
    "TyreLife",
    "Stint",
    "LapNumber"
]

X = df[features].fillna(0)
y = df["LapTimeSeconds"]

# ── 3. Train/test split ─────────────────────────────────────────────────────
print("Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"Training rows: {len(X_train)} | Test rows: {len(X_test)}")

# ── 4. Train the model ──────────────────────────────────────────────────────
print("Training Random Forest model...")
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)
print("Training complete!")

# ── 5. Evaluate the model ───────────────────────────────────────────────────
print("Evaluating model...")
y_pred = model.predict(X_test)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)

print(f"\n── Model Results ──────────────────")
print(f"RMSE : {rmse:.3f} seconds")
print(f"R²   : {r2:.3f}")
print(f"───────────────────────────────────")
print(f"On average the model predicts lap")
print(f"times within {rmse:.1f} seconds")

# ── 6. Feature importance ───────────────────────────────────────────────────
importance = pd.DataFrame({
    "Feature"   : features,
    "Importance": model.feature_importances_
}).sort_values("Importance", ascending=False)

print(f"\n── Feature Importance ─────────────")
print(importance.to_string(index=False))

# ── 7. Save predictions to BigQuery ────────────────────────────────────────
print("\nSaving predictions to BigQuery...")
results = X_test.copy()
results["ActualLapTime"]    = y_test.values
results["PredictedLapTime"] = y_pred
results["Error"]            = abs(results["ActualLapTime"] - results["PredictedLapTime"])

# Decode back to original labels
results["Driver"]   = le_driver.inverse_transform(results["Driver_enc"])
results["Compound"] = le_compound.inverse_transform(results["Compound_enc"])
results["Race"]     = le_race.inverse_transform(results["Race_enc"])
results["Year"] = df.loc[X_test.index, "Year_enc"].values

# Keep only readable columns
output = results[[
    "Driver","Race","Year","Compound",
    "TyreLife","LapNumber",
    "ActualLapTime","PredictedLapTime","Error"
]].round(3)

job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
client.load_table_from_dataframe(
    output,
    "f1-pipeline-497820.f1_transformed.lap_time_predictions",
    job_config=job_config
).result()

print(f"Saved {len(output)} predictions to BigQuery!")
print("\nDone! Check f1_transformed.lap_time_predictions in BigQuery.")