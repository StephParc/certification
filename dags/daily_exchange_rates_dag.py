# daily_exchange_rates_dag.py
"""
DAG for Daily Forex Exchange Rates Generation and Ingestion.

This workflow automates the daily generation of currency exchange rates 
and their subsequent ingestion into the PostgreSQL database. 
It supports financial reporting and currency conversion tasks within 
the MusicShop data warehouse.
"""
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'musicshop',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'daily_exchange_rates',
    default_args=default_args,
    description='Génération et ingestion quotidienne des taux de change (Forex)',
    schedule_interval='@daily',
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['finance', 'E6'],
) as dag:

    docker_exec = "docker exec -t fastapi_hbm"

    task_generate_rates = BashOperator(
        task_id='generate_daily_rates',
        bash_command=f"{docker_exec} python3 -m E6.gen_exchange_rates"
    )

    task_ingest_rates = BashOperator(
        task_id='ingest_daily_rates_to_db',
        bash_command=f"{docker_exec} python3 -m E6.ingest_rates_to_postgres"
    )

task_generate_rates >> task_ingest_rates