# setup_hbm_dag.py
"""
DAG for Initial Database Setup and Source Data Ingestion.

This DAG is designed to be executed once (@once) to initialize the 
relational (PostgreSQL) and NoSQL (MongoDB) database environments. 
It creates the SQL schema and populates the tables with initial 
CSV source data (users, instruments, events, and crawled items).
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'harmonie',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 0,
}

with DAG(
    'setup_hbm_database_v1',
    default_args=default_args,
    description='DB initialization and source data loading pipeline',
    schedule_interval='@once',
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['setup', 'E4'],
) as dag:

    # Target container: fastapi_hbm (App container with DB access)
    docker_base = "docker exec -t fastapi_hbm python3 -m E4.harmonie.BDD.create_db"

    # Task: Initialize PostgreSQL schema (Tables, Indexes, Constraints)
    task_init_sql = BashOperator(
        task_id='init_sql_schema',
        bash_command=f"{docker_base} init"
    )

    # Task: Import of User data from local CSV
    task_users_import = BashOperator(
        task_id='import_sql_users_data',
        bash_command=f"{docker_base} import_users --file E4/harmonie/sources/users.csv"
    )

    # Task: import of Instrument data from local CSVL
    task_instruments_sql_import = BashOperator(
        task_id='import_sql_instruments_data',
        bash_command=f"{docker_base} import_instruments --file E4/harmonie/sources/instruments.csv"
    )

    # Task: Bulk import of Event data from local CSV
    task_events_import = BashOperator(
        task_id='import_sql_events_data',
        bash_command=f"{docker_base} import_events --file E4/harmonie/sources/events.csv"
    )

    # Task: Bulk import of Scraped data from base test file
    task_scrapy_import = BashOperator(
        task_id='import_sql_scrapy_data',
        bash_command=f"{docker_base} import_scrapy --file E4/harmonie/sources/fichier_base_test.csv"
    )

    # Task: MongoDB initialization with base JSON collections
    task_init_mongo = BashOperator(
        task_id='init_mongo_json_data',
        bash_command='cd /opt/airflow && export PYTHONPATH=$PYTHONPATH:. && python3 -m utils.init_mongo'
    )

    # Dependencies: Create the schema first, then import data in parallel
    task_init_sql >> [task_users_import, task_events_import, task_instruments_sql_import, task_scrapy_import]

    # Mongo init can run independently
    task_init_mongo