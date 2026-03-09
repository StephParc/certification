# daily_musicshop_update_dag.py
"""
DAG for Daily Web Scraping and Database Synchronization.

This pipeline automates the extraction of instrument data from external 
sources using Scrapy. The process follows a classic ETL pattern:
1. Extract: Scrapy crawl and direct export to S3 (Raw Zone).
2. Transform: Cleaning and filtering of new items.
3. Load: Bulk insertion of new records into the PostgreSQL database.
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
    'daily_scrapy_update_v1',
    default_args=default_args,
    description='Daily MusicShop scraping, cleaning, and SQL update',
    schedule_interval=None,
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['production', 'E4'],
) as dag:

    docker_exec = "docker exec -t fastapi_hbm"

    # Task 1: Scrapy Crawl (Direct S3 Export via Feed Export)
    task_crawl = BashOperator(
        task_id='run_scrapy_crawl',
        bash_command=f"{docker_exec} /bin/bash -c 'cd E4/harmonie && scrapy crawl hbm_scrap -O s3://zone-brutes/E4/musicshop_last.csv'"
    )

    # Task 2: Data Cleaning and New Record Filtering
    task_clean = BashOperator(
        task_id='clean_and_filter_new',
        bash_command=f"{docker_exec} python3 -m E4.harmonie.harmonie.clean_scrapy"
    )

    # Task 3: SQL Ingestion
    # Imports the cleaned CSV from the S3 Trusted zone into PostgreSQL
    task_import_db = BashOperator(
        task_id='import_new_to_sql',
        bash_command=f"{docker_exec} python3 -m E4.harmonie.BDD.create_db import_scrapy --file s3://zone-propres/E4/musicshop_new.csv"
    )

    task_crawl >> task_clean >> task_import_db