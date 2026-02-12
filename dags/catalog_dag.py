# catalog_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# 1. Définition des arguments par défaut
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 2. Définition du DAG
with DAG(
    'dag_catalogue_v1',             # ID unique du DAG (ce que vous verrez dans l'UI)
    default_args=default_args,
    description='DAG pour mettre à jour le catalogue via harvester.py',
    schedule_interval=timedelta(days=1), # S'exécute une fois par jour
    start_date=datetime(2026, 2, 12),    # Date de début (historique)
    catchup=False,                      # Ne pas rattraper les exécutions passées
    tags=['production'],
) as dag:

    # 3. Définition de la tâche
    # Remplacer le chemin par le chemin réel de votre fichier
    run_harvester = BashOperator(
        task_id='executer_catalog_harvester',
        bash_command='cd /opt/airflow && export PYTHONPATH=$PYTHONPATH:. && python3 -m E7.harvester',
    )

    # 4. Dépendances (ici une seule tâche, donc simple)
    run_harvester