# musicshop_pipeline_dag.py
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
    'daily_orders_pipeline',
    default_args=default_args,
    description='Génération et ingestion des commandes',
    schedule_interval='*/60 * * * *',
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['production', 'E6'],
) as dag:

    # Commande de base docker
    docker_exec = "docker exec -t fastapi_hbm"

    task_generate_orders = BashOperator(
        task_id='generate_orders',
        bash_command=f"{docker_exec} python3 -m E6.gen_orders"
    )

    task_ingest_orders = BashOperator(
        task_id='ingest_orders_to_db',
        bash_command=f"{docker_exec} python3 -m E6.ingest_orders_to_postgres"
    )

    task_mutate_profiles = BashOperator(
        task_id='mutate_profiles',
        bash_command=f"{docker_exec} python3 -m E6.update_customer_profiles"
    )

task_generate_orders >> task_ingest_orders >> task_mutate_profiles