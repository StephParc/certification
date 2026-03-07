# sauvegarde_bases_dag.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import requests
from config.config import DISCORD_WEBHOOK_URL, DBUSER_RW, DBNAME, MONGO_USER, MONGO_PASSWORD, MONGO_DBNAME
from utils.S3_utils import upload_file

def send_discord_alert(context):
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
    directory = "/opt/airflow/backups/"
    files = [f for f in os.listdir(directory) if f.startswith(prefix)]

    # L'ordre alphabétique correspond ici à l'ordre chronologique
    files.sort()
    
    # 3. Identifier les fichiers à supprimer (tous sauf les 'limit' derniers)
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
    description='Sauvegarde automatique de PostgreSQL et MongoDB',
    schedule_interval='@daily',
    catchup=False
) as dag:

    pg_filename = "postgres_{}_{}.sql".format(DBNAME, "{{ ts_nodash }}")
    pg_local_path = f"/opt/airflow/backups/{pg_filename}"

    # Sauvegarde PostgreSQL locale
    task_backup_postgres_local = BashOperator(
        task_id='backup_postgresql_local',
        bash_command=f"docker exec postgres_db pg_dump -U {DBUSER_RW} {DBNAME} --clean --create > {pg_local_path}"
    )

    # Sauvegarde PostgreSQL s3
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

    mongo_filename = "mongo_{}.gz".format("{{ ts_nodash }}")
    mongo_local_path = f"/opt/airflow/backups/{mongo_filename}"

    # Sauvegarde MongoDB locale
    task_backup_mongodb_local = BashOperator(
        task_id='backup_mongodb_local',
        # bash_command=f"docker exec mongodb_db mongodump --archive > {mongo_local_path}"
        bash_command=f"docker exec mongodb_db mongodump --username { MONGO_USER } --password { MONGO_PASSWORD } --authenticationDatabase admin --db {MONGO_DBNAME} --archive > {mongo_local_path}"
    )

    # Sauvegarde MongoDB locale
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