import boto3
import os
from dotenv import load_dotenv
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logger_config import trace_action, setup_logger

# Initialisation du logger spécifique à ce script
logger = setup_logger("E7-DataLake")

# Chargement du .env qui est au-dessus (..)
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

# Configuration (toujours les mêmes)
access_key = os.getenv("ACCESS_KEY")
secret_key = os.getenv("SECRET_KEY")
minio_url = os.getenv("MINIO_URL")

@trace_action
def upload_to_minio(local_path, bucket_name):
    """Fonction décorée qui utilise les variables du .env"""
    
    # Connexion
    s3 = boto3.client(
        "s3",
        endpoint_url=minio_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )

    filename = os.path.basename(local_path)
    s3.upload_file(local_path, bucket_name, filename)
    logger.info(f"Fichier {filename} envoyé avec succès.")

if __name__ == "__main__":
    # Test avec un fichier CSV de ton E5
    path_csv = "../E5/infoconcert/infoconcert/2026-01-13-infoconcert.csv"
    upload_to_minio(path_csv, "test-manuel")

