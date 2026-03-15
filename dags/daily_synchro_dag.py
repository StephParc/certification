# daily_synchro_dag.py
"""
DAG for Cross-Database Synchronization (MongoDB to PostgreSQL).

This pipeline ensures data consistency between the NoSQL storage (MongoDB) 
and the relational database (PostgreSQL). It synchronizes UUIDs and 
creates necessary SQL records for instruments, musicians (users), 
and sheet music (partitions) to maintain system-wide referential integrity.
"""
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
    description='UUID and record synchronization between MongoDB and PostgreSQL',
    schedule_interval=None,
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['production', 'E4', 'sync'],
) as dag:

    docker_exec = "docker exec -t fastapi_hbm python3 -m E4.harmonie.BDD.sync_sql_mongo"

    # Task 1: Instrument Synchronization
    task_sync_inst = BashOperator(
        task_id='sync_instruments',
        bash_command=f"{docker_exec} sync_instruments"
    )

    # Task 2: Musician Synchronization
    # Handles SQL user account creation based on MongoDB musician profiles
    task_sync_users = BashOperator(
        task_id='sync_musicians',
        bash_command=f"{docker_exec} sync_musiciens"
    )

    # Task 2: Musician Synchronization
    # Handles SQL user account creation based on MongoDB musician profiles
    task_sync_parts = BashOperator(
        task_id='sync_partitions_mongo',
        bash_command=f"{docker_exec} sync_partitions"
    )

    task_sync_inst >> task_sync_users >> task_sync_parts