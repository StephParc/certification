# sauvegarde_bases_dag.py
"""
DAG for Database Maintenance and Backups (PostgreSQL & MongoDB).

This workflow automates the daily backup of both relational (PostgreSQL) 
and NoSQL (MongoDB) databases. It performs local dumps, uploads them 
to the 'zone-maintenance' S3 bucket for long-term storage, and purges 
old local files. It also includes an automated alerting system via Discord.
"""
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import requests
from config.config import (DISCORD_WEBHOOK_URL, DBUSER_RW, DBNAME,
             MONGO_USER, MONGO_PASSWORD, MONGO_DBNAME)
from utils.S3_utils import upload_file

def send_discord_alert(context):
    """
    Send a failure notification to a Discord channel via Webhook.

    This function extracts task instance metadata (ID, log URL) from the 
    Airflow context to build a rich embed message for monitoring.

    Args:
        context (dict): The Airflow task context dictionary.

    Side Effects:
        - Performs a POST request to the Discord Webhook URL.
        - Prints an error message to the console if the request fails.
    """
    webhook_url = DISCORD_WEBHOOK_URL
    if not webhook_url:
        return 
    
    ti = context.get('task_instance')
    dag_id = ti.dag_id
    task_id = ti.task_id
    log_url = ti.log_url
    
    payload = {
        "content": " **ALERTE SAUVEGARDES BASES** ",
        "embeds": [{
            "title": f"Échec du DAG : {dag_id}",
            "color": 15158332, # Rouge
            "fields": [
                {"name": "Tâche", "value": task_id, "inline": True},
                {"name": "Lien Logs", "value": f"[Consulter l'erreur]({log_url})", "inline": False}
            ],
            "footer": {"text": "Airflow Notification System"}
        }]
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Erreur lors de l'envoi Discord : {e}")

def purge_old_backups(prefix, limit=2):
    """
    Clean up old local backup files to preserve disk space.

    It lists all files in the backup directory starting with a specific 
    prefix, sorts them alphabetically (chronologically), and deletes 
    all but the most recent ones.

    Args:
        prefix (str): The filename prefix (e.g., 'postgres_' or 'mongo_').
        limit (int, optional): The number of recent backups to keep. Defaults to 2.

    Side Effects:
        - Deletes files from the '/opt/airflow/backups/' directory.
    """
    directory = "/opt/airflow/backups/"
    files = [f for f in os.listdir(directory) if f.startswith(prefix)]

    # Alphabetical order corresponds to chronological order here
    files.sort()
    
    # Identify files to delete (all except the last 'limit' files)
    files_to_delete = files[:-limit]
    
    for f in files_to_delete:
        file_path = os.path.join(directory, f)
        try:
            os.remove(file_path)
            print(f"Archive locale supprimée : {f}")
        except Exception as e:
            print(f"Erreur lors de la suppression de {f} : {e}")

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2026, 3, 1),
    'email': ['alerte-data@harmonie-projet.fr'],
    'email_on_failure': True,
    'on_failure_callback': send_discord_alert,
    'retries': 1
}

with DAG(
    'maintenance_database_backups',
    default_args=default_args,
    description='Automated PostgreSQL and MongoDB backups',
    schedule_interval='@daily',
    catchup=False
) as dag:

    # --- PostgreSQL Pipeline ---
    pg_filename = "postgres_{}_{}.sql".format(DBNAME, "{{ ts_nodash }}")
    pg_local_path = f"/opt/airflow/backups/{pg_filename}"

    task_backup_postgres_local = BashOperator(
        task_id='backup_postgresql_local',
        bash_command=f"docker exec postgres_db pg_dump -U {DBUSER_RW} {DBNAME} --clean --create > {pg_local_path}"
    )

    task_backup_postgres_s3 = PythonOperator(
        task_id='backup_postgresql_s3',
        python_callable=upload_file,
        op_kwargs={
            'local_path': pg_local_path,
            'bucket': 'zone-maintenance',
            's3_path': f"postgres/{pg_filename}",
            'metadata': {
                'source': 'Base PostgreSQL',
                'dag': 'sauvegarde_bases_dag',
                'destination': 'zone-maintenance/postgres/'
            }
        }
    )

    task_purge_postgres = PythonOperator(
        task_id='purge_old_postgres_local',
        python_callable=purge_old_backups,
        op_kwargs={'prefix': 'postgres_', 'limit': 2}
    )

    # --- MongoDB Pipeline ---
    mongo_filename = "mongo_{}.gz".format("{{ ts_nodash }}")
    mongo_local_path = f"/opt/airflow/backups/{mongo_filename}"

    task_backup_mongodb_local = BashOperator(
        task_id='backup_mongodb_local',
        bash_command=f"docker exec mongodb_db mongodump --username { MONGO_USER } --password { MONGO_PASSWORD } --authenticationDatabase admin --db {MONGO_DBNAME} --archive > {mongo_local_path}"
    )

    task_backup_mongo_s3 = PythonOperator(
        task_id='backup_mongo_s3',
        python_callable=upload_file,
        op_kwargs={
            'local_path': mongo_local_path,
            'bucket': 'zone-maintenance',
            's3_path': f"mongo/{mongo_filename}",
            'metadata': {
                'source': 'Base MongoDB',
                'dag': 'sauvegarde_bases_dag',
                'destination': 'zone-maintenance/mongo/'
            }
        }
    )

    task_purge_mongodb = PythonOperator(
        task_id='purge_old_mongodb_local',
        python_callable=purge_old_backups,
        op_kwargs={'prefix': 'mongo_', 'limit': 2}
    )

    task_backup_postgres_local >> task_backup_postgres_s3 >> task_purge_postgres
    task_backup_mongodb_local >> task_backup_mongo_s3 >> task_purge_mongodb