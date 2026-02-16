# daily_musicshop_update_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'daily_scrapy_update_v1',
    default_args=default_args,
    description='Scraping quotidien MusicShop, nettoyage et mise à jour BDD',
    schedule_interval='@daily',
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['production', 'E4'],
) as dag:

    # Commande de base docker
    docker_exec = "docker exec -t fastapi_hbm"

    # Tâche 1 : Scraping (Export direct S3 via Scrapy Feed)
    task_crawl = BashOperator(
        task_id='run_scrapy_crawl',
        bash_command=f"{docker_exec} /bin/bash -c 'cd E4/harmonie && scrapy crawl hbm_scrap -O s3://zone-brutes/E4/musicshop_last.csv'"
    )

    # Tâche 2 : Nettoyage et identification des nouveautés
    task_clean = BashOperator(
        task_id='clean_and_filter_new',
        bash_command=f"{docker_exec} python3 -m E4.harmonie.harmonie.clean_scrapy"
    )

    # Tâche 3 : Insertion des nouveautés en BDD via create_db.py
    # handle_path téléchargera automatiquement l'URI s3:// dans /tmp
    task_import_db = BashOperator(
        task_id='import_new_to_sql',
        bash_command=f"{docker_exec} python3 -m E4.harmonie.BDD.create_db import_scrapy --file s3://zone-propres/E4/musicshop_new.csv"
    )

    # Dépendances séquentielles
    task_crawl >> task_clean >> task_import_db