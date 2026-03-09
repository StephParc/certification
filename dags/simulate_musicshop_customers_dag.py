# simulate_musicshop_customers_dag.py
"""
DAG for MusicShop Customer Data Initialization.

This DAG performs a one-time setup (@once) to simulate a customer base 
for the MusicShop data warehouse. It generates a synthetic CSV dataset 
and ingests it into the PostgreSQL database (Silver layer) to support 
dbt transformation modeling.
"""
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'musicshop',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 0,
}

with DAG(
    'setup_musicshop_initialization',
    default_args=default_args,
    description='Initializes MusicShop customer data via generation and ingestion',
    schedule_interval='@once',
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['setup', 'E6'],
) as dag:


    docker_exec = "docker exec -t fastapi_hbm"

    # Task 1: Generate synthetic customer data in CSV format
    task_generate_file = BashOperator(
        task_id='generate_customers_csv',
        bash_command=f"{docker_exec} python3 -m E6.gen_customers"
    )

    # Task 2: Bulk ingestion of generated customers into PostgreSQL
    task_upload_postgres = BashOperator(
        task_id='upload_to_postgres',
        bash_command=f"{docker_exec} python3 -m E6.ingest_customers_to_postgres"
    )

task_generate_file >> task_upload_postgres