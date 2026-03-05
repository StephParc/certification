# daily_musicshop_update_dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from E5.ticketmaster_harvester import run_daily_ingestion
from E5.load_to_db import load_ticketmaster_file_to_bd

# Configuration par défaut
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
    description='Pipeline de transformation dbt (Silver -> Gold) pour Musicshop',
    schedule_interval='0 8 * * *',
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['E6', 'BI', 'dbt', 'musicshop'],
) as dag:

    # dbt_command = "docker exec -w /opt/airflow/harmonie_dbt fastapi_hbm dbt"
    # dbt_flags = "--target musicshop --select musicshop --profile-dir ."
   
    seed_task = BashOperator(
        task_id='dbt_seed',
        bash_command='cd /opt/airflow/harmonie_dbt && '
                 'dbt seed --target musicshop --profiles-dir .'
    )

    snapshot_task = BashOperator(
        task_id='dbt_snapshot_customers',
        bash_command='cd /opt/airflow/harmonie_dbt && '
                 'dbt snapshot --target musicshop --profiles-dir .' 
    )

    build_task = BashOperator(
        task_id='dbt_build_gold_layer',
        bash_command='cd /opt/airflow/harmonie_dbt && '
                 'dbt build --target musicshop --select musicshop --profiles-dir .'
    )

    # task_dbt_musicshop = BashOperator(
    # task_id='dbt_musicshop_transform',
    # bash_command='cd /opt/airflow/harmonie_dbt && '
    #              'dbt seed --target musicshop --select musicshop --profiles-dir . && '
    #              'dbt snapshot --target musicshop --profiles-dir . && '
    #              'dbt build --target musicshop --select musicshop --profiles-dir .'
    # )

    seed_task >> snapshot_task >> build_task