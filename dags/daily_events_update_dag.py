# daily_events_update_dag.py
"""
DAG for Daily Events Synchronization.

This DAG monitors a specific CSV file on GitHub. If changes are detected 
(via SHA comparison), it downloads the file and transfers it to the 
Garage Data Lake (S3). Finally, it triggers an internal API command 
to refresh the SQL database with the new data.
"""
from datetime import datetime
import requests
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import ShortCircuitOperator, PythonOperator
from airflow.operators.bash import BashOperator

from utils.S3_utils import upload_bytes
from config.config import GIT_RAW_URL, GIT_API_URL

BUCKET_NAME = "zone-brutes"

default_args = {
    'owner': 'harmoniew',
    'depends_on_past': False,
    'retries': 1,
}

def check_for_changes():
    """
    Check if the remote GitHub file has been updated by comparing SHAs.

    It fetches the latest commit metadata from the GitHub API and compares 
    the current SHA with the one stored in Airflow's Variables.

    Returns:
        bool: True if the file has changed or if no previous SHA exists 
              (forcing a sync), False otherwise.

    Side Effects:
        - Initializes the 'last_events_git_sha' Airflow Variable on the first run.
        - Updates the local workflow state based on remote repository changes.

    Notes:
        - Requires 'GIT_API_URL' environment variable to be set.
        - Uses the Airflow Metadata Database to persist the SHA.
    """
    response = requests.get(GIT_API_URL)
    response.raise_for_status()
    
    latest_sha = response.json()[0]['sha']
    old_sha = Variable.get("last_events_git_sha", default_var=None)

    if old_sha is None:
        print("Variable inexistante. Initialisation...")
        Variable.set("last_events_git_sha", "first_run")
        old_sha = "first_run"
    
    if latest_sha != old_sha:
        return True 
    return False

def transfer_git_to_garage():
    """
    Download the raw CSV from GitHub and upload it to the Garage Data Lake.

    The function acts as a bridge between the external source (GitHub) 
    and the internal raw zone (S3 Bucket). It attaches metadata to the 
    S3 object for traceability.

    Raises:
        Exception: If the 'upload_bytes' utility fails to persist the data 
                   into the S3 bucket.

    Side Effects:
        - Performs a GET request to GitHub Raw URL.
        - Writes data into the 'zone-brutes' S3 bucket at 'E4/events_latest.csv'.

    Notes:
        - Uses 'datetime.now()' to timestamp the 'sync_date' metadata.
    """
    git_url = GIT_RAW_URL
    res = requests.get(git_url)
    res.raise_for_status()
    
    success = upload_bytes(
        data=res.content,
        bucket=BUCKET_NAME,
        s3_path="E4/events_latest.csv",
        metadata={
            "source": "github_events", 
            "sync_date": datetime.now().isoformat(),
            "destination": "hbm.public.TB_evenement"}
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