# F1 Data Engineering Pipeline

End-to-end data pipeline for Formula 1 race analytics.

## Tools Used
- FastF1 — data ingestion
- Python + pandas — data processing
- Google BigQuery — data warehouse
- dbt — data transformation
- Looker Studio — dashboard

## Pipeline Steps
1. Ingest F1 lap and pit stop data via FastF1
2. Save as Parquet files locally
3. Load into BigQuery
4. Transform with dbt
5. Visualise in Looker Studio

## Dashboard
https://datastudio.google.com/s/kB36AHIMmRM

## Results
- 26,604 laps ingested across 24 races and 20 drivers
- 849 pit stops recorded across the full season
- 5 tyre compounds used: Hard, Medium, Soft, Intermediate, Wet
- Fastest lap of the season: 92.61 seconds (RUS, Soft tyres)