# simulate_musicshop_customers_dag.py
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
    description='Initialisation BDD et chargement des données sources',
    schedule_interval='@once',
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['setup', 'E6'],
) as dag:

    # Commande de base docker
    docker_exec = "docker exec -t fastapi_hbm"

    task_generate_file = BashOperator(
        task_id='generate_customers_csv',
        bash_command=f"{docker_exec} python3 -m E6.gen_customers"
    )

    task_upload_postgres = BashOperator(
        task_id='upload_to_postgres',
        bash_command=f"{docker_exec} python3 -m E6.ingest_customers_to_postgres"
    )

task_generate_file >> task_upload_postgres