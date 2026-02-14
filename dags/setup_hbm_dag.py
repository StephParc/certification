# setup_hbm_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 0,
}

with DAG(
    'setup_hbm_database_v1',
    default_args=default_args,
    description='Initialisation BDD et chargement des données sources',
    schedule_interval=None,
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['setup'],
) as dag:

    # Commande de base pour docker exec
    # -t : simule un terminal
    # fastapi_hbm : nom de ton conteneur App
    docker_base = "docker exec -t fastapi_hbm python3 -m E4.harmonie.BDD.create_db"

    # Création des tables SQL
    task_init_sql = BashOperator(
        task_id='init_sql_schema',
        bash_command=f"{docker_base} init"
    )

    # Insertion des données users PostgreSQL
    task_users_import = BashOperator(
        task_id='import_sql_users_data',
        bash_command=f"{docker_base} import_users --file E4/harmonie/sources/users.csv"
    )

    # Insertion des données instruments PostgreSQL
    task_instruments_sql_import = BashOperator(
        task_id='import_sql_instruments_data',
        bash_command=f"{docker_base} import_instruments --file E4/harmonie/sources/instruments.csv"
    )
    # Insertion des données events PostgreSQL
    task_events_import = BashOperator(
        task_id='import_sql_events_data',
        bash_command=f"{docker_base} import_events --file E4/harmonie/sources/events.csv"
    )

    # Insertion des données scrapées PostgreSQL
    task_scrapy_import = BashOperator(
        task_id='import_sql_scrapy_data',
        bash_command=f"{docker_base} import_scrapy --file E4/harmonie/sources/fichier_base_test.csv"
    )

    # Initialisation MongoDB avec collections de base (JSON)
    task_init_mongo = BashOperator(
        task_id='init_mongo_json_data',
        bash_command='cd /opt/airflow && export PYTHONPATH=$PYTHONPATH:. && python3 -m utils.init_mongo'
    )

    # Dépendances : Créer d'abord, importer ensuite
    task_init_sql >> [task_users_import, task_events_import, task_instruments_sql_import, task_scrapy_import]
    task_init_mongo