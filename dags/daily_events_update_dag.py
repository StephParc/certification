# daily_events_update_dag.py
import os
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import ShortCircuitOperator, PythonOperator
from airflow.operators.bash import BashOperator

from utils.S3_utils import upload_bytes

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=BASE_DIR / ".env")

GIT_RAW_URL = os.getenv("GIT_RAW_URL")
GIT_API_URL = os.getenv("GIT_API_URL")
S3_ENDPOINT = os.getenv("DL_ENDPOINT")
BUCKET_NAME = "zone-brutes"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

# 2. LOGIQUE DES FONCTIONS
def check_for_changes():
    """Vérifie si le fichier sur Git a un nouveau SHA."""
    response = requests.get(GIT_API_URL)
    response.raise_for_status()
    
    latest_sha = response.json()[0]['sha']
    old_sha = Variable.get("last_events_git_sha", default_var=None)

    if old_sha is None:
        print("Variable inexistante. Initialisation...")
        Variable.set("last_events_git_sha", "first_run")
        old_sha = "first_run"
    
    if latest_sha != old_sha:
        # On stocke le nouveau SHA pour que le prochain run le connaisse
        return True 
    return False

def transfer_git_to_garage():
    git_url = GIT_RAW_URL
    res = requests.get(git_url)
    res.raise_for_status()
    
    success = upload_bytes(
        data=res.content,
        bucket=BUCKET_NAME,
        s3_path="E4/events_latest.csv",
        metadata={'source': 'github_events', 'sync_date': datetime.now().isoformat()}
    )
    if not success:
        raise Exception("Échec de l'upload vers Garage")

with DAG(
    'daily_events_update_v1', 
    schedule_interval='@daily',
    start_date=datetime(2026, 2, 12),
    catchup=False,
    tags=['production', 'E4'],
) as dag:
    check = ShortCircuitOperator(
        task_id='check_git', 
        python_callable=check_for_changes)

    task_transfer = PythonOperator(
        task_id='transfer_git_to_s3',
        python_callable=transfer_git_to_garage
    )

    task_import = BashOperator(
        task_id='import_to_db',
        bash_command=(
            f"docker exec -t fastapi_hbm python3 -m E4.harmonie.BDD.create_db "
            f"import_events --file s3://{BUCKET_NAME}/E4/events_latest.csv"
        )
    )

    check >> task_transfer >> task_import