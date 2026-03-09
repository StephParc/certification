# daily_musicshop_update_dag.py
"""
DAG for MusicShop Data Transformation (Silver to Gold).

This pipeline orchestrates dbt (data build tool) commands to transform 
data from the Silver layer to the Gold layer within the MusicShop 
data warehouse. It handles seeding static data, creating snapshots 
for customer history, and building the final analytical models 
(E6 competency).
"""
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'musicshop',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'musicshop_gold_transformation',
    default_args=default_args,
    description='dbt transformation pipeline (Silver -> Gold) for Musicshop',
    schedule_interval='0 8 * * *',
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['E6', 'BI', 'dbt', 'musicshop'],
) as dag:
   
    # Task to load static data (CSV seeds) into the database
    seed_task = BashOperator(
        task_id='dbt_seed',
        bash_command='cd /opt/airflow/harmonie_dbt && '
                 'dbt seed --target musicshop --profiles-dir .'
    )

    # Task to capture historical changes (SCD Type 2) in the customer table
    snapshot_task = BashOperator(
        task_id='dbt_snapshot_customers',
        bash_command='cd /opt/airflow/harmonie_dbt && '
                 'dbt snapshot --target musicshop --profiles-dir .' 
    )

    # Task to run and test the transformation models for the Gold analytical layer
    build_task = BashOperator(
        task_id='dbt_build_gold_layer',
        bash_command='cd /opt/airflow/harmonie_dbt && '
                 'dbt build --target musicshop --select musicshop --profiles-dir .'
    )

    seed_task >> snapshot_task >> build_task