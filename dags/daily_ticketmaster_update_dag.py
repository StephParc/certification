# daily_ticketmaster_update_dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from E5.ticketmaster_harvester import run_daily_ingestion
from E5.load_to_db import load_ticketmaster_file_to_bd

# Configuration par défaut
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

    # 1. Extraction API vers S3
    task_harvester = PythonOperator(
        task_id='api_to_s3',
        python_callable=run_daily_ingestion,
        op_kwargs={'country_code': 'US'}
    )

    # 2. Chargement S3 vers Postgres Raw
    # On utilise {{ ds }} qui est la date d'exécution d'Airflow (YYYY-MM-DD)
    task_loader = PythonOperator(
        task_id='s3_to_postgres',
        python_callable=load_ticketmaster_file_to_bd,
        op_kwargs={'folder_date': '{{ data_interval_end | ds }}'} 
    )

    # 3. Transformation dbt (Silver & Gold)
    # On lance dbt deps d'abord pour être sûr d'avoir les packages, puis run
    task_dbt = BashOperator(
        task_id='dbt_transform',
        bash_command='cd /opt/airflow/harmonie_dbt && '
        'rm -rf dbt_packages target && '
        'dbt clean && dbt deps && '
        'dbt run --target ticketmaster --select ticketmaster --profiles-dir . && '
        'dbt test --target ticketmaster --select ticketmaster --profiles-dir .'
    )

    # Ordonnancement des tâches
    task_harvester >> task_loader >> task_dbt