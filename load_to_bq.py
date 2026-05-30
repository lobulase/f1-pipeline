from google.cloud import bigquery
import pandas as pd

client = bigquery.Client(project="f1-pipeline-497820")

def upload(parquet_path, table_id):
    df = pd.read_parquet(parquet_path)
    print(f"Uploading {len(df)} rows to {table_id}...")
    job = client.load_table_from_dataframe(df, table_id)
    job.result()
    print(f"Done! {table_id} is now in BigQuery.")

upload("data/raw/laps.parquet",      "f1-pipeline-497820.f1_raw.laps")
upload("data/raw/pit_stops.parquet", "f1-pipeline-497820.f1_raw.pit_stops")