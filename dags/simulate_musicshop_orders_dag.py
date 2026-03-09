# simulate_musicshop_orders_dag.py
"""
DAG for Daily MusicShop Order Simulation and Profile Mutation.

This workflow simulates a dynamic business environment by:
1. Generating synthetic daily orders.
2. Ingesting these orders into the PostgreSQL database.
3. Updating (mutating) customer profiles based on their purchase history.
It provides the necessary data volume for analytical dbt modeling.
"""
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
    description='Continuous generation and ingestion of orders and profile updates',
    # Runs every hour to simulate frequent business activity
    schedule_interval='* */1 * * *',
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['production', 'E6'],
) as dag:

    docker_exec = "docker exec -t fastapi_hbm"

    # Task 1: Generate synthetic orders for the current period
    task_generate_orders = BashOperator(
        task_id='generate_orders',
        bash_command=f"{docker_exec} python3 -m E6.gen_orders"
    )

    # Task 2: Bulk ingestion of orders into the relational database
    task_ingest_orders = BashOperator(
        task_id='ingest_orders_to_db',
        bash_command=f"{docker_exec} python3 -m E6.ingest_orders_to_postgres"
    )

    # Task 3: Update customer segments and profiles based on new activity
    task_mutate_profiles = BashOperator(
        task_id='mutate_profiles',
        bash_command=f"{docker_exec} python3 -m E6.update_customer_profiles"
    )

task_generate_orders >> task_ingest_orders >> task_mutate_profiles