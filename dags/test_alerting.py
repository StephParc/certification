# test_alerting.py
"""
DAG to test the Discord alerting system.

This DAG intentionally triggers a failure to verify that the 
'on_failure_callback' correctly sends a rich notification to the 
dedicated Discord channel via Webhook.
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
from config.config import DISCORD_WEBHOOK_URL

def send_discord_alert(context):
    """
    Send a failure notification to Discord via Webhook.

    Args:
        context (dict): Airflow task context containing task_instance and log_url.
    """
    webhook_url = DISCORD_WEBHOOK_URL
    if not webhook_url:
        return 
    
    ti = context.get('task_instance')
    dag_id = ti.dag_id
    task_id = ti.task_id
    log_url = ti.log_url
    
    # Construction d'un message "riche" (Embed) pour Discord
    payload = {
        "content": "🚨 **ALERTE PIPELINE HARMONIE** 🚨",
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


def task_qui_echoue():
    """Dummy task designed to raise a ValueError for testing purposes."""
    raise ValueError("Oups ! Quelque chose a cassé dans le pipeline Harmonie.")

default_args = {
    'owner': 'steph',
    'depends_on_past': False,
    'email': ['alerte-data@harmonie-projet.fr'],
    'email_on_failure': True,
    'email_on_retry': False,
    'on_failure_callback': send_discord_alert,
    'retries': 0
}

with DAG(
    'dag_test_alerting',
    default_args=default_args,
    start_date=datetime(2026, 3, 6),
    schedule_interval=None,
    catchup=False
) as dag:

    test_task = PythonOperator(
        task_id='trigger_error',
        python_callable=task_qui_echoue
    )