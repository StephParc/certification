# daily_synchro_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'harmonie',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'sync_mongo_sql_v1',
    default_args=default_args,
    description='Synchronisation UUIDs entre MongoDB et PostgreSQL',
    schedule_interval=None, # Manuel par défaut, ou '@hourly'
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['production', 'E4', 'sync'],
) as dag:

    docker_exec = "docker exec -t fastapi_hbm python3 -m E4.harmonie.BDD.sync_sql_mongo"

    # Tâche 1 : Synchronisation des Instruments
    task_sync_inst = BashOperator(
        task_id='sync_instruments',
        bash_command=f"{docker_exec} sync_instruments"
    )

    # Tâche 2 : Synchronisation des Musiciens (Création comptes SQL)
    task_sync_users = BashOperator(
        task_id='sync_musicians',
        bash_command=f"{docker_exec} sync_musiciens"
    )

    # Tâche 3 : Synchronisation des Partitions (Liaison Inventaire)
    task_sync_parts = BashOperator(
        task_id='sync_partitions_mongo',
        bash_command=f"{docker_exec} sync_partitions"
    )

    # Les tâches peuvent tourner en parallèle ou en séquence
    task_sync_inst >> task_sync_users >> task_sync_parts