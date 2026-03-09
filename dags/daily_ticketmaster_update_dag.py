# daily_ticketmaster_update_dag.py
"""
DAG for TicketMaster ETL Pipeline (API to dbt).

This pipeline orchestrates a complete data flow for TicketMaster events:
1. Extraction: Fetches data from the TicketMaster API and stores it in S3 (Raw).
2. Loading: Transfers data from S3 to the PostgreSQL 'raw' schema.
3. Transformation: Executes dbt models to clean and model data for analysis 
   in the Gold layer.
"""
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from E5.ticketmaster_harvester import run_daily_ingestion
from E5.load_to_db import load_ticketmaster_file_to_bd

default_args = {
    'owner': 'ticketmaster',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ticketmaster_etl_pipeline',
    default_args=default_args,
    description='Pipeline complet : API -> S3 -> Postgres -> dbt',
    schedule_interval='@daily',
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['E5', 'ticketmaster'],
) as dag:

    # 1. API Extraction to S3
    task_harvester = PythonOperator(
        task_id='api_to_s3',
        python_callable=run_daily_ingestion,
        op_kwargs={'country_code': 'US'}
    )

    # 2. S3 Load to Postgres Raw
    # Uses {{ ds }} which is the Airflow execution date (YYYY-MM-DD)
    task_loader = PythonOperator(
        task_id='s3_to_postgres',
        python_callable=load_ticketmaster_file_to_bd,
        op_kwargs={'folder_date': '{{ data_interval_end | ds }}'} 
    )

    # 3. dbt Transformation (Silver & Gold)
    task_dbt = BashOperator(
        task_id='dbt_transform',
        bash_command='cd /opt/airflow/harmonie_dbt && '
        'rm -rf dbt_packages target && '
        'dbt clean && dbt deps && '
        'dbt run --target ticketmaster --select ticketmaster --profiles-dir . && '
        'dbt test --target ticketmaster --select ticketmaster --profiles-dir .'
    )

    task_harvester >> task_loader >> task_dbt