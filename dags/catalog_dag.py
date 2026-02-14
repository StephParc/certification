# catalog_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Définition des arguments par défaut
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Définition du DAG
with DAG(
    'dag_catalogue_v1',
    default_args=default_args,
    description='DAG pour mettre à jour le catalogue via harvester.py',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['gouvernance'],
) as dag:

    # Définition de la tâche

    run_harvester = BashOperator(
        task_id='executer_catalog_harvester',
        bash_command='cd /opt/airflow && export PYTHONPATH=$PYTHONPATH:. && python3 -m E7.harvester',
    )

    # Dépendances
    run_harvester