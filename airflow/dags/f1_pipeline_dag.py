from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os

# Path to your project
PROJECT_DIR = "/Users/prasannaobulasetti/f1-pipeline"
VENV_PYTHON = "/Users/prasannaobulasetti/f1-pipeline/venv/bin/python"
DBT_DIR     = "/Users/prasannaobulasetti/f1-pipeline/f1_dbt"

# Default settings for all tasks
default_args = {
    "owner"           : "prasanna",
    "retries"         : 1,
    "retry_delay"     : timedelta(minutes=5),
    "email_on_failure": False,
}

# Define the DAG
with DAG(
    dag_id="f1_pipeline",
    default_args=default_args,
    description="F1 data pipeline - ingest, load, transform, predict",
    schedule="0 6 * * 1",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["f1", "data-engineering"]
) as dag:

    # Task 1 - Ingest F1 data
    ingest = BashOperator(
        task_id="ingest_f1_data",
        bash_command=f"cd {PROJECT_DIR} && {VENV_PYTHON} ingest.py",
    )

    # Task 2 - Load to BigQuery
    load_bq = BashOperator(
        task_id="load_to_bigquery",
        bash_command=f"cd {PROJECT_DIR} && {VENV_PYTHON} load_to_bq.py",
    )

    # Task 3 - Run dbt transformations
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run",
    )

    # Task 4 - Run dbt tests
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test",
    )

    # Task 5 - Run ML predictions
    ml_predict = BashOperator(
        task_id="ml_predictions",
        bash_command=f"cd {PROJECT_DIR} && {VENV_PYTHON} predict_lap_times.py",
    )

    # Define the order — each task waits for the previous one to finish
    ingest >> load_bq >> dbt_run >> dbt_test >> ml_predict
